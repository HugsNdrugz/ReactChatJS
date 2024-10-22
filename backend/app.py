import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize SQLAlchemy without binding it to an app yet
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure the SQLAlchemy part of the app instance
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    with app.app_context():
        # Import models here to avoid circular imports
        from . import models
        from . import routes

        # Create database tables
        db.create_all()

        # Register blueprints
        app.register_blueprint(routes.bp)

    return app
