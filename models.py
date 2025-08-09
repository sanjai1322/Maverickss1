# Legacy models file - models have been moved to backend/database.py
# This file is kept for backward compatibility

from backend.database import *
from backend.admin_models import *
    resume_text = db.Column(db.Text)  # Original resume content
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Enhanced agent-based tracking fields
    profile_created_at = db.Column(DateTime, default=datetime.utcnow)
    assessment_completed_at = db.Column(DateTime)
    skills_evaluated_at = db.Column(DateTime)
    learning_path_generated_at = db.Column(DateTime)
    last_login_at = db.Column(DateTime)
    
    # Agent system integration fields
    agent_profile_data = db.Column(Text)  # JSON data from ProfileAgent
    gamification_data = db.Column(Text)   # JSON data from GamificationAgent
    learning_progress = db.Column(Text)   # JSON data from LearningPathAgent
    analytics_data = db.Column(Text)      # JSON data from AnalyticsAgent
    
    # User preferences and settings
    preferred_learning_style = db.Column(String(50))
    time_commitment_hours = db.Column(Integer, default=5)
    learning_goals = db.Column(Text)  # JSON array of goals
    notification_preferences = db.Column(Text)  # JSON preferences
    
    # Engagement metrics
    total_points = db.Column(Integer, default=0)
    current_level = db.Column(Integer, default=1)
    current_streak = db.Column(Integer, default=0)
    longest_streak = db.Column(Integer, default=0)
    
    # Relationships
    learning_paths = db.relationship('LearningPath', backref='user', lazy=True, cascade='all, delete-orphan')
    hackathon_submissions = db.relationship('Hackathon', backref='user', lazy=True, cascade='all, delete-orphan')
    assessment_attempts = db.relationship('AssessmentAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'skills': self.skills,
            'scores': self.scores,
            'total_points': self.total_points,
            'current_level': self.current_level,
            'current_streak': self.current_streak,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_created_at': self.profile_created_at.isoformat() if self.profile_created_at else None,
            'assessment_completed_at': self.assessment_completed_at.isoformat() if self.assessment_completed_at else None,
            'skills_evaluated_at': self.skills_evaluated_at.isoformat() if self.skills_evaluated_at else None,
            'learning_path_generated_at': self.learning_path_generated_at.isoformat() if self.learning_path_generated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
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
    
    # Enhanced hackathon fields
    hackathon_id = db.Column(String(128))  # Reference to agent system hackathon
    theme = db.Column(String(64))
    difficulty = db.Column(String(32))
    rank = db.Column(Integer)
    final_score = db.Column(Integer)
    evaluation_data = db.Column(Text)  # JSON evaluation details
    team_name = db.Column(String(128))
    
    def __repr__(self):
        return f'<Hackathon {self.username}: {self.challenge_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'challenge_name': self.challenge_name,
            'submission': self.submission,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'score': self.score,
            'final_score': self.final_score,
            'rank': self.rank,
            'theme': self.theme,
            'difficulty': self.difficulty
        }


class AssessmentAttempt(db.Model):
    """Track individual assessment attempts for detailed analytics."""
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_id = db.Column(String(128), nullable=False)
    
    # Assessment details
    started_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    duration_minutes = db.Column(Integer)
    
    # Results
    total_score = db.Column(Integer)
    max_possible_score = db.Column(Integer)
    questions_attempted = db.Column(Integer)
    questions_correct = db.Column(Integer)
    
    # Detailed data
    question_responses = db.Column(Text)  # JSON array of responses
    skill_breakdown = db.Column(Text)     # JSON skill-level scores
    difficulty_level = db.Column(String(32))
    assessment_type = db.Column(String(64))
    
    def __repr__(self):
        return f'<AssessmentAttempt {self.user_id}: {self.assessment_id}>'


class UserAchievement(db.Model):
    """Track user achievements and badges."""
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey('user.id'), nullable=False)
    
    achievement_type = db.Column(String(64), nullable=False)
    achievement_name = db.Column(String(128), nullable=False)
    badge_level = db.Column(String(32))  # bronze, silver, gold, platinum
    description = db.Column(Text)
    icon = db.Column(String(64))
    
    earned_at = db.Column(DateTime, default=datetime.utcnow)
    points_awarded = db.Column(Integer, default=0)
    
    # Achievement criteria met
    criteria_data = db.Column(Text)  # JSON data about how it was earned
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id}: {self.achievement_name}>'


class LearningModule(db.Model):
    """Individual learning modules within learning paths."""
    id = db.Column(Integer, primary_key=True)
    learning_path_id = db.Column(Integer, db.ForeignKey('learning_path.id'), nullable=False)
    
    title = db.Column(String(256), nullable=False)
    description = db.Column(Text)
    module_order = db.Column(Integer, default=0)
    
    # Content details
    topics = db.Column(Text)  # JSON array of topics
    estimated_hours = db.Column(Integer)
    difficulty_level = db.Column(String(32))
    
    # Progress tracking
    completion_status = db.Column(String(32), default='not_started')
    completion_percentage = db.Column(Integer, default=0)
    started_at = db.Column(DateTime)
    completed_at = db.Column(DateTime)
    
    # Performance data
    exercises_completed = db.Column(Integer, default=0)
    average_score = db.Column(Integer)
    time_spent_minutes = db.Column(Integer, default=0)
    
    def __repr__(self):
        return f'<LearningModule {self.title}>'


class PlatformEvent(db.Model):
    """Track all platform events for analytics."""
    id = db.Column(Integer, primary_key=True)
    
    # Event identification
    event_id = db.Column(String(128), unique=True, nullable=False)
    event_type = db.Column(String(64), nullable=False)
    source_agent = db.Column(String(64))
    target_agent = db.Column(String(64))
    
    # Event context
    user_id = db.Column(Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    
    # Event data
    payload = db.Column(Text)  # JSON event payload
    processing_status = db.Column(String(32), default='processed')
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<PlatformEvent {self.event_type}>'


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
