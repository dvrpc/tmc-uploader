from flask import (
    Blueprint,
    render_template,
    flash
)
from flask_login import login_required, current_user


from db import db
from models import Project
from forms.add_project_form import AddProjectForm


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
