from flask import (
    Blueprint,
    redirect,
    url_for,
    flash,
    session
)
from flask_login import current_user, login_required
from datetime import datetime, time

#
from models import TMCFile
from db import db
from forms.upload_file_form import UploadFileForm
from common.extract_tmc_data import SQLUpload


# Blueprint for UPLOADING DATA
# ----------------------------
upload_bp = Blueprint(
    'upload_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@upload_bp.route('/upload-file', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = UploadFileForm()

    try:

        data = form.selected_file.data

        raw_tmc = SQLUpload(data)
        df = raw_tmc.spliced_light_and_heavy_df()

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
        data_date = raw_tmc.meta["data_date"]

        df_with_totals = raw_tmc.add_totals_to_df(df)

        noon = datetime.combine(data_date, time(hour=12))
        am_df = df_with_totals[(df_with_totals.index < noon)]
        am_start = am_df[["total_hourly"]].idxmax()[0]
        am_volume = am_df.at[am_start, "total_hourly"]

        pm_df = df_with_totals[(df_with_totals.index >= noon)]
        pm_start = pm_df[["total_hourly"]].idxmax()[0]
        pm_volume = pm_df.at[pm_start, "total_hourly"]

        tmc_entry = TMCFile(
            title=raw_tmc.meta["title"],
            filename=data.filename,
            uploaded_by=current_user.id,
            data_date=data_date,
            modes=modes,
            legs=legs,
            movements=movements,
            am_peak_start=am_start,
            pm_peak_start=pm_start,
            am_volume=float(am_volume),
            pm_volume=float(pm_volume),
            count_start_time=start,
            count_end_time=end,
        )
        db.session.add(tmc_entry)

        tbl_name = f"tmc_{tmc_entry.uid}"
        kwargs = {
            "if_exists": "replace",
            "schema": "tmc_data",
        }

        raw_tmc.publish_df_to_sql(df, tbl_name, kwargs=kwargs)

        db.session.commit()

        flash(f"Uploaded {raw_tmc.meta['title']}", "success")
        # flash(data, "info")
        # flash(f"This file includes data between {start} & {end}", "info")
        # flash(f"Vehicle Modes - {sorted(modes)}", "info")
        # flash(f"Intersection Legs - {sorted(legs)}", "info")
        # flash(f"Movements - {sorted(movements)}", "info")

        # flash(f"AM Peak - {am_start}", "info")
        # flash(f"PM Peak - {pm_start}", "info")

        session['validated'] = True

    except Exception as e:
        flash(str(e), "danger")
        session['validated'] = None

    return redirect(url_for('all_files_bp.all_files'))
