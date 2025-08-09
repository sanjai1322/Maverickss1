"""
Admin and System Models
======================

This file contains models specifically for administrative functions:
- AdminUser: Administrator accounts and permissions
- UserActivity: Detailed logging of user actions
- UserReport: Generated reports for analysis
- SystemAnalytics: Platform-wide metrics and performance data

These models support the admin dashboard and provide insights into
platform usage, user behavior, and system performance.
"""

from app import db
from sqlalchemy import DateTime, Text, Integer, String, Boolean, Float
from datetime import datetime


class AdminUser(db.Model):
    """
    Administrator accounts for accessing the admin dashboard.
    
    Provides authentication and permission management for platform administrators
    who need to monitor users, generate reports, and manage system settings.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication information
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # securely hashed password
    
    # Permissions and status
    is_admin = db.Column(db.Boolean, default=True)  # admin privilege flag
    is_active = db.Column(db.Boolean, default=True)  # account active status
    
    # Tracking
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_login = db.Column(DateTime)  # when admin last accessed dashboard
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
    
    def to_dict(self):
        """Convert admin user data to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class UserActivity(db.Model):
    """
    Detailed logging of all user activities for analytics and monitoring.
    
    Records every significant action users take on the platform including:
    - Login/logout events
    - Profile updates
    - Assessment attempts
    - Learning progress
    - Hackathon participation
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Activity classification
    activity_type = db.Column(db.String(50), nullable=False)  # login, assessment_start, etc.
    activity_category = db.Column(db.String(32))  # authentication, learning, assessment, etc.
    
    # Activity details
    activity_details = db.Column(db.Text)  # JSON string with specific activity data
    result = db.Column(db.String(32))  # success, failure, partial, etc.
    
    # Technical context
    ip_address = db.Column(db.String(45))  # user's IP address for security
    user_agent = db.Column(db.String(255))  # browser/device information
    session_id = db.Column(db.String(128))  # session identifier
    
    # Timing
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    duration = db.Column(Integer)  # activity duration in seconds
    
    def __repr__(self):
        return f'<UserActivity {self.username}: {self.activity_type}>'
    
    def to_dict(self):
        """Convert activity data to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'activity_type': self.activity_type,
            'activity_category': self.activity_category,
            'result': self.result,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration': self.duration
        }


class UserReport(db.Model):
    """
    Generated reports for users and administrators.
    
    Stores comprehensive reports about user progress, learning outcomes,
    skill development, and platform engagement that can be accessed by
    users themselves or administrators for analysis.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Report classification
    report_type = db.Column(db.String(50), nullable=False)  # progress, skills, assessment, learning_path
    report_title = db.Column(db.String(128))  # human-readable report title
    
    # Report content
    report_data = db.Column(db.Text, nullable=False)  # JSON string with report details
    summary = db.Column(db.Text)  # executive summary of key findings
    
    # Report metadata
    generated_at = db.Column(DateTime, default=datetime.utcnow)
    generated_by = db.Column(db.String(64))  # admin username or 'system' for auto-generated
    report_period_start = db.Column(DateTime)  # start of period covered by report
    report_period_end = db.Column(DateTime)  # end of period covered by report
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)  # whether user can access this report
    access_level = db.Column(db.String(32), default='user')  # user, admin, system
    
    def __repr__(self):
        return f'<UserReport {self.username}: {self.report_type}>'
    
    def to_dict(self):
        """Convert report data to dictionary for API responses."""
        return {
            'id': self.id,
            'username': self.username,
            'report_type': self.report_type,
            'report_title': self.report_title,
            'summary': self.summary,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'generated_by': self.generated_by,
            'is_public': self.is_public
        }


class SystemAnalytics(db.Model):
    """
    Platform-wide metrics and performance data for system monitoring.
    
    Tracks key performance indicators including:
    - User engagement metrics
    - Assessment completion rates
    - Learning path effectiveness
    - System performance data
    - Feature usage statistics
    """
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Metric identification
    metric_name = db.Column(db.String(100), nullable=False)  # e.g., 'daily_active_users'
    metric_category = db.Column(db.String(50))  # engagement, performance, learning, etc.
    
    # Metric values
    metric_value = db.Column(db.Float)  # numerical value for simple metrics
    metric_data = db.Column(db.Text)  # JSON string for complex metrics with multiple data points
    
    # Context and metadata
    measurement_period = db.Column(db.String(32))  # daily, weekly, monthly, etc.
    recorded_at = db.Column(DateTime, default=datetime.utcnow)
    data_source = db.Column(db.String(64))  # which agent or system component generated this
    
    # Trend analysis
    previous_value = db.Column(db.Float)  # previous period's value for comparison
    change_percentage = db.Column(db.Float)  # percentage change from previous period
    
    def __repr__(self):
        return f'<SystemAnalytics {self.metric_name}: {self.metric_value}>'
    
    def to_dict(self):
        """Convert analytics data to dictionary for API responses."""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_category': self.metric_category,
            'metric_value': self.metric_value,
            'measurement_period': self.measurement_period,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'change_percentage': self.change_percentage
        }


class Achievement(db.Model):
    """
    Achievement definitions and user achievement tracking.
    
    Note: This overlaps with UserAchievement in the main models but provides
    additional administrative functionality for managing achievement systems.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    
    # Achievement details
    achievement_type = db.Column(db.String(50), nullable=False)  # category of achievement
    achievement_name = db.Column(db.String(100), nullable=False)  # display name
    achievement_description = db.Column(db.Text)  # detailed description
    
    # Gamification
    points_earned = db.Column(Integer, default=0)  # points awarded
    badge_icon = db.Column(db.String(50))  # icon identifier
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    # Tracking
    earned_at = db.Column(DateTime, default=datetime.utcnow)
    criteria_data = db.Column(db.Text)  # JSON with specific criteria that were met
    
    def __repr__(self):
        return f'<Achievement {self.username}: {self.achievement_name}>'