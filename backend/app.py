import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# Initialize SQLAlchemy without binding it to an app yet
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configure the SQLAlchemy part of the app instance using environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}@{os.environ['PGHOST']}:{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')

    # Initialize SQLAlchemy with the app
    db.init_app(app)

    with app.app_context():
        # Import models here to avoid circular imports
        from . import models
        from . import routes

        # Create database tables
        db.create_all()

        # Create sample data
        create_sample_data()

        # Register blueprints
        app.register_blueprint(routes.bp)

        # Initialize the app (including creating full-text search index)
        routes.init_app(app)

    return app

def create_sample_data():
    from .models import Contact, Message
    if Contact.query.count() == 0:
        # Create sample contacts
        alice = Contact(name="Alice")
        bob = Contact(name="Bob")
        charlie = Contact(name="Charlie")
        db.session.add_all([alice, bob, charlie])
        db.session.commit()

        # Create sample messages
        messages = [
            Message(sender=alice, receiver=bob, content="Hey Bob, how are you?"),
            Message(sender=bob, receiver=alice, content="Hi Alice, I'm good! How about you?"),
            Message(sender=charlie, receiver=alice, content="Alice, don't forget about our meeting tomorrow!"),
            Message(sender=alice, receiver=charlie, content="Thanks for the reminder, Charlie!"),
        ]
        db.session.add_all(messages)
        db.session.commit()

        # Update last messages for contacts
        alice.last_message = "Thanks for the reminder, Charlie!"
        alice.last_message_time = datetime.utcnow()
        bob.last_message = "Hi Alice, I'm good! How about you?"
        bob.last_message_time = datetime.utcnow()
        charlie.last_message = "Alice, don't forget about our meeting tomorrow!"
        charlie.last_message_time = datetime.utcnow()
        db.session.commit()

        print("Sample data created successfully!")
    else:
        print("Sample data already exists. Skipping creation.")
