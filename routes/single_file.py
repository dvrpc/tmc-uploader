import json
from flask import (
    Blueprint,
    render_template,
    flash,
    request,
    redirect,
    url_for
)
from flask_login import login_required

# Plotting
import plotly
import plotly.graph_objects as go
from sqlalchemy import create_engine
import pandas as pd


from db import db
from models import TMCFile, Project
from forms.file_metadata_form import UpdateMetadataForm
from forms.assign_files_to_project import AssignProjectsToFile
from sql_connection import SQLALCHEMY_DATABASE_URI


single_file_bp = Blueprint(
    'single_file_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@single_file_bp.route('/file/<file_id>', methods=['GET'])
@login_required
def single_file(file_id):
    """ Page that allows users to interact with a single TMC file """

    this_file = TMCFile.query.filter_by(uid=file_id).first()

    metadata_form = UpdateMetadataForm()
    project_form = AssignProjectsToFile()

    latlng_data = [this_file.lat, this_file.lng]

    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    df = pd.read_sql(f"SELECT * FROM tmc_data.tmc_{file_id};", engine, index_col="datetime")
    engine.dispose()

    data = []
    for col in df.columns:
        if "total_" not in col:
            data.append(go.Bar(x=df.index, y=df[col], name=col))

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    all_projects = Project.query.all()

    return render_template(
        'single_file.html',
        this_file=this_file,
        latlng_data=json.dumps(latlng_data),
        metadata_form=metadata_form,
        fig=graphJSON,
        all_projects=all_projects,
        project_form=project_form,
    )



@single_file_bp.route('/file/<file_id>/metadata-update', methods=['POST'])
@login_required
def file_update_metadata(file_id):
    """ Page that allows users to interact with a single TMC file """

    this_file = TMCFile.query.filter_by(uid=file_id).first()

    metadata_form = UpdateMetadataForm()

    this_file.title = str(metadata_form.title.data)
    if metadata_form.model_id.data:
        if type(metadata_form.model_id.data) == int:
            this_file.model_id = int(metadata_form.model_id.data)

    this_file.lat = str(metadata_form.lat.data)
    this_file.lng = str(metadata_form.lng.data)
    this_file.legs = str(metadata_form.legs.data)
    this_file.movements = str(metadata_form.movements.data)
    this_file.modes = str(metadata_form.modes.data)

    db.session.commit()

    flash(f"Successfully updated metadata", "success")

    return redirect(url_for("single_file_bp.single_file", file_id=file_id))

@single_file_bp.route('/file/<file_id>/project-update', methods=['POST'])
@login_required
def file_update_projects(file_id):
    """ Page that allows users to interact with a single TMC file """
    
    this_file = TMCFile.query.filter_by(uid=file_id).first()
    
    project_form = AssignProjectsToFile()

    if project_form.validate_on_submit():
        data = dict((key, request.form.getlist(key) if len(
            request.form.getlist(key)) > 1 else request.form.getlist(key)[0])
            for key in request.form.keys())

        pid_list = []
        for k in data:
            if "project_" in k:
                pid_list.append(int(k.replace("project_", "")))

        # Make sure all selected projects are associated
        for pid in pid_list:
            project = Project.query.filter_by(uid=pid).first()
            if project not in this_file.project_ids:
                this_file.project_ids.append(project)

        # Remove association with unchecked projects
        for project in this_file.project_ids:
            if project.uid not in pid_list:
                this_file.project_ids.remove(project)

        db.session.commit()

        flash("Updated project associations", "success")

    return redirect(url_for("single_file_bp.single_file", file_id=file_id))
