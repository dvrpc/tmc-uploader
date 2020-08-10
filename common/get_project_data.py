"""
Merge the already-uploaded data for all files assigned to a given project


"""
import pandas as pd
from sqlalchemy import create_engine


from models import Project
from sql_connection import SQLALCHEMY_DATABASE_URI


def project_df(project_id: int, uri: str = SQLALCHEMY_DATABASE_URI):

    this_project = Project.query.filter_by(uid=project_id).first()

    file_ids = [f.uid for f in this_project.tmc_files]

    all_dfs = []

    for fid in file_ids:

        q = f"""
            SELECT
                to_char(datetime, 'HH24:MI') as time_idx,
                CASE WHEN f.title IN (NULL, '') THEN f.filename ELSE f.title END AS location,
                total_15_min
            FROM tmc_data.tmc_{fid}
            LEFT JOIN filedata f on f.uid = {fid}
            """

        engine = create_engine(uri)
        df = pd.read_sql(q, uri, index_col="time_idx")
        engine.dispose()

        # Replace any None values with nan
        df.fillna(value=0, inplace=True)

        all_dfs.append(df)

    return all_dfs #pd.concat(all_dfs)
