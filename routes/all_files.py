import json
from flask import (
    Blueprint,
    render_template,
)
from flask_login import login_required


from models import TMCFile
from forms.upload_file_form import UploadFileForm


all_files_bp = Blueprint(
    'all_files_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@all_files_bp.route('/all-files', methods=['GET', 'POST'])
@login_required
def all_files():
    """ Page that shows all files in the database """

    all_files = TMCFile.query.order_by(TMCFile.uid.desc()).all()

    latlng_data = [[f.lat, f.lng, f.name()] for f in all_files if f.lat]

    return render_template(
        'all_files.html',
        all_files=all_files,
        form=UploadFileForm(),
        latlngs=json.dumps(latlng_data)
    )
