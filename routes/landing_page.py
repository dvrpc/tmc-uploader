from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
)
from flask_login import current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from models import User
from db import db


class SignupForm(FlaskForm):
    """User Sign-up Form."""
    name = StringField(
        'User Name',
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Select a stronger password.')
        ]
    )
    confirm = PasswordField(
        'Confirm Your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User Log-in Form."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Enter a valid email.')
        ]
    )
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


landing_bp = Blueprint(
    'landing_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@landing_bp.route('/', methods=['GET', 'POST'])
def landing_page():
    """
    """
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect("www.google.com")  
        # return redirect(url_for('landing_bp.landing_page'))  

    login_form = LoginForm()
    signup_form = SignupForm()

    if request.method == 'POST':

        if request.form['submit'] == 'login':
            if login_form.validate_on_submit() and login_form.email.data:
                user = User.query.filter_by(
                    email=login_form.email.data
                ).first()

                if user and user.check_password(
                    password=login_form.password.data
                ):
                    login_user(user)
                    return redirect(url_for('main_bp.dashboard'))

            flash(r'Invalid username/password combination', "danger")

        if request.form['submit'] == 'signup':

            # Validate login attempt
            email_domain = request.form["email"].split("@")[-1]
            if email_domain != "dvrpc.org":
                flash('This application is only accessible to DVRPC employees.', "danger")

            elif signup_form.validate_on_submit() and signup_form.email.data:
                existing_user = User.query.filter_by(
                    email=signup_form.email.data
                ).first()

                if existing_user is None:
                    user = User(
                        name=signup_form.name.data,
                        email=signup_form.email.data
                    )
                    user.set_password(signup_form.password.data)
                    db.session.add(user)
                    db.session.commit()  # Create new user
                    login_user(user)  # Log in as newly created user
                    return redirect(url_for('main_bp.dashboard'))

                flash('A user already exists with that email address.', "danger")

    return render_template(
        'home.html',
        # login_form=login_form,
        # signup_form=signup_form,
    )
