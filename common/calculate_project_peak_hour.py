"""
This script calculates the project-level peak hours.
"""
import pandas as pd

from common.get_project_data import project_df


def project_peak_hours(project_id: int):
    """
        - Pull the project-level dataframe
        - Rename columns to avoid column name clashes
        - Add a project-wide total column
        - Split into AM and PM datasets
        - Find the AM & PM peak hours and volumes
    """

    # Get a list of all dataframes assigned to this project
    df_list = project_df(project_id, total_colname="total_hourly")

    # Add a number suffix so we don't have lots of columns
    # with the same names!
    counter = 0
    for raw_df in df_list:
        counter += 1

        raw_df.rename(columns={
            'total_hourly': f'total_hourly_{counter}',
            'location': f'location_{counter}'
        }, inplace=True)

    # Combine all dataframes into one
    df = pd.concat(df_list, axis=1)

    # Get a list of all columns we want to sum
    cols_to_sum = [col for col in df.columns if "total_hourly_" in col]

    # Sum the individual counts into a new 'total' column
    df["total"] = df[cols_to_sum].sum(axis=1)

    # Split the data into AM and PM series
    am = df[df.index < '12:00'].total
    pm = df[df.index >= '12:00'].total

    return {
        "am_vol": int(max(am)),
        "am_start": am.idxmax(),
        "pm_vol": int(max(pm)),
        "pm_start": pm.idxmax()
    }
