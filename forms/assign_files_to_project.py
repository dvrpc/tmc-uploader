from flask_wtf import FlaskForm
from wtforms import IntegerField


class AssignFilesToProject(FlaskForm):

    file_id = IntegerField("File ID")
