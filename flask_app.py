""" Setup the Flask application """
from flask import Flask

# Create the app
app = Flask(__name__)

# Pass configuration values
app.config.from_object("config.Config")

# Wire up the routes
from routes.landing_page import landing_bp
app.register_blueprint(landing_bp)
