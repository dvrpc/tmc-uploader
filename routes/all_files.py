from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify
)
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import FileField

import pandas as pd
from datetime import time, timedelta, datetime
from sqlalchemy import create_engine

from sql_connection import SQLALCHEMY_DATABASE_URI
from models import TMCFile
# from db import db
from helpers import flatten_headers


def add_totals_to_df(df):
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


# UPLOAD CLASS
# ------------


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

    def spliced_light_and_heavy_df(self, data_date):

        df_light = self.read_data("Light Vehicles", "Light")
        df_heavy = self.read_data("Heavy Vehicles", "Heavy")

        df = pd.concat([df_light, df_heavy], axis=1, sort=False)

        # df["fid"] = int(self._fid)

        return df

    # def publish_to_database(self,
    #                         db_uri: str = SQLALCHEMY_DATABASE_URI,
    #                         df: pd.DataFrame = None,
    #                         pg_table_name: str = None,):

    #     if not df:
    #         df = self.spliced_light_and_heavy_df()
    #     if not pg_table_name:
    #         pg_table_name = f"data_p{self._pid}_f{self._fid}"

    #     engine = create_engine(db_uri)

    #     kwargs = {
    #         "if_exists": "replace",
    #     }

    #     df.to_sql(pg_table_name, engine, **kwargs)

    #     engine.dispose()

# FORMS
# -----


class UploadFilesForm(FlaskForm):
    selected_file = FileField()


# ROUTES
# ------


all_files_bp = Blueprint(
    'all_files_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@all_files_bp.route('/all/files', methods=['GET', 'POST'])
# @login_required
def all_files():
    """ Page that shows all files in the database """

    all_files = TMCFile.query.all()

    return render_template(
        'all_files.html',
        all_files=all_files,
        form=UploadFilesForm()
    )


@all_files_bp.route('/upload-file', methods=['GET', 'POST'])
# @login_required
def upload_file():
    form = UploadFilesForm()

    # try:

    data = form.selected_file.data

    tmc = SQLUpload(data)
    meta = tmc.extract_metadata()
    data_date = meta["data_date"]
    df = tmc.spliced_light_and_heavy_df(data_date)


    # Get list of all modes, legs, and movements

    modes, legs, movements = [], [], []
    column_list = [x.split("_") for x in df.columns]

    for this_mode, this_leg, this_mvmt in column_list:
        if this_mode not in modes:
            modes.append(this_mode)
        if this_leg not in legs:
            legs.append(this_leg)
        if this_mvmt not in movements:
            movements.append(this_mvmt)

    start = df.index.min()
    end = df.index.max()

    # Get the AM peak hour
    df_with_totals = add_totals_to_df(df)

    noon = datetime.combine(meta["data_date"], time(hour=12))
    am_df = df_with_totals[(df_with_totals.index < noon)]
    am_start = am_df[["total_hourly"]].idxmax()[0]

    pm_df = df_with_totals[(df_with_totals.index >= noon)]
    pm_start = pm_df[["total_hourly"]].idxmax()[0]


    # flash(data, "info")
    flash(f"This file includes data between {start} & {end}", "info")
    flash(f"Vehicle Modes - {sorted(modes)}", "info")
    flash(f"Intersection Legs - {sorted(legs)}", "info")
    flash(f"Movements - {sorted(movements)}", "info")

    flash(f"AM Peak - {am_start}", "info")
    flash(f"PM Peak - {pm_start}", "info")



    # except Exception as e:
    #     flash(str(e), "danger")

    return redirect(url_for('all_files_bp.all_files'))
