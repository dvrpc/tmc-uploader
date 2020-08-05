from flask_wtf import FlaskForm
from wtforms import StringField, TextField


class AddProjectForm(FlaskForm):
    project_name = StringField()
    description = TextField()
