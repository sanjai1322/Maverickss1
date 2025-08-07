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
    # Additional timestamp fields for enhanced tracking
    profile_created_at = db.Column(DateTime, default=datetime.utcnow)
    assessment_completed_at = db.Column(DateTime)
    skills_evaluated_at = db.Column(DateTime)
    learning_path_generated_at = db.Column(DateTime)
    
    # Relationships
    learning_paths = db.relationship('LearningPath', backref='user', lazy=True, cascade='all, delete-orphan')
    hackathon_submissions = db.relationship('Hackathon', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'skills': self.skills,
            'scores': self.scores,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_created_at': self.profile_created_at.isoformat() if self.profile_created_at else None,
            'assessment_completed_at': self.assessment_completed_at.isoformat() if self.assessment_completed_at else None,
            'skills_evaluated_at': self.skills_evaluated_at.isoformat() if self.skills_evaluated_at else None,
            'learning_path_generated_at': self.learning_path_generated_at.isoformat() if self.learning_path_generated_at else None
        }


class LearningPath(db.Model):
    """Learning path modules for users to track skill development progress."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    module_name = db.Column(db.String(128), nullable=False)
    estimated_time = db.Column(db.Integer)  # in minutes
    completion_status = db.Column(db.String(32), default='Not Started')  # Not Started, In Progress, Completed
    created_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    
    def __repr__(self):
        return f'<LearningPath {self.username}: {self.module_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'module_name': self.module_name,
            'estimated_time': self.estimated_time,
            'completion_status': self.completion_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Hackathon(db.Model):
    """Hackathon challenge submissions for users."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    challenge_name = db.Column(db.String(128), nullable=False)
    submission = db.Column(db.Text, nullable=False)  # Challenge solution/submission text
    submitted_at = db.Column(DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer)  # Optional scoring for hackathon submissions
    
    def __repr__(self):
        return f'<Hackathon {self.username}: {self.challenge_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'challenge_name': self.challenge_name,
            'submission': self.submission,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'score': self.score
        }
