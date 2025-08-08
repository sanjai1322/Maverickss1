"""
Hackathon Agent
===============

Manages coding competitions, challenges, and hackathon events.
Provides automated scoring, ranking, and challenge generation.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

from .base_agent import BaseAgent, AgentEvent

logger = logging.getLogger(__name__)

class HackathonStatus(Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    JUDGING = "judging" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class HackathonAgent(BaseAgent):
    """
    Hackathon Agent manages coding competitions and challenges.
    
    Capabilities:
    - Dynamic challenge generation based on themes
    - Automated submission evaluation and scoring
    - Real-time leaderboard management
    - Team formation and collaboration features
    - Judge dashboard and manual review system
    """
    
    def __init__(self, event_bus=None):
        super().__init__("HackathonAgent", event_bus)
        
        # Subscribe to events
        self.subscribe_to_event("hackathon.create_requested")
        self.subscribe_to_event("hackathon.submission_made")
        self.subscribe_to_event("hackathon.join_requested")
        self.subscribe_to_event("hackathon.evaluation_completed")
        
        # Challenge templates by difficulty and theme
        self.challenge_templates = {
            "web_development": {
                "beginner": [
                    {
                        "title": "Personal Portfolio Website",
                        "description": "Create a responsive portfolio website showcasing your skills",
                        "requirements": [
                            "Responsive design (mobile-friendly)",
                            "At least 3 sections (about, projects, contact)",
                            "Clean, modern UI design",
                            "Working contact form"
                        ],
                        "judging_criteria": {
                            "functionality": 0.3,
                            "design": 0.3,
                            "code_quality": 0.2,
                            "creativity": 0.2
                        },
                        "time_limit": 180,  # 3 hours
                        "max_score": 100
                    }
                ],
                "intermediate": [
                    {
                        "title": "Task Management App",
                        "description": "Build a full-stack task management application",
                        "requirements": [
                            "User authentication system",
                            "CRUD operations for tasks",
                            "Task filtering and sorting",
                            "Data persistence (database)",
                            "RESTful API design"
                        ],
                        "judging_criteria": {
                            "functionality": 0.35,
                            "architecture": 0.25,
                            "user_experience": 0.2,
                            "code_quality": 0.2
                        },
                        "time_limit": 300,  # 5 hours
                        "max_score": 100
                    }
                ]
            },
            "algorithm": {
                "beginner": [
                    {
                        "title": "Data Structure Implementation",
                        "description": "Implement and optimize common data structures",
                        "requirements": [
                            "Implement at least 3 data structures",
                            "Include time/space complexity analysis",
                            "Comprehensive test cases",
                            "Performance benchmarking"
                        ],
                        "judging_criteria": {
                            "correctness": 0.4,
                            "efficiency": 0.3,
                            "code_quality": 0.2,
                            "documentation": 0.1
                        },
                        "time_limit": 240,  # 4 hours
                        "max_score": 100
                    }
                ]
            },
            "ai_ml": {
                "intermediate": [
                    {
                        "title": "Predictive Analytics Challenge",
                        "description": "Build a machine learning model for prediction",
                        "requirements": [
                            "Data preprocessing and cleaning",
                            "Feature engineering",
                            "Model training and validation",
                            "Performance metrics and evaluation",
                            "Deployment-ready solution"
                        ],
                        "judging_criteria": {
                            "model_accuracy": 0.35,
                            "feature_engineering": 0.25,
                            "code_organization": 0.2,
                            "documentation": 0.2
                        },
                        "time_limit": 360,  # 6 hours
                        "max_score": 100
                    }
                ]
            }
        }
        
        # Active hackathons storage
        self.active_hackathons = {}
        
        # Scoring weights for different aspects
        self.scoring_weights = {
            "automated_tests": 0.4,
            "code_quality": 0.25,
            "creativity": 0.15,
            "documentation": 0.1,
            "presentation": 0.1
        }
    
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process hackathon-related events"""
        try:
            if event.event_type == "hackathon.create_requested":
                return self._handle_hackathon_creation(event)
            elif event.event_type == "hackathon.submission_made":
                return self._handle_submission(event)
            elif event.event_type == "hackathon.join_requested":
                return self._handle_join_request(event)
            elif event.event_type == "hackathon.evaluation_completed":
                return self._handle_evaluation_completed(event)
            else:
                self.logger.warning(f"Unhandled event type: {event.event_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {str(e)}")
            return {"error": str(e)}
    
    def _handle_hackathon_creation(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle hackathon creation request"""
        user_id = event.user_id
        payload = event.payload
        
        # Extract hackathon parameters
        theme = payload.get("theme", "web_development")
        difficulty = payload.get("difficulty", "intermediate") 
        duration_hours = payload.get("duration_hours", 4)
        max_participants = payload.get("max_participants", 50)
        start_time = payload.get("start_time")
        
        # Generate challenge from template
        challenge = self._generate_challenge(theme, difficulty)
        if not challenge:
            return {"error": f"No challenges available for theme: {theme}, difficulty: {difficulty}"}
        
        # Create hackathon instance
        hackathon_id = f"hackathon_{theme}_{int(datetime.utcnow().timestamp())}"
        
        hackathon = {
            "id": hackathon_id,
            "title": f"{theme.replace('_', ' ').title()} Challenge",
            "description": f"A {difficulty} level {theme.replace('_', ' ')} hackathon",
            "theme": theme,
            "difficulty": difficulty,
            "challenge": challenge,
            "duration_hours": duration_hours,
            "max_participants": max_participants,
            "status": HackathonStatus.UPCOMING.value,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "start_time": start_time or (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "end_time": (datetime.fromisoformat(start_time) + timedelta(hours=duration_hours)).isoformat() if start_time else (datetime.utcnow() + timedelta(hours=duration_hours + 1)).isoformat(),
            "participants": [],
            "submissions": {},
            "leaderboard": []
        }
        
        # Store hackathon
        self.active_hackathons[hackathon_id] = hackathon
        self.update_state(hackathon_id, hackathon)
        
        # Emit hackathon created event
        self.emit_event(
            "hackathon.created",
            None,
            user_id,
            {
                "hackathon_id": hackathon_id,
                "hackathon": hackathon,
                "registration_open": True
            }
        )
        
        return {
            "status": "hackathon_created",
            "hackathon_id": hackathon_id,
            "hackathon": hackathon
        }
    
    def _handle_join_request(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle hackathon join request"""
        user_id = event.user_id
        payload = event.payload
        
        hackathon_id = payload.get("hackathon_id")
        team_name = payload.get("team_name", user_id)
        
        hackathon = self.active_hackathons.get(hackathon_id)
        if not hackathon:
            return {"error": "Hackathon not found"}
        
        # Check if hackathon is accepting participants
        if hackathon["status"] != HackathonStatus.UPCOMING.value:
            return {"error": "Hackathon is not accepting new participants"}
        
        # Check participant limit
        if len(hackathon["participants"]) >= hackathon["max_participants"]:
            return {"error": "Hackathon is full"}
        
        # Check if user already joined
        if user_id in [p["user_id"] for p in hackathon["participants"]]:
            return {"error": "Already registered for this hackathon"}
        
        # Add participant
        participant = {
            "user_id": user_id,
            "team_name": team_name,
            "joined_at": datetime.utcnow().isoformat(),
            "submission_status": "not_submitted"
        }
        
        hackathon["participants"].append(participant)
        self.active_hackathons[hackathon_id] = hackathon
        self.update_state(hackathon_id, hackathon)
        
        # Emit participant joined event
        self.emit_event(
            "hackathon.participant_joined",
            None,
            user_id,
            {
                "hackathon_id": hackathon_id,
                "team_name": team_name,
                "total_participants": len(hackathon["participants"])
            }
        )
        
        return {
            "status": "joined_successfully",
            "hackathon_id": hackathon_id,
            "team_name": team_name
        }
    
    def _handle_submission(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle hackathon submission"""
        user_id = event.user_id
        payload = event.payload
        
        hackathon_id = payload.get("hackathon_id")
        submission_data = payload.get("submission_data", {})
        
        hackathon = self.active_hackathons.get(hackathon_id)
        if not hackathon:
            return {"error": "Hackathon not found"}
        
        # Check if user is participant
        participant = next((p for p in hackathon["participants"] if p["user_id"] == user_id), None)
        if not participant:
            return {"error": "Not registered for this hackathon"}
        
        # Check if hackathon is active
        current_time = datetime.utcnow()
        start_time = datetime.fromisoformat(hackathon["start_time"])
        end_time = datetime.fromisoformat(hackathon["end_time"])
        
        if current_time < start_time:
            return {"error": "Hackathon has not started yet"}
        
        if current_time > end_time:
            return {"error": "Hackathon submission deadline has passed"}
        
        # Process submission
        submission = {
            "user_id": user_id,
            "team_name": participant["team_name"],
            "submission_data": submission_data,
            "submitted_at": datetime.utcnow().isoformat(),
            "evaluation_status": "pending",
            "score": 0,
            "feedback": []
        }
        
        # Evaluate submission
        evaluation_result = self._evaluate_submission(submission, hackathon["challenge"])
        submission.update(evaluation_result)
        
        # Store submission
        hackathon["submissions"][user_id] = submission
        
        # Update participant status
        participant["submission_status"] = "submitted"
        participant["submission_time"] = submission["submitted_at"]
        
        # Update leaderboard
        self._update_leaderboard(hackathon_id, submission)
        
        self.active_hackathons[hackathon_id] = hackathon
        self.update_state(hackathon_id, hackathon)
        
        # Emit submission received event
        self.emit_event(
            "hackathon.submission_received",
            None,
            user_id,
            {
                "hackathon_id": hackathon_id,
                "score": submission["score"],
                "rank": self._get_user_rank(hackathon_id, user_id)
            }
        )
        
        return {
            "status": "submission_received",
            "score": submission["score"],
            "feedback": submission["feedback"],
            "rank": self._get_user_rank(hackathon_id, user_id)
        }
    
    def _handle_evaluation_completed(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle manual evaluation completion"""
        payload = event.payload
        
        hackathon_id = payload.get("hackathon_id")
        user_id = payload.get("evaluated_user_id")
        manual_scores = payload.get("manual_scores", {})
        judge_feedback = payload.get("judge_feedback", "")
        
        hackathon = self.active_hackathons.get(hackathon_id)
        if not hackathon or user_id not in hackathon["submissions"]:
            return {"error": "Submission not found"}
        
        submission = hackathon["submissions"][user_id]
        
        # Combine automated and manual scores
        final_score = self._combine_scores(submission["score"], manual_scores)
        
        # Update submission
        submission.update({
            "final_score": final_score,
            "manual_scores": manual_scores,
            "judge_feedback": judge_feedback,
            "evaluation_status": "completed"
        })
        
        # Update leaderboard with final scores
        self._update_leaderboard(hackathon_id, submission, use_final_score=True)
        
        self.active_hackathons[hackathon_id] = hackathon
        self.update_state(hackathon_id, hackathon)
        
        return {
            "status": "evaluation_completed",
            "final_score": final_score
        }
    
    def _generate_challenge(self, theme: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """Generate challenge based on theme and difficulty"""
        if theme in self.challenge_templates and difficulty in self.challenge_templates[theme]:
            templates = self.challenge_templates[theme][difficulty]
            if templates:
                import random
                return random.choice(templates).copy()
        return None
    
    def _evaluate_submission(self, submission: Dict[str, Any], 
                           challenge: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate hackathon submission automatically"""
        submission_data = submission.get("submission_data", {})
        
        # Initialize evaluation
        evaluation = {
            "score": 0,
            "max_score": challenge.get("max_score", 100),
            "feedback": [],
            "score_breakdown": {},
            "evaluation_status": "completed"
        }
        
        # Check required components
        requirements = challenge.get("requirements", [])
        requirements_met = 0
        
        for i, requirement in enumerate(requirements):
            # Simplified requirement checking based on submission content
            requirement_met = self._check_requirement(submission_data, requirement)
            if requirement_met:
                requirements_met += 1
                evaluation["feedback"].append(f"✓ {requirement}")
            else:
                evaluation["feedback"].append(f"✗ {requirement}")
        
        # Calculate requirements score
        requirements_score = (requirements_met / len(requirements)) * 40 if requirements else 0
        evaluation["score_breakdown"]["requirements"] = requirements_score
        
        # Evaluate code quality (simplified)
        code_quality_score = self._evaluate_code_quality(submission_data)
        evaluation["score_breakdown"]["code_quality"] = code_quality_score
        
        # Evaluate creativity/innovation
        creativity_score = self._evaluate_creativity(submission_data)
        evaluation["score_breakdown"]["creativity"] = creativity_score
        
        # Evaluate documentation
        documentation_score = self._evaluate_documentation(submission_data)
        evaluation["score_breakdown"]["documentation"] = documentation_score
        
        # Calculate total score
        total_score = (
            requirements_score + 
            code_quality_score * 0.3 + 
            creativity_score * 0.2 + 
            documentation_score * 0.1
        )
        
        evaluation["score"] = min(int(total_score), evaluation["max_score"])
        
        # Time bonus (submitted early)
        submitted_time = datetime.fromisoformat(submission["submitted_at"])
        if "early_submission_bonus" not in evaluation:
            # Add time-based bonus logic here if needed
            pass
        
        return evaluation
    
    def _check_requirement(self, submission_data: Dict[str, Any], requirement: str) -> bool:
        """Check if submission meets a specific requirement"""
        # Simplified requirement checking
        requirement_lower = requirement.lower()
        
        # Check based on submission content
        description = submission_data.get("description", "").lower()
        code_files = submission_data.get("code_files", {})
        
        # Basic keyword matching for requirements
        keywords = {
            "responsive": ["responsive", "mobile", "media query"],
            "database": ["database", "db", "sql", "mongodb", "postgres"],
            "authentication": ["auth", "login", "signup", "user"],
            "api": ["api", "endpoint", "rest", "graphql"],
            "test": ["test", "testing", "jest", "pytest"],
        }
        
        for key, terms in keywords.items():
            if key in requirement_lower:
                return any(term in description or 
                          any(term in str(code).lower() for code in code_files.values()) 
                          for term in terms)
        
        # Default to basic check
        return len(submission_data.get("code_files", {})) > 0
    
    def _evaluate_code_quality(self, submission_data: Dict[str, Any]) -> float:
        """Evaluate code quality of submission"""
        code_files = submission_data.get("code_files", {})
        if not code_files:
            return 0.0
        
        quality_score = 50.0  # Base score
        
        # Check for good practices
        total_code = " ".join(str(code) for code in code_files.values()).lower()
        
        # Positive indicators
        if "function" in total_code or "def " in total_code:
            quality_score += 10  # Functions/modularity
        
        if "class" in total_code:
            quality_score += 5   # OOP
        
        if "import" in total_code:
            quality_score += 5   # External libraries
        
        # Check for comments
        if "#" in total_code or "//" in total_code or "/*" in total_code:
            quality_score += 10  # Documentation
        
        # Check for error handling
        if any(term in total_code for term in ["try", "catch", "except", "error"]):
            quality_score += 10  # Error handling
        
        return min(quality_score, 100.0)
    
    def _evaluate_creativity(self, submission_data: Dict[str, Any]) -> float:
        """Evaluate creativity and innovation"""
        description = submission_data.get("description", "").lower()
        features = submission_data.get("features", [])
        
        creativity_score = 30.0  # Base score
        
        # Check for innovative features
        innovative_terms = [
            "unique", "innovative", "creative", "original", "novel",
            "ai", "machine learning", "automation", "real-time",
            "visualization", "analytics", "dashboard"
        ]
        
        for term in innovative_terms:
            if term in description:
                creativity_score += 5
        
        # Bonus for additional features
        creativity_score += min(len(features) * 5, 20)
        
        return min(creativity_score, 100.0)
    
    def _evaluate_documentation(self, submission_data: Dict[str, Any]) -> float:
        """Evaluate documentation quality"""
        readme = submission_data.get("readme", "")
        description = submission_data.get("description", "")
        
        if not readme and not description:
            return 0.0
        
        doc_score = 20.0  # Base score for having documentation
        
        # Check documentation quality
        combined_docs = (readme + " " + description).lower()
        
        quality_indicators = [
            "installation", "setup", "usage", "features",
            "requirements", "dependencies", "api", "examples"
        ]
        
        for indicator in quality_indicators:
            if indicator in combined_docs:
                doc_score += 10
        
        return min(doc_score, 100.0)
    
    def _combine_scores(self, automated_score: float, manual_scores: Dict[str, float]) -> float:
        """Combine automated and manual scores"""
        if not manual_scores:
            return automated_score
        
        # Weighted combination
        automated_weight = 0.6
        manual_weight = 0.4
        
        manual_average = sum(manual_scores.values()) / len(manual_scores)
        
        return automated_score * automated_weight + manual_average * manual_weight
    
    def _update_leaderboard(self, hackathon_id: str, submission: Dict[str, Any], 
                          use_final_score: bool = False):
        """Update hackathon leaderboard"""
        hackathon = self.active_hackathons.get(hackathon_id)
        if not hackathon:
            return
        
        score_field = "final_score" if use_final_score and "final_score" in submission else "score"
        
        # Remove existing entry for this user
        hackathon["leaderboard"] = [
            entry for entry in hackathon["leaderboard"] 
            if entry["user_id"] != submission["user_id"]
        ]
        
        # Add new entry
        leaderboard_entry = {
            "user_id": submission["user_id"],
            "team_name": submission["team_name"],
            "score": submission[score_field],
            "submitted_at": submission["submitted_at"],
            "evaluation_status": submission.get("evaluation_status", "completed")
        }
        
        hackathon["leaderboard"].append(leaderboard_entry)
        
        # Sort by score descending
        hackathon["leaderboard"].sort(key=lambda x: x["score"], reverse=True)
        
        # Add ranks
        for i, entry in enumerate(hackathon["leaderboard"]):
            entry["rank"] = i + 1
    
    def _get_user_rank(self, hackathon_id: str, user_id: str) -> Optional[int]:
        """Get user's current rank in hackathon"""
        hackathon = self.active_hackathons.get(hackathon_id)
        if not hackathon:
            return None
        
        for entry in hackathon["leaderboard"]:
            if entry["user_id"] == user_id:
                return entry["rank"]
        
        return None
    
    def get_hackathon_status(self, hackathon_id: str) -> Dict[str, Any]:
        """Get current status of a hackathon"""
        hackathon = self.active_hackathons.get(hackathon_id)
        if not hackathon:
            return {"error": "Hackathon not found"}
        
        current_time = datetime.utcnow()
        start_time = datetime.fromisoformat(hackathon["start_time"])
        end_time = datetime.fromisoformat(hackathon["end_time"])
        
        # Update status based on time
        if current_time < start_time:
            status = HackathonStatus.UPCOMING.value
        elif current_time <= end_time:
            status = HackathonStatus.ACTIVE.value
        else:
            # Check if all submissions are evaluated
            all_evaluated = all(
                sub.get("evaluation_status") == "completed" 
                for sub in hackathon["submissions"].values()
            )
            status = HackathonStatus.COMPLETED.value if all_evaluated else HackathonStatus.JUDGING.value
        
        hackathon["status"] = status
        
        return {
            "hackathon": hackathon,
            "time_remaining": max(0, (end_time - current_time).total_seconds()) if status == HackathonStatus.ACTIVE.value else 0,
            "submissions_count": len(hackathon["submissions"]),
            "participants_count": len(hackathon["participants"])
        }
    
    def get_user_hackathons(self, user_id: str) -> List[Dict[str, Any]]:
        """Get hackathons user has participated in"""
        user_hackathons = []
        
        for hackathon in self.active_hackathons.values():
            # Check if user is participant
            if user_id in [p["user_id"] for p in hackathon["participants"]]:
                user_hackathons.append({
                    "hackathon_id": hackathon["id"],
                    "title": hackathon["title"],
                    "status": hackathon["status"],
                    "theme": hackathon["theme"],
                    "difficulty": hackathon["difficulty"],
                    "start_time": hackathon["start_time"],
                    "end_time": hackathon["end_time"],
                    "submission_status": hackathon["submissions"].get(user_id, {}).get("evaluation_status", "not_submitted"),
                    "score": hackathon["submissions"].get(user_id, {}).get("score", 0),
                    "rank": self._get_user_rank(hackathon["id"], user_id)
                })
        
        return user_hackathons
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": "HackathonAgent",
            "version": "1.0.0",
            "capabilities": [
                "challenge_generation",
                "automated_evaluation",
                "leaderboard_management",
                "team_formation",
                "submission_tracking",
                "judge_dashboard"
            ],
            "themes": list(self.challenge_templates.keys()),
            "difficulty_levels": ["beginner", "intermediate", "advanced"],
            "evaluation_criteria": list(self.scoring_weights.keys()),
            "hackathon_statuses": [status.value for status in HackathonStatus],
            "supported_events": [
                "hackathon.create_requested",
                "hackathon.submission_made", 
                "hackathon.join_requested",
                "hackathon.evaluation_completed"
            ],
            "emitted_events": [
                "hackathon.created",
                "hackathon.participant_joined",
                "hackathon.submission_received",
                "hackathon.leaderboard_updated"
            ]
        }