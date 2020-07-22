from flask import Blueprint, render_template

landing_bp = Blueprint(
    'landing_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@landing_bp.route('/')
def landing_page():
    return render_template(
        'home.html',
    )
