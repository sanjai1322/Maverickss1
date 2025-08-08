"""
Gamification Agent
==================

Manages points, badges, achievements, leaderboards, and engagement mechanics.
Transforms learning and assessment activities into engaging game-like experiences.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

from .base_agent import BaseAgent, AgentEvent

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    FIRST_STEPS = "first_steps"
    SKILL_MASTER = "skill_master"
    SPEED_DEMON = "speed_demon"
    PERFECTIONIST = "perfectionist"
    CONSISTENT_LEARNER = "consistent_learner"
    CHALLENGER = "challenger"
    MENTOR = "mentor"
    EXPLORER = "explorer"

class BadgeLevel(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class GamificationAgent(BaseAgent):
    """
    Gamification Agent manages all engagement mechanics including points,
    badges, achievements, leaderboards, and progress tracking.
    
    Capabilities:
    - Points system with multipliers and bonuses
    - Achievement tracking and badge awarding
    - Dynamic leaderboards with multiple categories
    - Engagement analytics and insights
    - Reward recommendations and motivation
    """
    
    def __init__(self, event_bus=None):
        super().__init__("GamificationAgent", event_bus)
        
        # Subscribe to relevant events
        self.subscribe_to_event("profile.created")
        self.subscribe_to_event("assessment.completed")
        self.subscribe_to_event("exercise.solution_submitted")
        self.subscribe_to_event("learning.module_completed")
        self.subscribe_to_event("hackathon.submission_made")
        self.subscribe_to_event("user.daily_login")
        
        # Points system configuration
        self.point_values = {
            "profile_created": 100,
            "first_assessment": 200,
            "exercise_completed": 50,
            "perfect_solution": 100,
            "fast_solution": 75,
            "learning_module": 150,
            "hackathon_participation": 300,
            "hackathon_win": 1000,
            "daily_login": 25,
            "weekly_streak": 200,
            "monthly_streak": 500,
            "skill_certification": 400,
            "mentor_activity": 100
        }
        
        # Achievement definitions
        self.achievements = {
            AchievementType.FIRST_STEPS: {
                "name": "First Steps",
                "description": "Complete your first coding exercise",
                "icon": "👶",
                "points": 100,
                "levels": {
                    BadgeLevel.BRONZE: {"requirement": 1, "description": "Complete 1 exercise"},
                    BadgeLevel.SILVER: {"requirement": 10, "description": "Complete 10 exercises"},
                    BadgeLevel.GOLD: {"requirement": 50, "description": "Complete 50 exercises"},
                    BadgeLevel.PLATINUM: {"requirement": 100, "description": "Complete 100 exercises"}
                }
            },
            AchievementType.SKILL_MASTER: {
                "name": "Skill Master",
                "description": "Achieve high proficiency in programming skills",
                "icon": "🎯",
                "points": 200,
                "levels": {
                    BadgeLevel.BRONZE: {"requirement": 80, "description": "Score 80% average"},
                    BadgeLevel.SILVER: {"requirement": 85, "description": "Score 85% average"},
                    BadgeLevel.GOLD: {"requirement": 90, "description": "Score 90% average"},
                    BadgeLevel.PLATINUM: {"requirement": 95, "description": "Score 95% average"}
                }
            },
            AchievementType.SPEED_DEMON: {
                "name": "Speed Demon",
                "description": "Complete exercises quickly and efficiently",
                "icon": "⚡",
                "points": 150,
                "levels": {
                    BadgeLevel.BRONZE: {"requirement": 5, "description": "5 fast completions"},
                    BadgeLevel.SILVER: {"requirement": 15, "description": "15 fast completions"},
                    BadgeLevel.GOLD: {"requirement": 30, "description": "30 fast completions"},
                    BadgeLevel.PLATINUM: {"requirement": 50, "description": "50 fast completions"}
                }
            },
            AchievementType.PERFECTIONIST: {
                "name": "Perfectionist",
                "description": "Achieve perfect scores on multiple exercises",
                "icon": "💎",
                "points": 300,
                "levels": {
                    BadgeLevel.BRONZE: {"requirement": 3, "description": "3 perfect scores"},
                    BadgeLevel.SILVER: {"requirement": 10, "description": "10 perfect scores"},
                    BadgeLevel.GOLD: {"requirement": 25, "description": "25 perfect scores"},
                    BadgeLevel.PLATINUM: {"requirement": 50, "description": "50 perfect scores"}
                }
            },
            AchievementType.CONSISTENT_LEARNER: {
                "name": "Consistent Learner",
                "description": "Maintain daily learning streaks",
                "icon": "🔥",
                "points": 250,
                "levels": {
                    BadgeLevel.BRONZE: {"requirement": 7, "description": "7-day streak"},
                    BadgeLevel.SILVER: {"requirement": 30, "description": "30-day streak"},
                    BadgeLevel.GOLD: {"requirement": 90, "description": "90-day streak"},
                    BadgeLevel.PLATINUM: {"requirement": 365, "description": "365-day streak"}
                }
            },
            AchievementType.CHALLENGER: {
                "name": "Challenger",
                "description": "Participate and excel in coding challenges",
                "icon": "🏆",
                "points": 400,
                "levels": {
                    BadgeLevel.BRONZE: {"requirement": 1, "description": "Complete 1 hackathon"},
                    BadgeLevel.SILVER: {"requirement": 5, "description": "Complete 5 hackathons"},
                    BadgeLevel.GOLD: {"requirement": 10, "description": "Win 3 hackathons"},
                    BadgeLevel.PLATINUM: {"requirement": 20, "description": "Win 10 hackathons"}
                }
            }
        }
        
        # Leaderboard categories
        self.leaderboard_categories = [
            "total_points",
            "monthly_points", 
            "assessment_scores",
            "exercise_completion",
            "hackathon_wins",
            "learning_streaks",
            "skill_certifications"
        ]
    
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process gamification-related events"""
        try:
            if event.event_type == "profile.created":
                return self._handle_profile_created(event)
            elif event.event_type == "assessment.completed":
                return self._handle_assessment_completed(event)
            elif event.event_type == "exercise.solution_submitted":
                return self._handle_exercise_completed(event)
            elif event.event_type == "learning.module_completed":
                return self._handle_learning_progress(event)
            elif event.event_type == "hackathon.submission_made":
                return self._handle_hackathon_participation(event)
            elif event.event_type == "user.daily_login":
                return self._handle_daily_login(event)
            else:
                self.logger.warning(f"Unhandled event type: {event.event_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {str(e)}")
            return {"error": str(e)}
    
    def _handle_profile_created(self, event: AgentEvent) -> Dict[str, Any]:
        """Initialize gamification profile for new user"""
        user_id = event.user_id
        
        # Initialize user gamification state
        gamification_state = {
            "user_id": user_id,
            "total_points": 0,
            "level": 1,
            "experience": 0,
            "badges": [],
            "achievements": {},
            "streaks": {
                "current_daily": 0,
                "longest_daily": 0,
                "last_activity": None
            },
            "statistics": {
                "exercises_completed": 0,
                "assessments_taken": 0,
                "hackathons_participated": 0,
                "perfect_scores": 0,
                "fast_completions": 0,
                "total_study_time": 0
            },
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Award welcome points
        points_earned = self.point_values["profile_created"]
        gamification_state["total_points"] = points_earned
        gamification_state["experience"] = points_earned
        
        self.update_state(user_id, gamification_state)
        
        # Emit gamification initialized event
        self.emit_event(
            "gamification.initialized",
            None,
            user_id,
            {
                "initial_points": points_earned,
                "level": 1,
                "available_achievements": len(self.achievements)
            }
        )
        
        return {
            "status": "gamification_initialized",
            "points_earned": points_earned,
            "current_level": 1
        }
    
    def _handle_assessment_completed(self, event: AgentEvent) -> Dict[str, Any]:
        """Process assessment completion for points and achievements"""
        user_id = event.user_id
        payload = event.payload
        
        final_results = payload.get("final_results", {})
        average_score = final_results.get("average_score", 0)
        
        gamification_state = self.get_state(user_id)
        if not gamification_state:
            return {"error": "Gamification profile not found"}
        
        # Calculate points based on performance
        base_points = self.point_values["first_assessment"]
        performance_multiplier = 1.0
        
        if average_score >= 90:
            performance_multiplier = 2.0
        elif average_score >= 80:
            performance_multiplier = 1.5
        elif average_score >= 70:
            performance_multiplier = 1.2
        
        points_earned = int(base_points * performance_multiplier)
        
        # Update statistics
        gamification_state["total_points"] += points_earned
        gamification_state["experience"] += points_earned
        gamification_state["statistics"]["assessments_taken"] += 1
        
        # Check for achievements
        new_achievements = self._check_achievements(user_id, "assessment", {
            "score": average_score,
            "assessments_count": gamification_state["statistics"]["assessments_taken"]
        })
        
        # Update level
        new_level = self._calculate_level(gamification_state["experience"])
        level_up = new_level > gamification_state["level"]
        gamification_state["level"] = new_level
        
        self.update_state(user_id, gamification_state)
        
        # Emit points awarded event
        self.emit_event(
            "points.awarded",
            None,
            user_id,
            {
                "points_earned": points_earned,
                "reason": "assessment_completed",
                "performance_multiplier": performance_multiplier,
                "new_total": gamification_state["total_points"],
                "level_up": level_up,
                "new_level": new_level,
                "new_achievements": new_achievements
            }
        )
        
        return {
            "points_earned": points_earned,
            "new_achievements": new_achievements,
            "level_up": level_up,
            "current_level": new_level
        }
    
    def _handle_exercise_completed(self, event: AgentEvent) -> Dict[str, Any]:
        """Process exercise completion for points and achievements"""
        user_id = event.user_id
        payload = event.payload
        
        solution_result = payload.get("evaluation_result", {})
        score = solution_result.get("score", 0)
        completion_time = payload.get("completion_time", 30)  # minutes
        
        gamification_state = self.get_state(user_id)
        if not gamification_state:
            return {"error": "Gamification profile not found"}
        
        # Calculate points
        base_points = self.point_values["exercise_completed"]
        bonus_points = 0
        
        # Perfect score bonus
        if score >= 100:
            bonus_points += self.point_values["perfect_solution"]
            gamification_state["statistics"]["perfect_scores"] += 1
        
        # Speed bonus (completed in under 15 minutes)
        if completion_time < 15:
            bonus_points += self.point_values["fast_solution"]
            gamification_state["statistics"]["fast_completions"] += 1
        
        total_points = base_points + bonus_points
        
        # Update statistics
        gamification_state["total_points"] += total_points
        gamification_state["experience"] += total_points
        gamification_state["statistics"]["exercises_completed"] += 1
        
        # Update daily streak
        self._update_daily_streak(gamification_state)
        
        # Check for achievements
        achievement_data = {
            "exercises_count": gamification_state["statistics"]["exercises_completed"],
            "perfect_scores": gamification_state["statistics"]["perfect_scores"],
            "fast_completions": gamification_state["statistics"]["fast_completions"],
            "average_score": score
        }
        new_achievements = self._check_achievements(user_id, "exercise", achievement_data)
        
        # Update level
        new_level = self._calculate_level(gamification_state["experience"])
        level_up = new_level > gamification_state["level"]
        gamification_state["level"] = new_level
        
        self.update_state(user_id, gamification_state)
        
        return {
            "points_earned": total_points,
            "bonus_points": bonus_points,
            "new_achievements": new_achievements,
            "level_up": level_up,
            "streak_updated": True
        }
    
    def _handle_learning_progress(self, event: AgentEvent) -> Dict[str, Any]:
        """Process learning module completion"""
        user_id = event.user_id
        
        gamification_state = self.get_state(user_id)
        if not gamification_state:
            return {"error": "Gamification profile not found"}
        
        points_earned = self.point_values["learning_module"]
        
        gamification_state["total_points"] += points_earned
        gamification_state["experience"] += points_earned
        
        self.update_state(user_id, gamification_state)
        
        return {"points_earned": points_earned}
    
    def _handle_hackathon_participation(self, event: AgentEvent) -> Dict[str, Any]:
        """Process hackathon participation and results"""
        user_id = event.user_id
        payload = event.payload
        
        position = payload.get("position", 0)  # 1st, 2nd, 3rd place, etc.
        
        gamification_state = self.get_state(user_id)
        if not gamification_state:
            return {"error": "Gamification profile not found"}
        
        # Base participation points
        points_earned = self.point_values["hackathon_participation"]
        
        # Winning bonus
        if position == 1:
            points_earned += self.point_values["hackathon_win"]
        elif position <= 3:
            points_earned += self.point_values["hackathon_win"] // 2
        
        gamification_state["total_points"] += points_earned
        gamification_state["experience"] += points_earned
        gamification_state["statistics"]["hackathons_participated"] += 1
        
        # Check challenger achievements
        new_achievements = self._check_achievements(user_id, "hackathon", {
            "hackathons_count": gamification_state["statistics"]["hackathons_participated"],
            "position": position
        })
        
        self.update_state(user_id, gamification_state)
        
        return {
            "points_earned": points_earned,
            "new_achievements": new_achievements
        }
    
    def _handle_daily_login(self, event: AgentEvent) -> Dict[str, Any]:
        """Process daily login for streak tracking"""
        user_id = event.user_id
        
        gamification_state = self.get_state(user_id)
        if not gamification_state:
            return {"error": "Gamification profile not found"}
        
        # Update daily streak
        streak_updated = self._update_daily_streak(gamification_state)
        
        points_earned = self.point_values["daily_login"]
        
        # Streak bonuses
        current_streak = gamification_state["streaks"]["current_daily"]
        if current_streak % 7 == 0 and current_streak > 0:  # Weekly streak
            points_earned += self.point_values["weekly_streak"]
        if current_streak % 30 == 0 and current_streak > 0:  # Monthly streak
            points_earned += self.point_values["monthly_streak"]
        
        gamification_state["total_points"] += points_earned
        gamification_state["experience"] += points_earned
        
        self.update_state(user_id, gamification_state)
        
        return {
            "points_earned": points_earned,
            "current_streak": current_streak,
            "streak_updated": streak_updated
        }
    
    def _check_achievements(self, user_id: str, activity_type: str, 
                          data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check and award new achievements"""
        new_achievements = []
        gamification_state = self.get_state(user_id)
        
        if not gamification_state:
            return new_achievements
        
        for achievement_type, achievement_config in self.achievements.items():
            # Check if user already has this achievement at any level
            user_achievements = gamification_state.get("achievements", {})
            current_level = user_achievements.get(achievement_type.value)
            
            # Determine what level user qualifies for
            qualified_level = None
            
            if achievement_type == AchievementType.FIRST_STEPS and activity_type == "exercise":
                exercises_count = data.get("exercises_count", 0)
                qualified_level = self._get_qualified_level(achievement_config["levels"], exercises_count)
            
            elif achievement_type == AchievementType.SKILL_MASTER and activity_type == "assessment":
                avg_score = data.get("score", 0)
                qualified_level = self._get_qualified_level(achievement_config["levels"], avg_score)
            
            elif achievement_type == AchievementType.SPEED_DEMON and activity_type == "exercise":
                fast_completions = data.get("fast_completions", 0)
                qualified_level = self._get_qualified_level(achievement_config["levels"], fast_completions)
            
            elif achievement_type == AchievementType.PERFECTIONIST and activity_type == "exercise":
                perfect_scores = data.get("perfect_scores", 0)
                qualified_level = self._get_qualified_level(achievement_config["levels"], perfect_scores)
            
            elif achievement_type == AchievementType.CHALLENGER and activity_type == "hackathon":
                hackathons_count = data.get("hackathons_count", 0)
                qualified_level = self._get_qualified_level(achievement_config["levels"], hackathons_count)
            
            # Award achievement if user qualifies and doesn't already have it at this level
            if qualified_level and (not current_level or self._is_level_higher(qualified_level, current_level)):
                # Award the achievement
                new_achievement = {
                    "type": achievement_type.value,
                    "name": achievement_config["name"],
                    "description": achievement_config["description"],
                    "icon": achievement_config["icon"],
                    "level": qualified_level.value,
                    "level_description": achievement_config["levels"][qualified_level]["description"],
                    "points": achievement_config["points"],
                    "earned_at": datetime.utcnow().isoformat()
                }
                
                new_achievements.append(new_achievement)
                
                # Update user's achievements
                gamification_state["achievements"][achievement_type.value] = qualified_level.value
                
                # Award achievement points
                gamification_state["total_points"] += achievement_config["points"]
                gamification_state["experience"] += achievement_config["points"]
        
        return new_achievements
    
    def _get_qualified_level(self, levels: Dict[BadgeLevel, Dict[str, Any]], 
                           value: float) -> Optional[BadgeLevel]:
        """Determine the highest level user qualifies for"""
        qualified_level = None
        
        for level, requirements in levels.items():
            if value >= requirements["requirement"]:
                qualified_level = level
        
        return qualified_level
    
    def _is_level_higher(self, new_level: BadgeLevel, current_level: str) -> bool:
        """Check if new level is higher than current level"""
        level_hierarchy = [BadgeLevel.BRONZE, BadgeLevel.SILVER, BadgeLevel.GOLD, BadgeLevel.PLATINUM]
        
        try:
            current_badge_level = BadgeLevel(current_level)
            return level_hierarchy.index(new_level) > level_hierarchy.index(current_badge_level)
        except ValueError:
            return True  # If current level is invalid, award new level
    
    def _update_daily_streak(self, gamification_state: Dict[str, Any]) -> bool:
        """Update daily login streak"""
        today = datetime.utcnow().date()
        last_activity = gamification_state["streaks"].get("last_activity")
        
        if last_activity:
            last_activity_date = datetime.fromisoformat(last_activity).date()
            
            if last_activity_date == today:
                return False  # Already updated today
            elif last_activity_date == today - timedelta(days=1):
                # Continue streak
                gamification_state["streaks"]["current_daily"] += 1
            else:
                # Streak broken
                gamification_state["streaks"]["current_daily"] = 1
        else:
            # First activity
            gamification_state["streaks"]["current_daily"] = 1
        
        # Update longest streak
        current_streak = gamification_state["streaks"]["current_daily"]
        if current_streak > gamification_state["streaks"]["longest_daily"]:
            gamification_state["streaks"]["longest_daily"] = current_streak
        
        gamification_state["streaks"]["last_activity"] = datetime.utcnow().isoformat()
        return True
    
    def _calculate_level(self, experience: int) -> int:
        """Calculate user level based on experience points"""
        # Level formula: Level = floor(sqrt(experience / 100))
        import math
        return max(1, math.floor(math.sqrt(experience / 100)))
    
    def get_leaderboard(self, category: str = "total_points", 
                       limit: int = 50) -> List[Dict[str, Any]]:
        """Get leaderboard for specified category"""
        if category not in self.leaderboard_categories:
            category = "total_points"
        
        # Get all user states
        leaderboard_data = []
        
        for user_id, state in self.state.items():
            if category == "total_points":
                score = state.get("total_points", 0)
            elif category == "monthly_points":
                # This would require tracking monthly points separately
                score = state.get("total_points", 0)  # Simplified
            elif category == "exercise_completion":
                score = state.get("statistics", {}).get("exercises_completed", 0)
            elif category == "hackathon_wins":
                score = state.get("statistics", {}).get("hackathon_wins", 0)
            else:
                score = state.get("total_points", 0)
            
            leaderboard_data.append({
                "user_id": user_id,
                "score": score,
                "level": state.get("level", 1),
                "badges_count": len(state.get("achievements", {})),
                "streak": state.get("streaks", {}).get("current_daily", 0)
            })
        
        # Sort by score descending
        leaderboard_data.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rankings
        for i, entry in enumerate(leaderboard_data[:limit]):
            entry["rank"] = i + 1
        
        return leaderboard_data[:limit]
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get complete gamification profile for user"""
        state = self.get_state(user_id)
        if not state:
            return {"error": "User profile not found"}
        
        # Add derived metrics
        profile = state.copy()
        profile["next_level_exp"] = ((profile.get("level", 1) + 1) ** 2) * 100
        profile["exp_to_next_level"] = profile["next_level_exp"] - profile.get("experience", 0)
        
        # Get user's rank
        leaderboard = self.get_leaderboard("total_points", 1000)
        user_rank = next((entry["rank"] for entry in leaderboard if entry["user_id"] == user_id), None)
        profile["global_rank"] = user_rank
        
        return profile
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": "GamificationAgent",
            "version": "1.0.0",
            "capabilities": [
                "points_system",
                "achievement_tracking",
                "badge_management", 
                "leaderboards",
                "streak_tracking",
                "level_progression",
                "engagement_analytics"
            ],
            "point_values": self.point_values,
            "achievement_types": [achievement.value for achievement in AchievementType],
            "badge_levels": [level.value for level in BadgeLevel],
            "leaderboard_categories": self.leaderboard_categories,
            "supported_events": [
                "profile.created",
                "assessment.completed",
                "exercise.solution_submitted", 
                "learning.module_completed",
                "hackathon.submission_made",
                "user.daily_login"
            ],
            "emitted_events": [
                "gamification.initialized",
                "points.awarded",
                "achievement.earned",
                "level.increased",
                "streak.updated"
            ]
        }