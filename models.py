from app import db
from sqlalchemy import DateTime
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    skills = db.Column(db.Text)  # JSON string of extracted skills
    scores = db.Column(db.Text)  # JSON string of assessment scores and responses
    resume_text = db.Column(db.Text)  # Original resume content
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'skills': self.skills,
            'scores': self.scores,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
