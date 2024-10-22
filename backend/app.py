import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import func, text, or_
from flask_migrate import Migrate

# Initialize SQLAlchemy without binding it to an app yet
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})

    # Configure the SQLAlchemy part of the app instance using environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ['PGUSER']}:{os.environ['PGPASSWORD']}@{os.environ['PGHOST']}:{os.environ['PGPORT']}/{os.environ['PGDATABASE']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')

    # Initialize SQLAlchemy and Flask-Migrate with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from .models import Chat

    @app.route('/api/contacts')
    def get_contacts():
        page = int(request.args.get('page', 1))
        per_page = 20
        search_query = request.args.get('search', '')

        # Create a subquery to get the latest message for each sender
        subquery = db.session.query(
            Chat.sender,
            func.max(Chat.time).label('last_message_time'),
            func.first_value(Chat.text).over(
                partition_by=Chat.sender,
                order_by=Chat.time.desc()
            ).label('last_message')
        ).group_by(Chat.sender).subquery()

        # Query contacts with search functionality
        query = db.session.query(
            subquery.c.sender,
            subquery.c.last_message_time,
            subquery.c.last_message
        ).order_by(subquery.c.last_message_time.desc())

        if search_query:
            query = query.filter(subquery.c.sender.ilike(f'%{search_query}%'))

        contacts = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'contacts': [
                {
                    'id': contact.sender,
                    'name': contact.sender,
                    'last_message': contact.last_message,
                    'last_message_time': contact.last_message_time.isoformat()
                } for contact in contacts.items
            ],
            'has_next': contacts.has_next
        })

    @app.route('/api/chat/<string:contact>')
    def get_chat_history(contact):
        page = int(request.args.get('page', 1))
        per_page = 50
        search_query = request.args.get('search', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Build the base query
        base_query = Chat.query.filter(Chat.sender.in_([contact, 'You']))

        # Apply search if a query is provided
        if search_query:
            base_query = base_query.filter(
                or_(
                    Chat.text.ilike(f'%{search_query}%'),
                    Chat.sender.ilike(f'%{search_query}%')
                )
            )

        # Apply date range filter if provided
        if start_date:
            base_query = base_query.filter(Chat.time >= datetime.fromisoformat(start_date))
        if end_date:
            base_query = base_query.filter(Chat.time <= datetime.fromisoformat(end_date))

        # Order by timestamp and paginate
        messages = base_query.order_by(Chat.time.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'messages': [message.to_dict() for message in messages.items],
            'has_next': messages.has_next
        })

    @app.route('/api/statistics/<string:contact>')
    def get_chat_statistics(contact):
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)

        daily_counts = db.session.query(
            func.date(Chat.time).label('date'),
            func.count().label('count')
        ).filter(
            Chat.sender.in_([contact, 'You']),
            Chat.time >= start_date
        ).group_by(func.date(Chat.time)) \
         .order_by(func.date(Chat.time)).all()

        return jsonify([{'date': str(date), 'count': count} for date, count in daily_counts])

    def create_fulltext_search_index():
        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chat_text_fts ON chats USING gin(to_tsvector('english', text));
            """))
            print("Full-text search index created successfully.")

    with app.app_context():
        # Create database tables
        db.create_all()

        # Create full-text search index
        create_fulltext_search_index()

    return app
