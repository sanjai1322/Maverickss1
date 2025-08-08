from app import db
from sqlalchemy import DateTime
from datetime import datetime


class AdminUser(db.Model):
    """Admin user model for admin dashboard access."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_login = db.Column(DateTime)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'


class UserReport(db.Model):
    """Generated reports for users and admins."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    report_type = db.Column(db.String(50))  # progress, skills, assessment, learning_path
    report_data = db.Column(db.Text)  # JSON string with report details
    generated_at = db.Column(DateTime, default=datetime.utcnow)
    generated_by = db.Column(db.String(64))  # admin username or system
    
    def __repr__(self):
        return f'<UserReport {self.username}: {self.report_type}>'


class SystemAnalytics(db.Model):
    """System-wide analytics and metrics."""
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float)
    metric_data = db.Column(db.Text)  # JSON string for complex metrics
    recorded_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemAnalytics {self.metric_name}: {self.metric_value}>'


class UserActivity(db.Model):
    """Track detailed user activities for analytics."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    activity_type = db.Column(db.String(50))  # login, profile_update, assessment_start, etc.
    activity_details = db.Column(db.Text)  # JSON string with activity details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserActivity {self.username}: {self.activity_type}>'


class Achievement(db.Model):
    """User achievements and badges."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), db.ForeignKey('user.username'), nullable=False)
    achievement_type = db.Column(db.String(50))  # first_assessment, skill_master, fast_learner, etc.
    achievement_name = db.Column(db.String(100))
    achievement_description = db.Column(db.Text)
    points_earned = db.Column(db.Integer, default=0)
    earned_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.username}: {self.achievement_name}>'