import json
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request
)
from flask_login import login_required, current_user

import plotly
import plotly.graph_objects as go

from db import db
from models import Project, TMCFile
from forms.add_project_form import AddProjectForm
from forms.assign_files_to_project import AssignFilesToProject
from common.get_project_data import project_df


project_bp = Blueprint(
    'project_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@project_bp.route('/all-projects', methods=['GET', 'POST'])
@login_required
def all_projects():
    """ Page that shows all PROJECTS in the database """

    form = AddProjectForm()

    if form.validate_on_submit():
        new_name = form.project_name.data
        desc = form.description.data

        # QA -  check the user input
        if len(new_name) == 0:
            flash("Please provide a name for your project", "danger")
            return redirect(url_for('project_bp.all_projects'))

        if len(new_name) > 50:
            flash("Please use a shorter name for your project", "danger")
            return redirect(url_for('project_bp.all_projects'))

        if len(desc) == 0:
            flash("Please provide a description for your project", "danger")
            return redirect(url_for('project_bp.all_projects'))

        # Check if this project already exists
        if Project.query.filter_by(name=new_name).first():
            flash(f'A project named "{new_name}" already exists', "danger")
            return redirect(url_for('project_bp.all_projects'))

        new_project = Project(
            name=new_name,
            description=desc,
            created_by=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()

        flash(f"Added new project named: {new_name}", "info")

    all_projects = Project.query.all()

    return render_template(
        'all_projects.html',
        all_projects=all_projects,
        form=form,
    )


@project_bp.route('/project/<project_id>', methods=['GET', 'POST'])
@login_required
def single_project(project_id):
    """ Page for a SINGLE PROJECT """

    this_project = Project.query.filter_by(uid=project_id).first()

    all_tmc_files = TMCFile.query.all()

    form = AssignFilesToProject()

    # if form.validate_on_submit():
    if request.method == "POST":
        data = dict((key, request.form.getlist(key) if len(
            request.form.getlist(key)) > 1 else request.form.getlist(key)[0])
            for key in request.form.keys())

        # Run thru all checkboxes
        selected_files = []
        for filename in data:
            file_id = int(filename.split("_")[-1])
            selected_files.append(file_id)
            file_obj = TMCFile.query.filter_by(uid=file_id).first()
            if file_obj not in this_project.tmc_files:
                this_project.tmc_files.append(file_obj)
                flash(f"Added {file_obj.name()} to this project", "success")

        # Remove any unselected files
        for tmcfile in this_project.tmc_files:
            file_id = tmcfile.uid
            if file_id not in selected_files:
                file_obj = TMCFile.query.filter_by(uid=file_id).first()
                this_project.tmc_files.remove(file_obj)
                flash(f"Removed {file_obj.name()} from this project", "warning")

        db.session.commit()


    #     new_name = form.project_name.data
    #     desc = form.description.data

    #     # QA -  check the user input
    #     if len(new_name) == 0:
    #         flash("Please provide a name for your project", "danger")
    #         return redirect(url_for('project_bp.all_projects'))

    #     if len(new_name) > 50:
    #         flash("Please use a shorter name for your project", "danger")
    #         return redirect(url_for('project_bp.all_projects'))

    #     if len(desc) == 0:
    #         flash("Please provide a description for your project", "danger")
    #         return redirect(url_for('project_bp.all_projects'))

    #     # Check if this project already exists
    #     if Project.query.filter_by(name=new_name).first():
    #         flash(f'A project named "{new_name}" already exists', "danger")
    #         return redirect(url_for('project_bp.all_projects'))

    #     new_project = Project(
    #         name=new_name,
    #         description=desc,
    #         created_by=current_user.id
    #     )
    #     db.session.add(new_project)
    #     db.session.commit()

    #     flash(f"Added new project named: {new_name}", "info")

    # all_projects = Project.query.all()

    this_project = Project.query.filter_by(uid=project_id).first()

    latlng_data = [[f.lat, f.lng] for f in this_project.tmc_files]

    all_dfs = project_df(project_id)

    data = []
    for df in all_dfs:
        df_name = df.location.unique()[0]
        data.append(go.Bar(x=df.index, y=df["total_15_min"], name=df_name))

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)


    # flash(df, "info")

    return render_template(
        'single_project.html',
        this_project=this_project,
        latlng_data=json.dumps(latlng_data),
        all_tmc_files=all_tmc_files,
        fig=graphJSON,
        # all_projects=all_projects,
        # form=form,
    )
