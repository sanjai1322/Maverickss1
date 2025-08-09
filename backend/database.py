"""
Database Models and Configuration
=================================

This file contains all database models for the Mavericks platform.
Models are organized by functionality:
- Core User Models: User, UserProfile data
- Learning Models: LearningPath, AssessmentAttempt, etc.
- Admin Models: AdminUser, UserActivity, SystemAnalytics
- Agent Models: UserAchievement, PlatformEvent for agent system

Each model includes:
- Clear field definitions with comments
- Relationship mappings
- Helper methods for data conversion
- Proper constraints and validation
"""

from app import db
from sqlalchemy import DateTime, Text, Integer, String, Boolean, Float
from datetime import datetime


class User(db.Model):
    """
    Core user model storing all user information and progress.
    
    This is the central model that connects to all other user-related data.
    It stores:
    - Basic profile information (username, skills extracted from resume)
    - Assessment and learning progress timestamps
    - Agent system data (JSON fields for each agent's data)
    - Gamification metrics (points, levels, streaks)
    """
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # Core profile data extracted from resume
    skills = db.Column(db.Text)  # JSON string of extracted skills
    scores = db.Column(db.Text)  # JSON string of assessment scores and responses
    resume_text = db.Column(db.Text)  # Original resume content for re-analysis
    
    # Timeline tracking - when important events happened
    created_at = db.Column(DateTime, default=datetime.utcnow)
    profile_created_at = db.Column(DateTime, default=datetime.utcnow)
    assessment_completed_at = db.Column(DateTime)
    skills_evaluated_at = db.Column(DateTime)
    learning_path_generated_at = db.Column(DateTime)
    last_login_at = db.Column(DateTime)
    
    # Agent system integration fields - store JSON data from each specialized agent
    agent_profile_data = db.Column(Text)  # Data from ProfileAgent (detailed skill analysis)
    gamification_data = db.Column(Text)   # Data from GamificationAgent (achievements, badges)
    learning_progress = db.Column(Text)   # Data from LearningPathAgent (custom curricula)
    analytics_data = db.Column(Text)      # Data from AnalyticsAgent (usage patterns, insights)
    
    # User preferences and learning configuration
    preferred_learning_style = db.Column(String(50))  # visual, auditory, kinesthetic, reading
    time_commitment_hours = db.Column(Integer, default=5)  # hours per week available for learning
    learning_goals = db.Column(Text)  # JSON array of specific learning objectives
    notification_preferences = db.Column(Text)  # JSON preferences for notifications
    
    # Gamification and engagement metrics
    total_points = db.Column(Integer, default=0)  # Total points earned across platform
    current_level = db.Column(Integer, default=1)  # Current user level based on points
    current_streak = db.Column(Integer, default=0)  # Current consecutive days active
    longest_streak = db.Column(Integer, default=0)  # Longest streak ever achieved
    
    # Database relationships - connect to related data
    learning_paths = db.relationship('LearningPath', backref='user', lazy=True, cascade='all, delete-orphan')
    hackathon_submissions = db.relationship('Hackathon', backref='user', lazy=True, cascade='all, delete-orphan')
    assessment_attempts = db.relationship('AssessmentAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """
        Convert user data to dictionary for API responses and JSON serialization.
        
        Returns:
            dict: User data with properly formatted timestamps
        """
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
    """
    Individual learning modules that make up a user's personalized curriculum.
    
    Each record represents one learning module (like "Python Basics" or "React Components").
    Multiple modules together form a complete learning path for the user.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Module information
    module_name = db.Column(db.String(128), nullable=False)  # e.g., "Python Data Structures"
    estimated_time = db.Column(db.Integer)  # estimated completion time in minutes
    
    # Progress tracking
    completion_status = db.Column(db.String(32), default='Not Started')  # Not Started, In Progress, Completed
    created_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)  # when user finished this module
    
    def __repr__(self):
        return f'<LearningPath {self.username}: {self.module_name}>'
    
    def to_dict(self):
        """Convert learning path data to dictionary for API responses."""
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
    """
    Hackathon challenge submissions and competition data.
    
    Stores both the coding challenges users participate in and their submissions.
    Includes scoring, ranking, and evaluation data for competitions.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Challenge information
    challenge_name = db.Column(db.String(128), nullable=False)  # e.g., "Build a REST API"
    submission = db.Column(db.Text, nullable=False)  # user's code submission
    submitted_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Basic scoring
    score = db.Column(db.Integer)  # basic score for the submission
    
    # Enhanced hackathon fields for agent system
    hackathon_id = db.Column(String(128))  # reference to agent system hackathon
    theme = db.Column(String(64))  # hackathon theme like "AI/ML" or "Web Development"
    difficulty = db.Column(String(32))  # beginner, intermediate, advanced
    rank = db.Column(Integer)  # user's rank in this hackathon
    final_score = db.Column(Integer)  # final evaluated score
    evaluation_data = db.Column(Text)  # JSON with detailed evaluation from agents
    team_name = db.Column(String(128))  # if participating as team
    
    def __repr__(self):
        return f'<Hackathon {self.username}: {self.challenge_name}>'
    
    def to_dict(self):
        """Convert hackathon data to dictionary for API responses."""
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
    """
    Detailed tracking of user assessment attempts and performance.
    
    Stores comprehensive data about each time a user takes an assessment,
    including question-by-question breakdown and skill-specific scores.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Assessment session information
    attempt_number = db.Column(Integer, default=1)  # if user retakes assessment
    started_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    
    # Assessment content and responses
    questions_data = db.Column(Text)  # JSON with questions asked
    responses_data = db.Column(Text)  # JSON with user's answers
    
    # Scoring and evaluation
    total_score = db.Column(Integer)  # overall assessment score
    skill_breakdown = db.Column(Text)  # JSON with score per skill area
    
    # Agent system evaluation
    evaluation_data = db.Column(Text)  # JSON with detailed agent analysis
    recommendations = db.Column(Text)  # JSON with learning recommendations
    
    def __repr__(self):
        return f'<AssessmentAttempt {self.username}: Attempt {self.attempt_number}>'


