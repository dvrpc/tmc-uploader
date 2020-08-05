from flask_wtf import FlaskForm
from wtforms import FileField


class UploadFileForm(FlaskForm):
    selected_file = FileField()
