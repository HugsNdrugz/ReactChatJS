from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import func, or_, text
from datetime import datetime, timedelta
from .app import db
from .models import Contact, Message

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/contacts')
def get_contacts():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 20

    contacts = Contact.query.filter(Contact.name.ilike(f'%{search_query}%')) \
        .order_by(Contact.last_message_time.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'contacts': [contact.to_dict() for contact in contacts.items],
        'has_next': contacts.has_next
    })

@bp.route('/api/chat/<int:contact_id>')
def get_chat_history(contact_id):
    page = int(request.args.get('page', 1))
    per_page = 50
    search_query = request.args.get('search', '')

    # Create a full-text search query
    search_vector = func.to_tsvector('english', Message.content)
    search_query_tsquery = func.plainto_tsquery('english', search_query)

    # Build the base query
    base_query = Message.query.filter(
        (Message.sender_id == contact_id) | (Message.receiver_id == contact_id)
    )

    # Apply search if a query is provided
    if search_query:
        base_query = base_query.filter(search_vector.match(search_query_tsquery))

    # Order by timestamp and paginate
    messages = base_query.order_by(Message.timestamp.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'messages': [message.to_dict() for message in messages.items],
        'has_next': messages.has_next
    })

@bp.route('/api/statistics/<int:contact_id>')
def get_chat_statistics(contact_id):
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)

    daily_counts = db.session.query(
        func.date(Message.timestamp).label('date'),
        func.count().label('count')
    ).filter(
        (Message.sender_id == contact_id) | (Message.receiver_id == contact_id),
        Message.timestamp >= start_date
    ).group_by(func.date(Message.timestamp)) \
     .order_by(func.date(Message.timestamp)).all()

    return jsonify([{'date': str(date), 'count': count} for date, count in daily_counts])

def create_fulltext_search_index():
    with db.engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_message_content_fts ON message USING gin(to_tsvector('english', content));
        """))
        print("Full-text search index created successfully.")

def init_app(app):
    with app.app_context():
        create_fulltext_search_index()
