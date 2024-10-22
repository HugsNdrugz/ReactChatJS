from flask import Blueprint, jsonify, request
from sqlalchemy import func
from datetime import datetime, timedelta
from .app import db
from .models import Contact, Message

bp = Blueprint('main', __name__)

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

    messages = Message.query.filter(
        (Message.sender_id == contact_id) | (Message.receiver_id == contact_id)
    ).order_by(Message.timestamp.desc()) \
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
