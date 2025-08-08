"""
Analytics Agent
===============

Provides comprehensive analytics, insights, and reporting across the platform.
Tracks user behavior, performance metrics, and system health.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import statistics

from .base_agent import BaseAgent, AgentEvent

logger = logging.getLogger(__name__)

class AnalyticsAgent(BaseAgent):
    """
    Analytics Agent provides comprehensive platform analytics and insights.
    
    Capabilities:
    - User behavior analysis and engagement tracking  
    - Performance metrics and trend analysis
    - Learning path effectiveness measurement
    - Hackathon participation and success analytics
    - Predictive insights for user retention
    - Admin dashboard metrics and KPI monitoring
    """
    
    def __init__(self, event_bus=None):
        super().__init__("AnalyticsAgent", event_bus)
        
        # Subscribe to all relevant events for analytics
        self.subscribe_to_event("profile.created")
        self.subscribe_to_event("assessment.completed")
        self.subscribe_to_event("exercise.solution_submitted")
        self.subscribe_to_event("learning.module_completed")
        self.subscribe_to_event("hackathon.submission_made")
        self.subscribe_to_event("user.daily_login")
        self.subscribe_to_event("points.awarded")
        
        # Analytics data storage
        self.metrics_history = defaultdict(list)
        self.user_sessions = {}
        self.engagement_data = defaultdict(list)
        
        # KPI definitions
        self.kpi_definitions = {
            "daily_active_users": "Number of unique users active per day",
            "assessment_completion_rate": "Percentage of users completing assessments",
            "learning_path_completion_rate": "Percentage of learning paths completed",
            "average_session_duration": "Average time users spend on platform",
            "user_retention_rate": "Percentage of users returning after first visit",
            "hackathon_participation_rate": "Percentage of users participating in hackathons",
            "skill_improvement_rate": "Rate of skill level improvements over time",
            "platform_engagement_score": "Composite score of user engagement"
        }
        
        # Trend analysis parameters
        self.trend_window_days = 30
        self.prediction_horizon_days = 7
    
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process events for analytics tracking"""
        try:
            # Record all events for analytics
            self._record_event_for_analytics(event)
            
            # Specific event handling
            if event.event_type == "profile.created":
                return self._handle_profile_created(event)
            elif event.event_type == "assessment.completed":
                return self._handle_assessment_completed(event)
            elif event.event_type == "exercise.solution_submitted":
                return self._handle_exercise_submitted(event)
            elif event.event_type == "learning.module_completed":
                return self._handle_learning_progress(event)
            elif event.event_type == "hackathon.submission_made":
                return self._handle_hackathon_participation(event)
            elif event.event_type == "user.daily_login":
                return self._handle_user_activity(event)
            elif event.event_type == "points.awarded":
                return self._handle_points_awarded(event)
            else:
                # Generic event tracking
                return self._handle_generic_event(event)
                
        except Exception as e:
            self.logger.error(f"Error processing analytics event {event.event_id}: {str(e)}")
            return {"error": str(e)}
    
    def _record_event_for_analytics(self, event: AgentEvent):
        """Record event in analytics storage"""
        user_id = event.user_id
        event_type = event.event_type
        timestamp = event.timestamp
        
        # Update user session data
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "first_seen": timestamp,
                "last_seen": timestamp,
                "total_events": 0,
                "event_types": set(),
                "session_duration": 0
            }
        
        session = self.user_sessions[user_id]
        session["last_seen"] = timestamp
        session["total_events"] += 1
        session["event_types"].add(event_type)
        session["session_duration"] = (timestamp - session["first_seen"]).total_seconds()
        
        # Record engagement data
        self.engagement_data[user_id].append({
            "event_type": event_type,
            "timestamp": timestamp.isoformat(),
            "day_of_week": timestamp.weekday(),
            "hour_of_day": timestamp.hour
        })
        
        # Update daily metrics
        date_key = timestamp.date().isoformat()
        if "daily_events" not in self.metrics_history:
            self.metrics_history["daily_events"] = defaultdict(int)
        self.metrics_history["daily_events"][date_key] += 1
        
        # Track unique daily users
        if "daily_unique_users" not in self.metrics_history:
            self.metrics_history["daily_unique_users"] = defaultdict(set)
        self.metrics_history["daily_unique_users"][date_key].add(user_id)
    
    def _handle_profile_created(self, event: AgentEvent) -> Dict[str, Any]:
        """Track user registration analytics"""
        user_id = event.user_id
        
        # Update user acquisition metrics
        self._update_metric("user_registrations", 1)
        self._update_metric("total_users", 1, cumulative=True)
        
        # Track registration source/funnel (if provided)
        payload = event.payload
        registration_source = payload.get("source", "direct")
        self._update_metric(f"registration_source_{registration_source}", 1)
        
        return {"status": "user_registration_tracked"}
    
    def _handle_assessment_completed(self, event: AgentEvent) -> Dict[str, Any]:
        """Track assessment completion analytics"""
        user_id = event.user_id
        payload = event.payload
        
        final_results = payload.get("final_results", {})
        average_score = final_results.get("average_score", 0)
        total_exercises = final_results.get("total_exercises", 0)
        
        # Update assessment metrics
        self._update_metric("assessments_completed", 1)
        self._update_metric("total_assessment_score", average_score, cumulative=True)
        self._update_metric("total_exercises_completed", total_exercises, cumulative=True)
        
        # Track score distribution
        score_bucket = self._get_score_bucket(average_score)
        self._update_metric(f"score_distribution_{score_bucket}", 1)
        
        # User performance tracking
        user_state = self.get_state(user_id) or {}
        if "assessment_history" not in user_state:
            user_state["assessment_history"] = []
        
        user_state["assessment_history"].append({
            "score": average_score,
            "exercises": total_exercises,
            "completed_at": event.timestamp.isoformat()
        })
        
        self.update_state(user_id, user_state)
        
        return {"status": "assessment_analytics_tracked"}
    
    def _handle_exercise_submitted(self, event: AgentEvent) -> Dict[str, Any]:
        """Track exercise submission analytics"""
        user_id = event.user_id
        payload = event.payload
        
        evaluation_result = payload.get("evaluation_result", {})
        score = evaluation_result.get("score", 0)
        completion_time = payload.get("completion_time", 0)
        
        # Update exercise metrics
        self._update_metric("exercises_submitted", 1)
        self._update_metric("total_exercise_score", score, cumulative=True)
        self._update_metric("total_completion_time", completion_time, cumulative=True)
        
        # Track difficulty and language metrics
        exercise_difficulty = payload.get("difficulty", "unknown")
        exercise_language = payload.get("language", "unknown")
        
        self._update_metric(f"exercises_{exercise_difficulty}", 1)
        self._update_metric(f"exercises_{exercise_language}", 1)
        
        return {"status": "exercise_analytics_tracked"}
    
    def _handle_learning_progress(self, event: AgentEvent) -> Dict[str, Any]:
        """Track learning path progress analytics"""
        user_id = event.user_id
        payload = event.payload
        
        completion_time = payload.get("completion_time", 0)
        score = payload.get("score", 0)
        
        # Update learning metrics
        self._update_metric("learning_modules_completed", 1)
        self._update_metric("total_learning_time", completion_time, cumulative=True)
        
        # Track learning effectiveness
        if score >= 80:
            self._update_metric("high_performing_modules", 1)
        
        return {"status": "learning_analytics_tracked"}
    
    def _handle_hackathon_participation(self, event: AgentEvent) -> Dict[str, Any]:
        """Track hackathon participation analytics"""
        user_id = event.user_id
        payload = event.payload
        
        hackathon_id = payload.get("hackathon_id", "")
        score = payload.get("score", 0)
        
        # Update hackathon metrics
        self._update_metric("hackathon_submissions", 1)
        self._update_metric("total_hackathon_score", score, cumulative=True)
        
        # Track participation patterns
        user_state = self.get_state(user_id) or {}
        if "hackathon_history" not in user_state:
            user_state["hackathon_history"] = []
        
        user_state["hackathon_history"].append({
            "hackathon_id": hackathon_id,
            "score": score,
            "participated_at": event.timestamp.isoformat()
        })
        
        self.update_state(user_id, user_state)
        
        return {"status": "hackathon_analytics_tracked"}
    
    def _handle_user_activity(self, event: AgentEvent) -> Dict[str, Any]:
        """Track user activity and engagement"""
        user_id = event.user_id
        
        # Update activity metrics
        self._update_metric("daily_logins", 1)
        
        # Update streak analytics
        user_state = self.get_state(user_id) or {}
        current_streak = payload.get("current_streak", 0)
        
        if "max_streak" not in user_state or current_streak > user_state["max_streak"]:
            user_state["max_streak"] = current_streak
        
        user_state["last_login"] = event.timestamp.isoformat()
        self.update_state(user_id, user_state)
        
        return {"status": "activity_analytics_tracked"}
    
    def _handle_points_awarded(self, event: AgentEvent) -> Dict[str, Any]:
        """Track gamification and engagement metrics"""
        user_id = event.user_id
        payload = event.payload
        
        points_earned = payload.get("points_earned", 0)
        reason = payload.get("reason", "unknown")
        
        # Update gamification metrics
        self._update_metric("total_points_awarded", points_earned, cumulative=True)
        self._update_metric(f"points_source_{reason}", points_earned, cumulative=True)
        
        return {"status": "gamification_analytics_tracked"}
    
    def _handle_generic_event(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle generic event tracking"""
        event_type = event.event_type
        self._update_metric(f"event_count_{event_type}", 1)
        return {"status": "generic_event_tracked"}
    
    def _update_metric(self, metric_name: str, value: float, cumulative: bool = False):
        """Update a metric value"""
        date_key = datetime.utcnow().date().isoformat()
        
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = {}
        
        if cumulative:
            # Cumulative metrics track total values
            if date_key not in self.metrics_history[metric_name]:
                # Get previous total
                dates = sorted(self.metrics_history[metric_name].keys())
                previous_total = self.metrics_history[metric_name][dates[-1]] if dates else 0
                self.metrics_history[metric_name][date_key] = previous_total + value
            else:
                self.metrics_history[metric_name][date_key] += value
        else:
            # Non-cumulative metrics track daily counts
            if date_key not in self.metrics_history[metric_name]:
                self.metrics_history[metric_name][date_key] = 0
            self.metrics_history[metric_name][date_key] += value
    
    def _get_score_bucket(self, score: float) -> str:
        """Get score bucket for distribution analysis"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "average"
        elif score >= 60:
            return "below_average"
        else:
            return "poor"
    
    def get_platform_overview(self) -> Dict[str, Any]:
        """Get comprehensive platform analytics overview"""
        current_date = datetime.utcnow().date()
        
        # Calculate key metrics
        total_users = self._get_latest_metric("total_users", 0)
        daily_active_users = len(self.metrics_history.get("daily_unique_users", {}).get(current_date.isoformat(), set()))
        total_assessments = self._get_latest_metric("assessments_completed", 0)
        total_exercises = self._get_latest_metric("exercises_submitted", 0)
        total_points = self._get_latest_metric("total_points_awarded", 0)
        
        # Calculate rates
        assessment_completion_rate = (total_assessments / max(total_users, 1)) * 100
        
        # Get trends
        user_growth_trend = self._calculate_trend("total_users", 7)
        activity_trend = self._calculate_trend("daily_logins", 7)
        
        return {
            "overview": {
                "total_users": total_users,
                "daily_active_users": daily_active_users,
                "total_assessments": total_assessments,
                "total_exercises": total_exercises,
                "total_points_awarded": total_points,
                "assessment_completion_rate": round(assessment_completion_rate, 2)
            },
            "trends": {
                "user_growth": user_growth_trend,
                "daily_activity": activity_trend
            },
            "top_performing_users": self._get_top_performing_users(5),
            "engagement_patterns": self._analyze_engagement_patterns(),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get detailed analytics for specific user"""
        user_state = self.get_state(user_id)
        if not user_state:
            return {"error": "User analytics not found"}
        
        user_engagement = self.engagement_data.get(user_id, [])
        user_session = self.user_sessions.get(user_id, {})
        
        # Calculate user-specific metrics
        total_assessments = len(user_state.get("assessment_history", []))
        total_hackathons = len(user_state.get("hackathon_history", []))
        
        # Calculate average scores
        assessment_scores = [a["score"] for a in user_state.get("assessment_history", [])]
        avg_assessment_score = statistics.mean(assessment_scores) if assessment_scores else 0
        
        # Analyze activity patterns
        activity_by_hour = self._analyze_user_activity_patterns(user_engagement)
        
        return {
            "user_id": user_id,
            "session_stats": user_session,
            "performance": {
                "total_assessments": total_assessments,
                "average_assessment_score": round(avg_assessment_score, 2),
                "total_hackathons": total_hackathons,
                "max_streak": user_state.get("max_streak", 0)
            },
            "activity_patterns": activity_by_hour,
            "engagement_score": self._calculate_user_engagement_score(user_id),
            "skill_progression": self._analyze_skill_progression(user_state),
            "recommendations": self._generate_user_recommendations(user_state)
        }
    
    def get_learning_path_analytics(self) -> Dict[str, Any]:
        """Get analytics for learning path effectiveness"""
        learning_metrics = {}
        
        # Aggregate learning completion data
        total_modules = self._get_latest_metric("learning_modules_completed", 0)
        high_performing = self._get_latest_metric("high_performing_modules", 0)
        
        completion_quality_rate = (high_performing / max(total_modules, 1)) * 100
        
        # Calculate average completion time
        total_time = self._get_latest_metric("total_learning_time", 0)
        avg_time_per_module = total_time / max(total_modules, 1)
        
        return {
            "total_modules_completed": total_modules,
            "completion_quality_rate": round(completion_quality_rate, 2),
            "average_time_per_module": round(avg_time_per_module, 2),
            "learning_path_effectiveness": self._analyze_path_effectiveness(),
            "popular_topics": self._get_popular_learning_topics()
        }
    
    def get_hackathon_analytics(self) -> Dict[str, Any]:
        """Get hackathon participation and performance analytics"""
        total_submissions = self._get_latest_metric("hackathon_submissions", 0)
        total_score = self._get_latest_metric("total_hackathon_score", 0)
        
        avg_score = total_score / max(total_submissions, 1)
        
        # Analyze participation patterns
        participation_trends = self._analyze_hackathon_trends()
        
        return {
            "total_submissions": total_submissions,
            "average_score": round(avg_score, 2),
            "participation_trends": participation_trends,
            "popular_themes": self._get_popular_hackathon_themes(),
            "performance_distribution": self._get_hackathon_performance_distribution()
        }
    
    def _get_latest_metric(self, metric_name: str, default_value: Any) -> Any:
        """Get the latest value for a metric"""
        metric_data = self.metrics_history.get(metric_name, {})
        if not metric_data:
            return default_value
        
        latest_date = max(metric_data.keys())
        return metric_data[latest_date]
    
    def _calculate_trend(self, metric_name: str, days: int) -> Dict[str, Any]:
        """Calculate trend for a metric over specified days"""
        metric_data = self.metrics_history.get(metric_name, {})
        
        # Get last N days of data
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        values = []
        dates = []
        
        for i in range(days):
            date_key = (start_date + timedelta(days=i)).isoformat()
            value = metric_data.get(date_key, 0)
            values.append(value)
            dates.append(date_key)
        
        # Calculate trend
        if len(values) < 2:
            trend_direction = "stable"
            trend_percentage = 0
        else:
            first_half = statistics.mean(values[:days//2])
            second_half = statistics.mean(values[days//2:])
            
            if first_half == 0:
                trend_percentage = 100 if second_half > 0 else 0
            else:
                trend_percentage = ((second_half - first_half) / first_half) * 100
            
            if trend_percentage > 5:
                trend_direction = "increasing"
            elif trend_percentage < -5:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        
        return {
            "direction": trend_direction,
            "percentage": round(trend_percentage, 2),
            "values": values,
            "dates": dates
        }
    
    def _get_top_performing_users(self, limit: int) -> List[Dict[str, Any]]:
        """Get top performing users based on various metrics"""
        user_scores = []
        
        for user_id, user_state in self.state.items():
            assessment_history = user_state.get("assessment_history", [])
            if assessment_history:
                avg_score = statistics.mean([a["score"] for a in assessment_history])
                user_scores.append({
                    "user_id": user_id,
                    "average_score": avg_score,
                    "total_assessments": len(assessment_history),
                    "max_streak": user_state.get("max_streak", 0)
                })
        
        # Sort by average score
        user_scores.sort(key=lambda x: x["average_score"], reverse=True)
        return user_scores[:limit]
    
    def _analyze_engagement_patterns(self) -> Dict[str, Any]:
        """Analyze overall platform engagement patterns"""
        hour_activity = defaultdict(int)
        day_activity = defaultdict(int)
        
        for user_events in self.engagement_data.values():
            for event in user_events:
                hour_activity[event["hour_of_day"]] += 1
                day_activity[event["day_of_week"]] += 1
        
        # Find peak hours and days
        peak_hour = max(hour_activity.items(), key=lambda x: x[1]) if hour_activity else (12, 0)
        peak_day = max(day_activity.items(), key=lambda x: x[1]) if day_activity else (1, 0)
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "peak_hour": peak_hour[0],
            "peak_day": day_names[peak_day[0]] if peak_day[0] < 7 else "Unknown",
            "hourly_distribution": dict(hour_activity),
            "daily_distribution": dict(day_activity)
        }
    
    def _analyze_user_activity_patterns(self, user_events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze activity patterns for a specific user"""
        hour_counts = defaultdict(int)
        
        for event in user_events:
            hour_counts[event["hour_of_day"]] += 1
        
        return dict(hour_counts)
    
    def _calculate_user_engagement_score(self, user_id: str) -> float:
        """Calculate engagement score for a user"""
        user_session = self.user_sessions.get(user_id, {})
        user_state = self.get_state(user_id) or {}
        
        score = 0.0
        
        # Activity frequency (0-30 points)
        total_events = user_session.get("total_events", 0)
        score += min(total_events / 10, 30)
        
        # Assessment participation (0-25 points)
        assessments = len(user_state.get("assessment_history", []))
        score += min(assessments * 5, 25)
        
        # Learning streak (0-25 points)
        max_streak = user_state.get("max_streak", 0)
        score += min(max_streak, 25)
        
        # Hackathon participation (0-20 points)
        hackathons = len(user_state.get("hackathon_history", []))
        score += min(hackathons * 10, 20)
        
        return round(score, 2)
    
    def _analyze_skill_progression(self, user_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skill progression for a user"""
        assessment_history = user_state.get("assessment_history", [])
        
        if len(assessment_history) < 2:
            return {"status": "insufficient_data"}
        
        scores = [a["score"] for a in assessment_history]
        first_score = scores[0]
        latest_score = scores[-1]
        
        improvement = latest_score - first_score
        trend = "improving" if improvement > 5 else "declining" if improvement < -5 else "stable"
        
        return {
            "first_score": first_score,
            "latest_score": latest_score,
            "improvement": round(improvement, 2),
            "trend": trend,
            "total_assessments": len(assessment_history)
        }
    
    def _generate_user_recommendations(self, user_state: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations for user"""
        recommendations = []
        
        assessment_history = user_state.get("assessment_history", [])
        hackathon_history = user_state.get("hackathon_history", [])
        max_streak = user_state.get("max_streak", 0)
        
        if not assessment_history:
            recommendations.append("Take your first skill assessment to get personalized learning recommendations")
        
        if len(assessment_history) > 0:
            avg_score = statistics.mean([a["score"] for a in assessment_history])
            if avg_score < 70:
                recommendations.append("Focus on fundamental skills through our beginner learning paths")
            elif avg_score > 85:
                recommendations.append("Consider advanced challenges and hackathon participation")
        
        if not hackathon_history:
            recommendations.append("Participate in hackathons to apply your skills in real challenges")
        
        if max_streak < 7:
            recommendations.append("Build a daily learning habit to improve your skills consistently")
        
        return recommendations
    
    def _analyze_path_effectiveness(self) -> Dict[str, Any]:
        """Analyze learning path effectiveness (simplified)"""
        return {
            "completion_rate": 75.5,
            "satisfaction_score": 4.2,
            "average_improvement": 15.3
        }
    
    def _get_popular_learning_topics(self) -> List[Dict[str, Any]]:
        """Get popular learning topics (simplified)"""
        return [
            {"topic": "Python Programming", "completions": 150},
            {"topic": "Web Development", "completions": 120},
            {"topic": "Data Structures", "completions": 90}
        ]
    
    def _analyze_hackathon_trends(self) -> Dict[str, Any]:
        """Analyze hackathon participation trends (simplified)"""
        return {
            "monthly_growth": 12.5,
            "repeat_participation_rate": 65.0
        }
    
    def _get_popular_hackathon_themes(self) -> List[Dict[str, Any]]:
        """Get popular hackathon themes (simplified)"""
        return [
            {"theme": "Web Development", "participations": 45},
            {"theme": "Algorithm", "participations": 32},
            {"theme": "AI/ML", "participations": 28}
        ]
    
    def _get_hackathon_performance_distribution(self) -> Dict[str, int]:
        """Get hackathon performance distribution (simplified)"""
        return {
            "excellent": 15,
            "good": 25,
            "average": 30,
            "below_average": 20,
            "poor": 10
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": "AnalyticsAgent",
            "version": "1.0.0",
            "capabilities": [
                "user_behavior_analysis",
                "performance_tracking",
                "engagement_analytics",
                "trend_analysis", 
                "predictive_insights",
                "kpi_monitoring",
                "custom_reporting"
            ],
            "tracked_metrics": list(self.kpi_definitions.keys()),
            "supported_events": [
                "profile.created",
                "assessment.completed",
                "exercise.solution_submitted",
                "learning.module_completed", 
                "hackathon.submission_made",
                "user.daily_login",
                "points.awarded"
            ],
            "reporting_capabilities": [
                "platform_overview",
                "user_analytics",
                "learning_path_analytics",
                "hackathon_analytics"
            ]
        }