class UserAchievement(db.Model):
    """
    User achievements and badges earned through platform activities.
    
    Tracks accomplishments like "First Assessment", "Skill Master", "Fast Learner"
    that motivate continued engagement and learning.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Achievement details
    achievement_type = db.Column(db.String(50))  # category: assessment, learning, engagement
    achievement_name = db.Column(db.String(100))  # display name like "First Assessment Complete"
    achievement_description = db.Column(db.Text)  # detailed description of accomplishment
    
    # Gamification
    points_earned = db.Column(Integer, default=0)  # points awarded for this achievement
    badge_icon = db.Column(String(50))  # icon identifier for display
    
    # Tracking
    earned_at = db.Column(DateTime, default=datetime.utcnow)
    criteria_met = db.Column(Text)  # JSON with specific criteria that were met
    
    def __repr__(self):
        return f'<UserAchievement {self.username}: {self.achievement_name}>'


class LearningModule(db.Model):
    """
    Individual learning modules within learning paths.
    
    Represents specific learning content like lessons, exercises, or projects
    that users complete as part of their personalized curriculum.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    learning_path_id = db.Column(Integer, db.ForeignKey('learning_path.id'))
    
    # Module content
    module_title = db.Column(String(128), nullable=False)
    module_description = db.Column(Text)
    module_type = db.Column(String(32))  # lesson, exercise, project, quiz
    content_data = db.Column(Text)  # JSON with module content
    
    # Progress tracking
    status = db.Column(String(32), default='not_started')  # not_started, in_progress, completed
    progress_percentage = db.Column(Integer, default=0)  # 0-100
    time_spent = db.Column(Integer, default=0)  # minutes spent on this module
    
    # Completion tracking
    started_at = db.Column(DateTime)
    completed_at = db.Column(DateTime)
    
    def __repr__(self):
        return f'<LearningModule {self.username}: {self.module_title}>'


class PlatformEvent(db.Model):
    """
    Complete event tracking for agent system analytics.
    
    Records all significant events that happen on the platform for analysis
    by the AnalyticsAgent and other system components.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event identification
    event_type = db.Column(String(50), nullable=False)  # user_registered, assessment_completed, etc.
    event_name = db.Column(String(100))  # human-readable event name
    
    # Event context
    username = db.Column(String(64), db.ForeignKey('user.username'))  # user who triggered event
    session_id = db.Column(String(128))  # session identifier
    
    # Event data
    event_data = db.Column(Text)  # JSON with event-specific data
    event_metadata = db.Column(Text)  # JSON with additional context
    
    # Tracking
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    ip_address = db.Column(String(45))  # user's IP address
    user_agent = db.Column(String(255))  # browser/client information
    
    def __repr__(self):
        return f'<PlatformEvent {self.event_type}: {self.username}>'


# Legacy models for backward compatibility
class TailoredCourse(db.Model):
    """
    Legacy model: AI-generated courses with completion tracking.
    Kept for backward compatibility with existing data.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    course_title = db.Column(db.String(200), nullable=False)
    course_content = db.Column(db.Text, nullable=False)
    estimated_duration = db.Column(db.String(50))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    completion_status = db.Column(db.String(32), default='Not Started')
    completed_at = db.Column(DateTime)
    
    def __repr__(self):
        return f'<TailoredCourse {self.username}: {self.course_title}>'


class CourseModule(db.Model):
    """
    Legacy model: Individual learning modules within courses.
    Kept for backward compatibility with existing data.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('tailored_course.id'), nullable=False)
    module_title = db.Column(db.String(200), nullable=False)
    module_content = db.Column(db.Text, nullable=False)
    module_order = db.Column(db.Integer, default=1)
    estimated_time = db.Column(db.String(50))
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(DateTime)
    
    def __repr__(self):
        return f'<CourseModule {self.module_title}>'


class ProgressTracking(db.Model):
    """
    Legacy model: Real-time activity and progress monitoring.
    Kept for backward compatibility with existing data.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    activity_data = db.Column(db.Text)
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProgressTracking {self.username}: {self.activity_type}>'