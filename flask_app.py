""" Setup the Flask application """
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv, find_dotenv

from db import db
from routes.auth import login_manager

load_dotenv(find_dotenv())


# Create the app
app = Flask(__name__)

# Pass configuration values
app.config.from_object("config.Config")

login_manager.init_app(app)

with app.app_context():

    # Wire up the routes
    from routes.landing_page import landing_bp
    app.register_blueprint(landing_bp)


if __name__ == "__main__":

    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
