import pandas as pd
from datetime import time, timedelta, datetime
from sqlalchemy import create_engine

from sql_connection import SQLALCHEMY_DATABASE_URI
from common.flatten_tmc_headers import flatten_headers


class SQLUpload:
    """
    Efficiently extract data from Excel and import into SQL.

    """

    def __init__(self, src_file):

        self.src_file = src_file
        self.meta = self.extract_metadata()

    def extract_metadata(self):
        location_kwargs = {
            "sheet_name": "Information",
            "header": None,
            "usecols": "A:B",
            "names": ["place_type", "place_name"]
        }

        df_location = pd.read_excel(self.src_file, **location_kwargs).dropna()

        location_kwargs["usecols"] = "D:E"
        location_kwargs["names"] = ["time_type", "time_value"]

        df_time = pd.read_excel(self.src_file, **location_kwargs).dropna()

        data_date = None
        start_time = ""
        end_time = ""
        location_name = ""
        legs = {}

        # Get the location_name and leg names
        for _, row in df_location.iterrows():

            if row.place_type == "Intersection Name":
                location_name = row.place_name
            else:
                legs[row.place_type.lower()] = row.place_name

        # Get the date and start/end times
        for _, row in df_time.iterrows():

            if row.time_type == "Date":
                data_date = row.time_value
            elif row.time_type == "Start Time":
                start_time = row.time_value
            elif row.time_type == "End Time":
                end_time = row.time_value

        return {
            "title": location_name,
            "legs": legs,
            "data_date": data_date,
            "start_time": start_time,
            "end_time": end_time,
        }

    def read_data(self,
                  tabname: str,
                  col_prefix: str):
        """
        Minimalist approach to reading the XLS files.

        Parameters
        ----------
            - tabname: name of tab in the excel file
            - col_prefix: whatever you want to use at
                          the beginning of the column names.
        """

        df = pd.read_excel(self.src_file,
                           skiprows=3,
                           header=None,
                           names=flatten_headers(self.src_file, tabname),
                           sheet_name=tabname).dropna()

        # Check all time values and ensure that each one
        # is formatted as a datetime.time. Some aren't by default!
        for idx, row in df.iterrows():

            if type(row.time) != time:
                hour, minute = row.time.split(":")
                df.at[idx, "time"] = time(
                    hour=int(hour),
                    minute=int(minute)
                )

        # Reindex on the time column
        df.set_index("time", inplace=True)

        # Clean up column names for SQL
        #  Prefix all columns. i.e. "SB U" -> "Light SB U"
        new_cols = {}
        for col in df.columns:
            nice_prefix = col_prefix.lower()
            nice_col = col.replace(" ", "_").lower()

            # Special handling for bikes and peds
            # If it's one of these, set it as the mode
            for val in ["_bikes", "_peds"]:
                if val in nice_col:
                    nice_col = nice_col.replace(val, "")
                    nice_prefix = val[1:]

                    if len(nice_col.split("_")) == 1:
                        nice_col += "_xwalk"

            new_cols[col] = f"{nice_prefix}_{nice_col}"

        df.rename(
            columns=new_cols,
            inplace=True
        )

        df["datetime"] = None

        for idx, row in df.iterrows():
            df.at[idx, "datetime"] = datetime.combine(self.meta["data_date"], idx)

        # Set the dataframe index to the timestamp
        df.set_index("datetime", inplace=True)

        return df

    def spliced_light_and_heavy_df(self):

        df_light = self.read_data("Light Vehicles", "Light")
        df_heavy = self.read_data("Heavy Vehicles", "Heavy")

        df = pd.concat([df_light, df_heavy], axis=1, sort=False)

        # df["fid"] = int(self._fid)

        return df

    def add_totals_to_df(self, df):
        df["total_15_min"] = df.iloc[:, :].sum(axis=1)

        df["total_hourly"] = 0

        for idx, row in df.iterrows():
            start = idx
            end = start + timedelta(hours=1)

            hourly_total = df.loc[
                (df.index >= start) & (df.index < end),
                "total_15_min"
            ].sum()

            df.at[idx, "total_hourly"] = hourly_total

        return df

    def publish_df_to_sql(self,
                          df: pd.DataFrame,
                          pg_table_name: str = None,
                          db_uri: str = SQLALCHEMY_DATABASE_URI,
                          kwargs: dict = {"if_exists": "replace"}):

        engine = create_engine(db_uri)
        df.to_sql(pg_table_name, engine, **kwargs)
        engine.dispose()
