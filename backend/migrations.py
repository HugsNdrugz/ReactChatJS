from flask import current_app
from flask_migrate import Migrate
from sqlalchemy import text
from .app import db

def upgrade():
    with current_app.app_context():
        db.session.execute(text("ALTER TABLE chats ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;"))
        db.session.commit()

def downgrade():
    with current_app.app_context():
        db.session.execute(text("ALTER TABLE chats DROP COLUMN IF EXISTS id;"))
        db.session.commit()

migrate = Migrate(current_app, db)
