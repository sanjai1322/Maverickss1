"""
Learning Path Agent
===================

Generates personalized learning curricula and manages learning progress.
Creates adaptive learning experiences based on user skills and goals.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent, AgentEvent

logger = logging.getLogger(__name__)

class LearningPathAgent(BaseAgent):
    """
    Learning Path Agent creates and manages personalized learning curricula.
    
    Capabilities:
    - Personalized curriculum generation based on skill gaps
    - Adaptive learning path recommendations
    - Progress tracking and milestone management
    - Learning resource curation and organization
    """
    
    def __init__(self, event_bus=None):
        super().__init__("LearningPathAgent", event_bus)
        
        # Subscribe to relevant events
        self.subscribe_to_event("skills.extracted")
        self.subscribe_to_event("assessment.completed")
        self.subscribe_to_event("learning.path_requested")
        self.subscribe_to_event("learning.module_completed")
        self.subscribe_to_event("learning.progress_update")
        
        # Learning curriculum templates
        self.curriculum_templates = {
            "python_fundamentals": {
                "title": "Python Programming Fundamentals",
                "description": "Master the basics of Python programming",
                "duration_weeks": 8,
                "difficulty": "beginner",
                "prerequisites": [],
                "modules": [
                    {
                        "title": "Python Syntax and Data Types",
                        "description": "Learn basic Python syntax, variables, and data types",
                        "duration_hours": 6,
                        "topics": ["variables", "data_types", "operators", "input_output"],
                        "exercises": 5,
                        "resources": [
                            {"type": "reading", "title": "Python Basics", "url": "example.com"},
                            {"type": "video", "title": "Python Variables", "duration": 30}
                        ]
                    },
                    {
                        "title": "Control Flow and Functions",
                        "description": "Master if statements, loops, and function creation",
                        "duration_hours": 8,
                        "topics": ["conditionals", "loops", "functions", "scope"],
                        "exercises": 8,
                        "resources": []
                    },
                    {
                        "title": "Data Structures",
                        "description": "Work with lists, dictionaries, sets, and tuples",
                        "duration_hours": 10,
                        "topics": ["lists", "dictionaries", "sets", "tuples"],
                        "exercises": 12,
                        "resources": []
                    },
                    {
                        "title": "File I/O and Error Handling",
                        "description": "Handle files and manage exceptions",
                        "duration_hours": 6,
                        "topics": ["file_operations", "exceptions", "debugging"],
                        "exercises": 6,
                        "resources": []
                    }
                ]
            },
            "web_development_basics": {
                "title": "Web Development Fundamentals",
                "description": "Build modern web applications",
                "duration_weeks": 12,
                "difficulty": "intermediate",
                "prerequisites": ["html", "css", "javascript"],
                "modules": [
                    {
                        "title": "HTML5 and Semantic Markup",
                        "description": "Create structured, accessible web pages",
                        "duration_hours": 8,
                        "topics": ["html5_elements", "forms", "accessibility", "seo"],
                        "exercises": 6
                    },
                    {
                        "title": "CSS3 and Responsive Design",
                        "description": "Style websites with modern CSS",
                        "duration_hours": 12,
                        "topics": ["flexbox", "grid", "animations", "responsive_design"],
                        "exercises": 10
                    },
                    {
                        "title": "JavaScript ES6+",
                        "description": "Modern JavaScript programming",
                        "duration_hours": 15,
                        "topics": ["arrow_functions", "promises", "async_await", "modules"],
                        "exercises": 15
                    },
                    {
                        "title": "Frontend Framework (React)",
                        "description": "Build interactive user interfaces",
                        "duration_hours": 20,
                        "topics": ["components", "state", "hooks", "routing"],
                        "exercises": 12
                    }
                ]
            },
            "data_structures_algorithms": {
                "title": "Data Structures and Algorithms",
                "description": "Master fundamental CS concepts",
                "duration_weeks": 16,
                "difficulty": "advanced",
                "prerequisites": ["programming_basics"],
                "modules": [
                    {
                        "title": "Array and String Algorithms",
                        "description": "Master array and string manipulation",
                        "duration_hours": 12,
                        "topics": ["two_pointers", "sliding_window", "string_matching"],
                        "exercises": 20
                    },
                    {
                        "title": "Linked Lists and Trees",
                        "description": "Understand linear and hierarchical data structures",
                        "duration_hours": 15,
                        "topics": ["linked_lists", "binary_trees", "tree_traversal"],
                        "exercises": 25
                    },
                    {
                        "title": "Graphs and Dynamic Programming",
                        "description": "Advanced algorithmic concepts",
                        "duration_hours": 20,
                        "topics": ["graph_algorithms", "dp_patterns", "optimization"],
                        "exercises": 30
                    }
                ]
            }
        }
        
        # Skill to curriculum mapping
        self.skill_to_curriculum = {
            "python": ["python_fundamentals", "data_structures_algorithms"],
            "javascript": ["web_development_basics"],
            "web_technologies": ["web_development_basics"],
            "algorithms": ["data_structures_algorithms"],
            "data_structures": ["data_structures_algorithms"]
        }
    
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process learning path related events"""
        try:
            if event.event_type == "skills.extracted":
                return self._handle_skills_extracted(event)
            elif event.event_type == "assessment.completed":
                return self._handle_assessment_completed(event)
            elif event.event_type == "learning.path_requested":
                return self._handle_learning_path_request(event)
            elif event.event_type == "learning.module_completed":
                return self._handle_module_completion(event)
            elif event.event_type == "learning.progress_update":
                return self._handle_progress_update(event)
            else:
                self.logger.warning(f"Unhandled event type: {event.event_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {str(e)}")
            return {"error": str(e)}
    
    def _handle_skills_extracted(self, event: AgentEvent) -> Dict[str, Any]:
        """Generate initial learning path recommendations based on extracted skills"""
        user_id = event.user_id
        payload = event.payload
        
        extracted_skills = payload.get("extracted_skills", {})
        skill_vector = payload.get("skill_vector", {})
        
        # Generate learning path recommendations
        recommendations = self._generate_path_recommendations(extracted_skills, skill_vector)
        
        # Store learning state
        learning_state = {
            "user_id": user_id,
            "extracted_skills": extracted_skills,
            "skill_vector": skill_vector,
            "recommendations": recommendations,
            "active_paths": [],
            "completed_modules": [],
            "progress": {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.update_state(user_id, learning_state)
        
        # Emit recommendations ready event
        self.emit_event(
            "learning.recommendations_ready",
            None,
            user_id,
            {
                "recommendations": recommendations,
                "total_paths": len(recommendations),
                "estimated_time": sum(rec.get("duration_weeks", 0) for rec in recommendations)
            }
        )
        
        return {
            "status": "recommendations_generated",
            "recommendations": recommendations
        }
    
    def _handle_assessment_completed(self, event: AgentEvent) -> Dict[str, Any]:
        """Refine learning paths based on assessment results"""
        user_id = event.user_id
        payload = event.payload
        
        final_results = payload.get("final_results", {})
        skill_levels = final_results.get("skill_levels", {})
        
        learning_state = self.get_state(user_id)
        if not learning_state:
            return {"error": "Learning state not found"}
        
        # Refine recommendations based on assessment
        refined_recommendations = self._refine_recommendations(
            learning_state.get("recommendations", []),
            skill_levels,
            final_results
        )
        
        # Generate personalized learning path
        personalized_path = self._generate_personalized_path(skill_levels, final_results)
        
        learning_state.update({
            "assessment_results": final_results,
            "skill_levels": skill_levels,
            "refined_recommendations": refined_recommendations,
            "personalized_path": personalized_path,
            "path_generated_at": datetime.utcnow().isoformat()
        })
        
        self.update_state(user_id, learning_state)
        
        # Emit personalized path ready event
        self.emit_event(
            "learning.personalized_path_ready",
            None,
            user_id,
            {
                "personalized_path": personalized_path,
                "refined_recommendations": refined_recommendations,
                "skill_gaps_addressed": len(personalized_path.get("modules", []))
            }
        )
        
        return {
            "status": "personalized_path_created",
            "path": personalized_path
        }
    
    def _handle_learning_path_request(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle specific learning path requests from user"""
        user_id = event.user_id
        payload = event.payload
        
        requested_path = payload.get("path_type")
        learning_goals = payload.get("learning_goals", [])
        time_commitment = payload.get("time_commitment", 5)  # hours per week
        
        learning_state = self.get_state(user_id)
        if not learning_state:
            return {"error": "Learning state not found"}
        
        # Create customized learning path
        custom_path = self._create_custom_path(
            requested_path, 
            learning_goals, 
            time_commitment,
            learning_state.get("skill_levels", {})
        )
        
        # Add to active paths
        if "active_paths" not in learning_state:
            learning_state["active_paths"] = []
        
        learning_state["active_paths"].append(custom_path)
        learning_state["progress"][custom_path["id"]] = {
            "status": "started",
            "completed_modules": 0,
            "total_modules": len(custom_path.get("modules", [])),
            "start_date": datetime.utcnow().isoformat(),
            "estimated_completion": self._calculate_completion_date(
                custom_path, time_commitment
            )
        }
        
        self.update_state(user_id, learning_state)
        
        return {
            "status": "custom_path_created",
            "path": custom_path,
            "estimated_completion": learning_state["progress"][custom_path["id"]]["estimated_completion"]
        }
    
    def _handle_module_completion(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle learning module completion"""
        user_id = event.user_id
        payload = event.payload
        
        path_id = payload.get("path_id")
        module_id = payload.get("module_id")
        completion_time = payload.get("completion_time", 0)
        score = payload.get("score", 0)
        
        learning_state = self.get_state(user_id)
        if not learning_state:
            return {"error": "Learning state not found"}
        
        # Update progress
        if path_id in learning_state.get("progress", {}):
            path_progress = learning_state["progress"][path_id]
            path_progress["completed_modules"] += 1
            
            # Check if path is complete
            if path_progress["completed_modules"] >= path_progress["total_modules"]:
                path_progress["status"] = "completed"
                path_progress["completion_date"] = datetime.utcnow().isoformat()
                
                # Emit path completion event
                self.emit_event(
                    "learning.path_completed",
                    None,
                    user_id,
                    {
                        "path_id": path_id,
                        "completion_date": path_progress["completion_date"],
                        "total_modules": path_progress["total_modules"]
                    }
                )
        
        # Add to completed modules
        if "completed_modules" not in learning_state:
            learning_state["completed_modules"] = []
        
        learning_state["completed_modules"].append({
            "path_id": path_id,
            "module_id": module_id,
            "completed_at": datetime.utcnow().isoformat(),
            "completion_time": completion_time,
            "score": score
        })
        
        self.update_state(user_id, learning_state)
        
        # Generate next recommendations
        next_recommendations = self._get_next_recommendations(user_id)
        
        return {
            "status": "module_completed",
            "path_progress": learning_state["progress"].get(path_id, {}),
            "next_recommendations": next_recommendations
        }
    
    def _handle_progress_update(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle learning progress updates"""
        user_id = event.user_id
        payload = event.payload
        
        progress_data = payload.get("progress_data", {})
        
        learning_state = self.get_state(user_id)
        if not learning_state:
            return {"error": "Learning state not found"}
        
        # Update progress data
        for path_id, progress in progress_data.items():
            if path_id in learning_state.get("progress", {}):
                learning_state["progress"][path_id].update(progress)
        
        learning_state["last_updated"] = datetime.utcnow().isoformat()
        self.update_state(user_id, learning_state)
        
        return {"status": "progress_updated"}
    
    def _generate_path_recommendations(self, extracted_skills: Dict[str, List[str]], 
                                     skill_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate initial learning path recommendations"""
        recommendations = []
        
        # Analyze skill gaps and strengths
        strong_skills = [skill for skill, level in skill_vector.items() if level > 0.7]
        weak_skills = [skill for skill, level in skill_vector.items() if level < 0.4]
        
        # Recommend paths based on extracted skills
        for category, skills in extracted_skills.items():
            if category in self.skill_to_curriculum:
                for curriculum_id in self.skill_to_curriculum[category]:
                    if curriculum_id in self.curriculum_templates:
                        curriculum = self.curriculum_templates[curriculum_id].copy()
                        
                        # Customize based on skill level
                        if any(skill in str(strong_skills).lower() for skill in skills):
                            curriculum["recommended_pace"] = "accelerated"
                            curriculum["skip_basics"] = True
                        elif any(skill in str(weak_skills).lower() for skill in skills):
                            curriculum["recommended_pace"] = "thorough"
                            curriculum["extra_practice"] = True
                        else:
                            curriculum["recommended_pace"] = "normal"
                        
                        curriculum["match_score"] = self._calculate_match_score(
                            curriculum, extracted_skills, skill_vector
                        )
                        
                        recommendations.append(curriculum)
        
        # Sort by match score
        recommendations.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _refine_recommendations(self, current_recommendations: List[Dict[str, Any]], 
                              skill_levels: Dict[str, str],
                              assessment_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Refine recommendations based on assessment results"""
        refined = []
        
        for rec in current_recommendations:
            refined_rec = rec.copy()
            
            # Adjust difficulty based on assessment performance
            avg_score = assessment_results.get("average_score", 50)
            
            if avg_score >= 80:
                refined_rec["difficulty"] = "advanced"
                refined_rec["accelerated_track"] = True
            elif avg_score >= 60:
                refined_rec["difficulty"] = "intermediate"
            else:
                refined_rec["difficulty"] = "beginner"
                refined_rec["foundational_support"] = True
            
            # Add priority based on skill gaps
            priority_score = 0
            for skill, level in skill_levels.items():
                if level == "beginner" and skill in refined_rec.get("title", "").lower():
                    priority_score += 3
                elif level == "intermediate":
                    priority_score += 2
                else:
                    priority_score += 1
            
            refined_rec["priority_score"] = priority_score
            refined.append(refined_rec)
        
        # Sort by priority
        refined.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return refined
    
    def _generate_personalized_path(self, skill_levels: Dict[str, str], 
                                   assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fully personalized learning path"""
        avg_score = assessment_results.get("average_score", 50)
        recommendations = assessment_results.get("recommendations", [])
        
        # Determine starting difficulty
        if avg_score >= 80:
            starting_difficulty = "intermediate"
        elif avg_score >= 60:
            starting_difficulty = "beginner-plus"
        else:
            starting_difficulty = "beginner"
        
        # Create personalized modules based on skill gaps
        personalized_modules = []
        
        # Add foundational modules for low-scoring areas
        for skill, level in skill_levels.items():
            if level == "beginner":
                personalized_modules.extend(self._get_foundational_modules(skill))
        
        # Add intermediate modules for moderate areas
        for skill, level in skill_levels.items():
            if level == "intermediate":
                personalized_modules.extend(self._get_intermediate_modules(skill))
        
        # Create the personalized path
        personalized_path = {
            "id": f"personalized_{assessment_results.get('user_id', 'user')}_{int(datetime.utcnow().timestamp())}",
            "title": "Your Personalized Learning Journey",
            "description": f"Customized path based on your assessment results (Score: {avg_score}%)",
            "difficulty": starting_difficulty,
            "total_modules": len(personalized_modules),
            "estimated_weeks": len(personalized_modules) * 2,  # 2 weeks per module average
            "modules": personalized_modules,
            "created_at": datetime.utcnow().isoformat(),
            "assessment_based": True,
            "skill_focus": list(skill_levels.keys())
        }
        
        return personalized_path
    
    def _create_custom_path(self, path_type: str, learning_goals: List[str], 
                          time_commitment: int, skill_levels: Dict[str, str]) -> Dict[str, Any]:
        """Create custom learning path based on user preferences"""
        
        # Select base curriculum
        base_curriculum = None
        if path_type in self.curriculum_templates:
            base_curriculum = self.curriculum_templates[path_type].copy()
        else:
            # Default to most relevant curriculum
            base_curriculum = list(self.curriculum_templates.values())[0].copy()
        
        # Customize based on time commitment
        modules = base_curriculum.get("modules", [])
        if time_commitment < 5:  # Less than 5 hours per week
            # Extend timeline and add more practice
            for module in modules:
                module["duration_hours"] = int(module.get("duration_hours", 5) * 1.5)
                module["extra_practice"] = True
        elif time_commitment > 10:  # More than 10 hours per week
            # Accelerated pace
            for module in modules:
                module["duration_hours"] = int(module.get("duration_hours", 5) * 0.8)
                module["accelerated"] = True
        
        # Add goal-specific modules
        for goal in learning_goals:
            if goal.lower() in ["job interview", "interview prep"]:
                modules.append({
                    "title": "Technical Interview Preparation",
                    "description": "Practice coding interviews and system design",
                    "duration_hours": 15,
                    "topics": ["interview_practice", "system_design", "behavioral_questions"],
                    "exercises": 20
                })
        
        custom_path = {
            "id": f"custom_{path_type}_{int(datetime.utcnow().timestamp())}",
            "title": base_curriculum.get("title", "Custom Learning Path"),
            "description": base_curriculum.get("description", ""),
            "modules": modules,
            "time_commitment": time_commitment,
            "learning_goals": learning_goals,
            "customized": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return custom_path
    
    def _get_foundational_modules(self, skill: str) -> List[Dict[str, Any]]:
        """Get foundational modules for a skill area"""
        foundational_modules = {
            "python": [
                {
                    "title": "Python Basics Review",
                    "description": "Strengthen Python fundamentals",
                    "duration_hours": 8,
                    "topics": ["syntax", "variables", "basic_operations"],
                    "exercises": 10
                }
            ],
            "javascript": [
                {
                    "title": "JavaScript Fundamentals",
                    "description": "Core JavaScript concepts and syntax",
                    "duration_hours": 10,
                    "topics": ["variables", "functions", "objects", "arrays"],
                    "exercises": 12
                }
            ]
        }
        
        return foundational_modules.get(skill, [])
    
    def _get_intermediate_modules(self, skill: str) -> List[Dict[str, Any]]:
        """Get intermediate modules for a skill area"""
        intermediate_modules = {
            "python": [
                {
                    "title": "Advanced Python Concepts",
                    "description": "Object-oriented programming and advanced features",
                    "duration_hours": 12,
                    "topics": ["oop", "decorators", "generators", "context_managers"],
                    "exercises": 15
                }
            ],
            "javascript": [
                {
                    "title": "Modern JavaScript",
                    "description": "ES6+ features and async programming",
                    "duration_hours": 15,
                    "topics": ["arrow_functions", "promises", "async_await", "modules"],
                    "exercises": 18
                }
            ]
        }
        
        return intermediate_modules.get(skill, [])
    
    def _calculate_match_score(self, curriculum: Dict[str, Any], 
                             extracted_skills: Dict[str, List[str]], 
                             skill_vector: Dict[str, float]) -> float:
        """Calculate how well a curriculum matches user's skills"""
        match_score = 0.0
        
        curriculum_title = curriculum.get("title", "").lower()
        curriculum_description = curriculum.get("description", "").lower()
        
        # Check skill category matches
        for category, skills in extracted_skills.items():
            if category.replace("_", " ") in curriculum_title or category.replace("_", " ") in curriculum_description:
                match_score += 0.3
            
            # Check individual skill matches
            for skill in skills:
                if skill in curriculum_title or skill in curriculum_description:
                    skill_level = skill_vector.get(f"skill_{skill}", 0.5)
                    match_score += skill_level * 0.1
        
        return min(match_score, 1.0)
    
    def _calculate_completion_date(self, path: Dict[str, Any], hours_per_week: int) -> str:
        """Calculate estimated completion date for a learning path"""
        total_hours = sum(module.get("duration_hours", 5) for module in path.get("modules", []))
        weeks_needed = total_hours / max(hours_per_week, 1)
        completion_date = datetime.utcnow() + timedelta(weeks=weeks_needed)
        return completion_date.isoformat()
    
    def _get_next_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get next learning recommendations based on current progress"""
        learning_state = self.get_state(user_id)
        if not learning_state:
            return []
        
        completed_modules = learning_state.get("completed_modules", [])
        active_paths = learning_state.get("active_paths", [])
        
        recommendations = []
        
        # Recommend next modules in active paths
        for path in active_paths:
            path_progress = learning_state.get("progress", {}).get(path["id"], {})
            completed_count = path_progress.get("completed_modules", 0)
            total_modules = len(path.get("modules", []))
            
            if completed_count < total_modules:
                next_module = path["modules"][completed_count]
                recommendations.append({
                    "type": "continue_path",
                    "path_id": path["id"],
                    "path_title": path.get("title", ""),
                    "next_module": next_module,
                    "priority": "high"
                })
        
        return recommendations
    
    def get_user_learning_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive learning dashboard for user"""
        learning_state = self.get_state(user_id)
        if not learning_state:
            return {"error": "Learning state not found"}
        
        dashboard = {
            "user_id": user_id,
            "active_paths": learning_state.get("active_paths", []),
            "progress": learning_state.get("progress", {}),
            "completed_modules": len(learning_state.get("completed_modules", [])),
            "recommendations": learning_state.get("recommendations", []),
            "next_actions": self._get_next_recommendations(user_id),
            "learning_streak": self._calculate_learning_streak(learning_state),
            "total_study_time": self._calculate_total_study_time(learning_state),
            "skill_progress": self._calculate_skill_progress(learning_state),
            "achievements": self._get_learning_achievements(learning_state)
        }
        
        return dashboard
    
    def _calculate_learning_streak(self, learning_state: Dict[str, Any]) -> int:
        """Calculate current learning streak"""
        completed_modules = learning_state.get("completed_modules", [])
        if not completed_modules:
            return 0
        
        # Simple streak calculation based on daily activity
        streak = 0
        current_date = datetime.utcnow().date()
        
        for i in range(30):  # Check last 30 days
            check_date = current_date - timedelta(days=i)
            day_activity = any(
                datetime.fromisoformat(module["completed_at"]).date() == check_date
                for module in completed_modules
            )
            
            if day_activity:
                streak += 1
            else:
                break
        
        return streak
    
    def _calculate_total_study_time(self, learning_state: Dict[str, Any]) -> int:
        """Calculate total study time in hours"""
        completed_modules = learning_state.get("completed_modules", [])
        total_time = sum(module.get("completion_time", 2) for module in completed_modules)
        return total_time
    
    def _calculate_skill_progress(self, learning_state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate skill progress based on completed modules"""
        completed_modules = learning_state.get("completed_modules", [])
        skill_progress = {}
        
        # This would be more sophisticated in practice
        for module in completed_modules:
            # Extract skills from module topics (simplified)
            module_id = module.get("module_id", "")
            if "python" in module_id.lower():
                skill_progress["python"] = skill_progress.get("python", 0) + 1
            elif "javascript" in module_id.lower():
                skill_progress["javascript"] = skill_progress.get("javascript", 0) + 1
        
        return skill_progress
    
    def _get_learning_achievements(self, learning_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get learning-specific achievements"""
        achievements = []
        completed_modules = learning_state.get("completed_modules", [])
        
        if len(completed_modules) >= 5:
            achievements.append({
                "title": "Dedicated Learner",
                "description": "Completed 5 learning modules",
                "earned_at": datetime.utcnow().isoformat()
            })
        
        if len(completed_modules) >= 20:
            achievements.append({
                "title": "Learning Marathon",
                "description": "Completed 20 learning modules", 
                "earned_at": datetime.utcnow().isoformat()
            })
        
        return achievements
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": "LearningPathAgent",
            "version": "1.0.0",
            "capabilities": [
                "personalized_curriculum_generation",
                "adaptive_learning_paths",
                "progress_tracking",
                "skill_gap_analysis",
                "resource_curation",
                "milestone_management"
            ],
            "curriculum_templates": list(self.curriculum_templates.keys()),
            "skill_mappings": self.skill_to_curriculum,
            "supported_events": [
                "skills.extracted",
                "assessment.completed",
                "learning.path_requested",
                "learning.module_completed",
                "learning.progress_update"
            ],
            "emitted_events": [
                "learning.recommendations_ready",
                "learning.personalized_path_ready",
                "learning.path_completed",
                "learning.module_available"
            ]
        }