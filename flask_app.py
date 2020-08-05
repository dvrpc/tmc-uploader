""" Setup the Flask application """
import os
from flask import Flask

from db import db
from routes.auth import login_manager
from sql_connection import SQLALCHEMY_DATABASE_URI

# General Config
DEBUG = True
SECRET_KEY = os.urandom(32)

# Database
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Create the app
app = Flask(__name__)

# Pass configuration values
app.config["DEBUG"] = DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_ECHO"] = SQLALCHEMY_ECHO
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
login_manager.init_app(app)

with app.app_context():

    # Wire up the routes

    # Landing pages
    from routes.landing_page import landing_bp
    app.register_blueprint(landing_bp)

    # File views
    from routes.all_files import all_files_bp
    app.register_blueprint(all_files_bp)

    # Upload data views
    from routes.upload_file import upload_bp
    app.register_blueprint(upload_bp)

    # Project pages
    from routes.projects import project_bp
    app.register_blueprint(project_bp)

    # Single file views
    from routes.single_file import single_file_bp
    app.register_blueprint(single_file_bp)


if __name__ == "__main__":

    with app.app_context():
        db.create_all()
    app.run(debug=True)
