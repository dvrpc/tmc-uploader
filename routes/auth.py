from flask import flash, redirect, url_for
from flask_login import logout_user, current_user, login_user, LoginManager

from models import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.get_started'))


# @auth_bp.route('/logout', methods=['GET'])
# def logout():
#     logout_user()
#     return redirect("/")
