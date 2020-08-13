from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, IntegerField, FloatField


class UpdateMetadataForm(FlaskForm):

    title = StringField("Title")
    model_id = StringField("model ID")
    lat = FloatField("lat")
    lng = FloatField("lng")
    legs = TextField("legs")
    leg_names = TextField("leg names")
    movements = TextField("movements")
    modes = TextField("modes")
