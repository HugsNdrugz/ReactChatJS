from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from datetime import datetime
from .models import db, Chat

bp = Blueprint('api', __name__)

@bp.route('/api/chat/<string:contact>')
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

def init_app(app):
    app.register_blueprint(bp, url_prefix='/api')
