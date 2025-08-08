"""
Assessment Agent
================

Manages automated coding skill assessments, exercise generation, and evaluation.
Uses AI to create personalized coding challenges and assess user performance.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

from .base_agent import BaseAgent, AgentEvent

logger = logging.getLogger(__name__)

class AssessmentAgent(BaseAgent):
    """
    Assessment Agent handles coding skill evaluation and exercise generation.
    
    Capabilities:
    - Automated exercise generation based on skill level
    - Code solution evaluation and scoring
    - Adaptive difficulty adjustment
    - Performance analytics and insights
    """
    
    def __init__(self, event_bus=None):
        super().__init__("AssessmentAgent", event_bus)
        
        # Subscribe to events
        self.subscribe_to_event("skills.extracted")
        self.subscribe_to_event("assessment.start_requested")
        self.subscribe_to_event("exercise.solution_submitted")
        self.subscribe_to_event("assessment.adaptive_adjustment")
        
        # Exercise templates by skill and difficulty
        self.exercise_templates = {
            "python": {
                "beginner": [
                    {
                        "title": "List Manipulation",
                        "description": "Write a function to find the maximum element in a list",
                        "starter_code": "def find_max(numbers):\n    # Your code here\n    pass",
                        "test_cases": [
                            {"input": "[1, 5, 3, 9, 2]", "expected": "9"},
                            {"input": "[-1, -5, -3]", "expected": "-1"}
                        ],
                        "skills": ["basic_programming", "data_structures"],
                        "time_limit": 15
                    },
                    {
                        "title": "String Operations",
                        "description": "Create a function to reverse words in a sentence",
                        "starter_code": "def reverse_words(sentence):\n    # Your code here\n    pass",
                        "test_cases": [
                            {"input": "'hello world'", "expected": "'world hello'"},
                            {"input": "'python programming'", "expected": "'programming python'"}
                        ],
                        "skills": ["string_manipulation", "basic_programming"],
                        "time_limit": 20
                    }
                ],
                "intermediate": [
                    {
                        "title": "Binary Search Implementation",
                        "description": "Implement binary search algorithm for a sorted array",
                        "starter_code": "def binary_search(arr, target):\n    # Your code here\n    pass",
                        "test_cases": [
                            {"input": "[1, 3, 5, 7, 9], 5", "expected": "2"},
                            {"input": "[2, 4, 6, 8], 1", "expected": "-1"}
                        ],
                        "skills": ["algorithms", "searching"],
                        "time_limit": 30
                    }
                ],
                "advanced": [
                    {
                        "title": "Dynamic Programming",
                        "description": "Solve the coin change problem using dynamic programming",
                        "starter_code": "def coin_change(coins, amount):\n    # Your code here\n    pass",
                        "test_cases": [
                            {"input": "[1, 3, 4], 6", "expected": "2"},
                            {"input": "[2], 3", "expected": "-1"}
                        ],
                        "skills": ["dynamic_programming", "optimization"],
                        "time_limit": 45
                    }
                ]
            },
            "javascript": {
                "beginner": [
                    {
                        "title": "Array Filter",
                        "description": "Filter even numbers from an array",
                        "starter_code": "function filterEvenNumbers(arr) {\n    // Your code here\n}",
                        "test_cases": [
                            {"input": "[1, 2, 3, 4, 5, 6]", "expected": "[2, 4, 6]"}
                        ],
                        "skills": ["array_methods", "functional_programming"],
                        "time_limit": 15
                    }
                ],
                "intermediate": [
                    {
                        "title": "Promise Handling",
                        "description": "Create a function that handles multiple API calls",
                        "starter_code": "async function handleAPICalls(urls) {\n    // Your code here\n}",
                        "test_cases": [
                            {"description": "Should handle concurrent requests properly"}
                        ],
                        "skills": ["async_programming", "promises"],
                        "time_limit": 30
                    }
                ]
            }
        }
        
        # Scoring criteria
        self.scoring_criteria = {
            "correctness": 0.4,      # Does it work?
            "efficiency": 0.25,      # Algorithm complexity
            "code_quality": 0.2,     # Clean, readable code
            "edge_cases": 0.15       # Handles edge cases
        }
    
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process assessment-related events"""
        try:
            if event.event_type == "skills.extracted":
                return self._handle_skills_extracted(event)
            elif event.event_type == "assessment.start_requested":
                return self._handle_assessment_start(event)
            elif event.event_type == "exercise.solution_submitted":
                return self._handle_solution_submission(event)
            elif event.event_type == "assessment.adaptive_adjustment":
                return self._handle_adaptive_adjustment(event)
            else:
                self.logger.warning(f"Unhandled event type: {event.event_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {str(e)}")
            return {"error": str(e)}
    
    def _handle_skills_extracted(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle skills extraction to prepare assessment strategy"""
        user_id = event.user_id
        payload = event.payload
        
        extracted_skills = payload.get("extracted_skills", {})
        skill_vector = payload.get("skill_vector", {})
        
        # Determine assessment strategy based on skills
        assessment_plan = self._create_assessment_plan(extracted_skills, skill_vector)
        
        # Store assessment state
        self.update_state(user_id, {
            "extracted_skills": extracted_skills,
            "skill_vector": skill_vector,
            "assessment_plan": assessment_plan,
            "current_difficulty": "beginner",
            "exercises_completed": 0,
            "total_score": 0,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # Emit assessment ready event
        self.emit_event(
            "assessment.ready",
            None,
            user_id,
            {
                "assessment_plan": assessment_plan,
                "recommended_exercises": len(assessment_plan.get("exercises", [])),
                "estimated_time": assessment_plan.get("estimated_time", 60)
            }
        )
        
        return {"status": "assessment_plan_created", "plan": assessment_plan}
    
    def _handle_assessment_start(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle assessment start request"""
        user_id = event.user_id
        payload = event.payload
        
        assessment_state = self.get_state(user_id)
        if not assessment_state:
            return {"error": "No assessment plan found. Please upload resume first."}
        
        # Generate first exercise
        exercise = self._generate_next_exercise(user_id, assessment_state)
        if not exercise:
            return {"error": "Unable to generate exercise"}
        
        # Update state
        assessment_state.update({
            "status": "in_progress",
            "current_exercise": exercise,
            "start_time": datetime.utcnow().isoformat()
        })
        self.update_state(user_id, assessment_state)
        
        # Emit exercise generated event
        self.emit_event(
            "exercise.generated",
            None,
            user_id,
            {
                "exercise": exercise,
                "assessment_status": "in_progress",
                "progress": f"{assessment_state['exercises_completed']}/{len(assessment_state.get('assessment_plan', {}).get('exercises', []))}"
            }
        )
        
        return {"status": "assessment_started", "exercise": exercise}
    
    def _handle_solution_submission(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle submitted exercise solution"""
        user_id = event.user_id
        payload = event.payload
        
        solution_code = payload.get("solution_code", "")
        exercise_id = payload.get("exercise_id", "")
        submission_time = payload.get("submission_time", datetime.utcnow().isoformat())
        
        assessment_state = self.get_state(user_id)
        if not assessment_state:
            return {"error": "Assessment session not found"}
        
        current_exercise = assessment_state.get("current_exercise", {})
        
        # Evaluate solution
        evaluation_result = self._evaluate_solution(solution_code, current_exercise)
        
        # Update assessment state
        assessment_state["exercises_completed"] += 1
        assessment_state["total_score"] += evaluation_result["score"]
        assessment_state["last_submission"] = {
            "exercise_id": exercise_id,
            "solution_code": solution_code,
            "score": evaluation_result["score"],
            "feedback": evaluation_result["feedback"],
            "submitted_at": submission_time
        }
        
        # Determine if assessment is complete
        plan_exercises = assessment_state.get("assessment_plan", {}).get("exercises", [])
        is_complete = assessment_state["exercises_completed"] >= len(plan_exercises)
        
        if is_complete:
            # Complete assessment
            final_results = self._finalize_assessment(user_id, assessment_state)
            
            # Emit assessment completed event
            self.emit_event(
                "assessment.completed",
                None,
                user_id,
                {
                    "final_results": final_results,
                    "total_exercises": assessment_state["exercises_completed"],
                    "average_score": assessment_state["total_score"] / assessment_state["exercises_completed"],
                    "skill_levels": final_results.get("skill_levels", {})
                }
            )
            
            return {"status": "assessment_complete", "results": final_results}
        else:
            # Generate next exercise
            next_exercise = self._generate_next_exercise(user_id, assessment_state)
            assessment_state["current_exercise"] = next_exercise
            
            self.update_state(user_id, assessment_state)
            
            # Emit next exercise event
            self.emit_event(
                "exercise.generated",
                None,
                user_id,
                {
                    "exercise": next_exercise,
                    "previous_score": evaluation_result["score"],
                    "progress": f"{assessment_state['exercises_completed']}/{len(plan_exercises)}"
                }
            )
            
            return {
                "status": "exercise_evaluated",
                "evaluation": evaluation_result,
                "next_exercise": next_exercise
            }
    
    def _handle_adaptive_adjustment(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle adaptive difficulty adjustment based on performance"""
        user_id = event.user_id
        payload = event.payload
        
        performance_data = payload.get("performance_data", {})
        assessment_state = self.get_state(user_id)
        
        if not assessment_state:
            return {"error": "Assessment session not found"}
        
        # Adjust difficulty based on performance
        current_difficulty = assessment_state.get("current_difficulty", "beginner")
        new_difficulty = self._calculate_adaptive_difficulty(performance_data, current_difficulty)
        
        assessment_state["current_difficulty"] = new_difficulty
        self.update_state(user_id, assessment_state)
        
        return {
            "status": "difficulty_adjusted",
            "old_difficulty": current_difficulty,
            "new_difficulty": new_difficulty
        }
    
    def _create_assessment_plan(self, extracted_skills: Dict[str, List[str]], 
                              skill_vector: Dict[str, float]) -> Dict[str, Any]:
        """Create personalized assessment plan based on extracted skills"""
        plan = {
            "exercises": [],
            "estimated_time": 0,
            "skill_areas": [],
            "difficulty_progression": ["beginner", "intermediate"]
        }
        
        # Determine primary programming languages
        programming_langs = extracted_skills.get("programming_languages", [])
        if not programming_langs:
            programming_langs = ["python"]  # Default
        
        # Select exercises for each skill area
        for lang in programming_langs[:2]:  # Limit to top 2 languages
            if lang in self.exercise_templates:
                plan["skill_areas"].append(lang)
                
                # Add exercises from different difficulty levels
                for difficulty in ["beginner", "intermediate"]:
                    templates = self.exercise_templates[lang].get(difficulty, [])
                    if templates:
                        selected_exercise = random.choice(templates)
                        plan["exercises"].append({
                            "language": lang,
                            "difficulty": difficulty,
                            "template": selected_exercise
                        })
                        plan["estimated_time"] += selected_exercise.get("time_limit", 30)
        
        # Add advanced exercises if user shows strong skills
        advanced_skills = [skill for skill, level in skill_vector.items() if level > 0.8]
        if advanced_skills and len(plan["exercises"]) >= 2:
            for lang in programming_langs[:1]:  # One advanced exercise
                if lang in self.exercise_templates and "advanced" in self.exercise_templates[lang]:
                    templates = self.exercise_templates[lang]["advanced"]
                    if templates:
                        selected_exercise = random.choice(templates)
                        plan["exercises"].append({
                            "language": lang,
                            "difficulty": "advanced",
                            "template": selected_exercise
                        })
                        plan["estimated_time"] += selected_exercise.get("time_limit", 45)
        
        return plan
    
    def _generate_next_exercise(self, user_id: str, assessment_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate the next exercise for the user"""
        plan = assessment_state.get("assessment_plan", {})
        exercises_completed = assessment_state.get("exercises_completed", 0)
        planned_exercises = plan.get("exercises", [])
        
        if exercises_completed >= len(planned_exercises):
            return None
        
        exercise_plan = planned_exercises[exercises_completed]
        template = exercise_plan["template"]
        
        # Create exercise instance
        exercise = {
            "id": f"{user_id}_exercise_{exercises_completed}",
            "language": exercise_plan["language"],
            "difficulty": exercise_plan["difficulty"],
            "title": template["title"],
            "description": template["description"],
            "starter_code": template["starter_code"],
            "test_cases": template["test_cases"],
            "skills": template["skills"],
            "time_limit": template["time_limit"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        return exercise
    
    def _evaluate_solution(self, solution_code: str, exercise: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate submitted solution code"""
        if not solution_code or not exercise:
            return {"score": 0, "feedback": ["No solution provided"]}
        
        feedback = []
        score_components = {}
        
        # Basic correctness check (simplified)
        correctness_score = self._check_correctness(solution_code, exercise.get("test_cases", []))
        score_components["correctness"] = correctness_score
        
        if correctness_score > 0:
            feedback.append("✓ Basic functionality implemented")
        else:
            feedback.append("✗ Solution doesn't meet basic requirements")
        
        # Code quality assessment
        quality_score = self._assess_code_quality(solution_code)
        score_components["code_quality"] = quality_score
        
        if quality_score > 0.7:
            feedback.append("✓ Good code structure and readability")
        elif quality_score > 0.4:
            feedback.append("△ Code could be more readable")
        else:
            feedback.append("✗ Consider improving code structure")
        
        # Efficiency assessment (simplified)
        efficiency_score = self._assess_efficiency(solution_code, exercise.get("skills", []))
        score_components["efficiency"] = efficiency_score
        
        if efficiency_score > 0.7:
            feedback.append("✓ Efficient algorithm implementation")
        
        # Calculate total score
        total_score = 0
        for criterion, weight in self.scoring_criteria.items():
            component_score = score_components.get(criterion, 0.5)  # Default to 50%
            total_score += component_score * weight
        
        # Convert to 0-100 scale
        final_score = int(total_score * 100)
        
        return {
            "score": final_score,
            "score_components": score_components,
            "feedback": feedback,
            "evaluation_timestamp": datetime.utcnow().isoformat()
        }
    
    def _check_correctness(self, code: str, test_cases: List[Dict[str, Any]]) -> float:
        """Basic correctness checking (simplified for demo)"""
        if not code or len(code.strip()) < 10:
            return 0.0
        
        # Basic checks
        correctness_indicators = 0
        total_checks = 4
        
        # Check if function is defined
        if "def " in code or "function " in code:
            correctness_indicators += 1
        
        # Check if return statement exists
        if "return " in code:
            correctness_indicators += 1
        
        # Check for basic logic patterns
        if any(keyword in code for keyword in ["if", "for", "while", "in"]):
            correctness_indicators += 1
        
        # Check if it's not just a placeholder
        if "pass" not in code and "todo" not in code.lower():
            correctness_indicators += 1
        
        return correctness_indicators / total_checks
    
    def _assess_code_quality(self, code: str) -> float:
        """Assess code quality factors"""
        if not code:
            return 0.0
        
        quality_score = 0.0
        factors = 0
        
        # Check indentation consistency
        lines = code.split('\n')
        indented_lines = [line for line in lines if line.strip() and line.startswith('    ')]
        if indented_lines:
            quality_score += 0.2
        factors += 1
        
        # Check for meaningful variable names
        words = code.split()
        meaningful_vars = [word for word in words if len(word) > 3 and word.isalpha()]
        if len(meaningful_vars) > 0:
            quality_score += 0.3
        factors += 1
        
        # Check for comments or docstrings
        if "#" in code or '"""' in code or "'''" in code:
            quality_score += 0.2
        factors += 1
        
        # Check code length (not too short, not too long)
        if 20 <= len(code) <= 500:
            quality_score += 0.3
        factors += 1
        
        return quality_score if factors == 0 else quality_score
    
    def _assess_efficiency(self, code: str, skills: List[str]) -> float:
        """Assess algorithm efficiency (simplified)"""
        if not code:
            return 0.0
        
        efficiency_score = 0.5  # Base score
        
        # Check for efficient patterns based on skills
        if "algorithms" in skills:
            if "binary" in code.lower() or "log" in code.lower():
                efficiency_score += 0.3
            if "sort" in code.lower() and "sorted(" in code:
                efficiency_score += 0.2
        
        if "data_structures" in skills:
            if any(ds in code for ds in ["dict", "set", "deque"]):
                efficiency_score += 0.2
        
        # Penalize inefficient patterns
        if code.count("for") > 2:  # Nested loops indication
            efficiency_score -= 0.1
        
        return min(efficiency_score, 1.0)
    
    def _calculate_adaptive_difficulty(self, performance_data: Dict[str, Any], 
                                     current_difficulty: str) -> str:
        """Calculate adaptive difficulty based on performance"""
        avg_score = performance_data.get("average_score", 50)
        completion_time = performance_data.get("completion_time", 30)  # minutes
        
        difficulty_levels = ["beginner", "intermediate", "advanced", "expert"]
        current_index = difficulty_levels.index(current_difficulty) if current_difficulty in difficulty_levels else 0
        
        # Increase difficulty if performing well
        if avg_score > 85 and completion_time < 20:
            new_index = min(current_index + 1, len(difficulty_levels) - 1)
        # Decrease difficulty if struggling
        elif avg_score < 50 and completion_time > 40:
            new_index = max(current_index - 1, 0)
        else:
            new_index = current_index
        
        return difficulty_levels[new_index]
    
    def _finalize_assessment(self, user_id: str, assessment_state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize assessment and generate results"""
        exercises_completed = assessment_state.get("exercises_completed", 0)
        total_score = assessment_state.get("total_score", 0)
        
        if exercises_completed == 0:
            average_score = 0
        else:
            average_score = total_score / exercises_completed
        
        # Calculate skill levels based on performance
        skill_levels = {}
        plan = assessment_state.get("assessment_plan", {})
        
        for exercise_plan in plan.get("exercises", []):
            language = exercise_plan.get("language", "unknown")
            difficulty = exercise_plan.get("difficulty", "beginner")
            
            # Simplified skill level calculation
            if average_score >= 80:
                skill_levels[language] = "proficient"
            elif average_score >= 60:
                skill_levels[language] = "intermediate"
            else:
                skill_levels[language] = "beginner"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(average_score, skill_levels)
        
        final_results = {
            "user_id": user_id,
            "assessment_id": f"assessment_{user_id}_{datetime.utcnow().timestamp()}",
            "total_exercises": exercises_completed,
            "average_score": round(average_score, 2),
            "skill_levels": skill_levels,
            "recommendations": recommendations,
            "completed_at": datetime.utcnow().isoformat(),
            "assessment_duration": assessment_state.get("start_time", ""),
            "performance_tier": self._get_performance_tier(average_score)
        }
        
        # Update state with final results
        assessment_state.update({
            "status": "completed",
            "final_results": final_results
        })
        self.update_state(user_id, assessment_state)
        
        return final_results
    
    def _generate_recommendations(self, average_score: float, 
                                skill_levels: Dict[str, str]) -> List[str]:
        """Generate learning recommendations based on assessment results"""
        recommendations = []
        
        if average_score < 60:
            recommendations.extend([
                "Focus on fundamental programming concepts",
                "Practice basic data structures and algorithms",
                "Complete beginner-level coding exercises daily"
            ])
        elif average_score < 80:
            recommendations.extend([
                "Strengthen intermediate programming skills",
                "Learn about time and space complexity",
                "Practice with real-world coding problems"
            ])
        else:
            recommendations.extend([
                "Explore advanced algorithms and data structures",
                "Practice system design concepts",
                "Consider contributing to open source projects"
            ])
        
        # Skill-specific recommendations
        for skill, level in skill_levels.items():
            if level == "beginner":
                recommendations.append(f"Take a comprehensive {skill} course")
            elif level == "intermediate":
                recommendations.append(f"Practice advanced {skill} concepts")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _get_performance_tier(self, average_score: float) -> str:
        """Get performance tier based on average score"""
        if average_score >= 90:
            return "Expert"
        elif average_score >= 80:
            return "Advanced"
        elif average_score >= 65:
            return "Intermediate"
        elif average_score >= 50:
            return "Beginner+"
        else:
            return "Beginner"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": "AssessmentAgent",
            "version": "1.0.0",
            "capabilities": [
                "exercise_generation",
                "solution_evaluation",
                "adaptive_difficulty",
                "performance_analytics",
                "skill_assessment"
            ],
            "supported_languages": list(self.exercise_templates.keys()),
            "difficulty_levels": ["beginner", "intermediate", "advanced", "expert"],
            "scoring_criteria": self.scoring_criteria,
            "supported_events": [
                "skills.extracted",
                "assessment.start_requested", 
                "exercise.solution_submitted",
                "assessment.adaptive_adjustment"
            ],
            "emitted_events": [
                "assessment.ready",
                "exercise.generated",
                "assessment.completed"
            ]
        }