import json
from flask import (
    Blueprint,
    render_template,
    flash,
    request
)
from flask_login import login_required

# Plotting
import plotly
import plotly.graph_objects as go
from sqlalchemy import create_engine
import pandas as pd


from db import db
from models import TMCFile
from forms.file_metadata_form import UpdateMetadataForm
from sql_connection import SQLALCHEMY_DATABASE_URI


single_file_bp = Blueprint(
    'single_file_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@single_file_bp.route('/file/<file_id>', methods=['GET', 'POST'])
@login_required
def single_file(file_id):
    """ Page that allows users to interact with a single TMC file """

    this_file = TMCFile.query.filter_by(uid=file_id).first()

    form = UpdateMetadataForm()

    if request.method == 'POST':

        this_file.title = str(form.title.data)
        if form.model_id.data:
            if type(form.model_id.data) == int:
                this_file.model_id = int(form.model_id.data)

        this_file.lat = str(form.lat.data)
        this_file.lng = str(form.lng.data)
        this_file.legs = str(form.legs.data)
        this_file.movements = str(form.movements.data)
        this_file.modes = str(form.modes.data)

        db.session.commit()

        flash(f"Successfully updated metadata", "success")

    latlng_data = [this_file.lat, this_file.lng]

    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    df = pd.read_sql(f"SELECT * FROM tmc_data.tmc_{file_id};", engine, index_col="datetime")
    engine.dispose()

    data = []
    for col in df.columns:
        if "total_" not in col:
            data.append(go.Bar(x=df.index, y=df[col], name=col))

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'single_file.html',
        this_file=this_file,
        latlng_data=json.dumps(latlng_data),
        form=form,
        fig=graphJSON,
    )
