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
    last_login_at = db.Column(DateTime)
    
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


class TailoredCourse(db.Model):
    """AI-generated tailored courses for users based on resume analysis."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    course_title = db.Column(db.String(200), nullable=False)
    course_description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(50))
    estimated_duration = db.Column(db.String(50))
    course_plan = db.Column(db.Text)  # JSON string with full course structure
    skill_focus = db.Column(db.Text)  # JSON array of skills this course targets
    created_at = db.Column(DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Relationships
    modules = db.relationship('CourseModule', backref='tailored_course', lazy=True, cascade='all, delete-orphan')
    progress_tracking = db.relationship('ProgressTracking', backref='tailored_course', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TailoredCourse {self.username}: {self.course_title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'course_title': self.course_title,
            'course_description': self.course_description,
            'difficulty_level': self.difficulty_level,
            'estimated_duration': self.estimated_duration,
            'course_plan': self.course_plan,
            'skill_focus': self.skill_focus,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'completion_percentage': self.completion_percentage
        }


class CourseModule(db.Model):
    """Individual modules within tailored courses."""
    id = db.Column(db.Integer, primary_key=True)
    tailored_course_id = db.Column(db.Integer, db.ForeignKey('tailored_course.id'), nullable=False)
    module_title = db.Column(db.String(200), nullable=False)
    module_description = db.Column(db.Text)
    module_order = db.Column(db.Integer, nullable=False)
    resources = db.Column(db.Text)  # JSON string with videos, articles, exercises
    estimated_time = db.Column(db.Integer)  # minutes
    is_completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(DateTime)
    
    def __repr__(self):
        return f'<CourseModule {self.module_title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tailored_course_id': self.tailored_course_id,
            'module_title': self.module_title,
            'module_description': self.module_description,
            'module_order': self.module_order,
            'resources': self.resources,
            'estimated_time': self.estimated_time,
            'is_completed': self.is_completed,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None
        }


class ProgressTracking(db.Model):
    """Real-time progress tracking for tailored courses."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    tailored_course_id = db.Column(db.Integer, db.ForeignKey('tailored_course.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('course_module.id'), nullable=True)
    activity_type = db.Column(db.String(50))  # video_watched, exercise_completed, quiz_taken, reading_completed
    activity_detail = db.Column(db.Text)  # JSON string with specific activity data
    time_spent = db.Column(db.Integer)  # minutes spent on activity
    completion_rate = db.Column(db.Float)  # percentage of activity completed
    score = db.Column(db.Integer)  # score if applicable (quiz/exercise)
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    ai_feedback = db.Column(db.Text)  # AI-generated feedback based on performance
    
    def __repr__(self):
        return f'<ProgressTracking {self.username}: {self.activity_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'tailored_course_id': self.tailored_course_id,
            'module_id': self.module_id,
            'activity_type': self.activity_type,
            'activity_detail': self.activity_detail,
            'time_spent': self.time_spent,
            'completion_rate': self.completion_rate,
            'score': self.score,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ai_feedback': self.ai_feedback
        }
