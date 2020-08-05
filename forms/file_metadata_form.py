from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, IntegerField


class UpdateMetadataForm(FlaskForm):

    title = StringField("Title")
    model_id = IntegerField("model ID")
    lat = StringField("lat")
    lng = StringField("lng")
    legs = TextField("legs")
    movements = TextField("movements")
    modes = TextField("modes")

    submit = SubmitField('Update Metadata')