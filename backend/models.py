from .app import db
from datetime import datetime

class Chat(db.Model):
    __tablename__ = 'chats'
    chat_id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.Text, nullable=False)
    messenger = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.chat_id,
            'sender': self.sender,
            'time': self.time.isoformat(),
            'text': self.text,
            'messenger': self.messenger
        }
