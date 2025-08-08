"""
Profile Agent
=============

Manages user profiles, skill analysis, and resume processing.
Uses AI/NLP to extract technical skills and generate skill vectors.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

from .base_agent import BaseAgent, AgentEvent

logger = logging.getLogger(__name__)

class ProfileAgent(BaseAgent):
    """
    Profile Agent handles user registration, skill extraction, and profile management.
    
    Capabilities:
    - Resume text analysis and skill extraction
    - User skill vector generation
    - Profile completeness assessment
    - Skill gap analysis
    """
    
    def __init__(self, event_bus=None):
        super().__init__("ProfileAgent", event_bus)
        
        # Subscribe to relevant events
        self.subscribe_to_event("user.registered")
        self.subscribe_to_event("resume.uploaded")
        self.subscribe_to_event("profile.update_requested")
        self.subscribe_to_event("skills.assessment_completed")
        
        # Predefined skill categories and keywords
        self.skill_categories = {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
                "swift", "kotlin", "scala", "ruby", "php", "perl", "r", "matlab"
            ],
            "web_technologies": [
                "html", "css", "react", "angular", "vue", "node.js", "express", "django",
                "flask", "spring", "asp.net", "bootstrap", "tailwind", "sass", "less"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
                "oracle", "sql server", "sqlite", "dynamodb", "neo4j", "influxdb"
            ],
            "cloud_platforms": [
                "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
                "ansible", "jenkins", "gitlab", "github actions", "circleci"
            ],
            "data_science": [
                "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
                "pandas", "numpy", "jupyter", "tableau", "power bi", "spark", "hadoop"
            ],
            "mobile_development": [
                "ios", "android", "react native", "flutter", "xamarin", "ionic",
                "swift", "kotlin", "objective-c", "dart"
            ],
            "devops_tools": [
                "docker", "kubernetes", "jenkins", "gitlab", "github", "terraform",
                "ansible", "chef", "puppet", "nagios", "prometheus", "grafana"
            ],
            "frameworks": [
                "spring boot", "django", "flask", "express", "react", "angular", "vue",
                ".net", "laravel", "rails", "symfony", "fastapi"
            ]
        }
    
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """Process incoming events related to user profiles"""
        try:
            if event.event_type == "user.registered":
                return self._handle_user_registration(event)
            elif event.event_type == "resume.uploaded":
                return self._handle_resume_upload(event)
            elif event.event_type == "profile.update_requested":
                return self._handle_profile_update(event)
            elif event.event_type == "skills.assessment_completed":
                return self._handle_skills_assessment(event)
            else:
                self.logger.warning(f"Unhandled event type: {event.event_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {str(e)}")
            return {"error": str(e)}
    
    def _handle_user_registration(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle new user registration"""
        user_id = event.user_id
        payload = event.payload
        
        # Initialize user profile state
        profile_data = {
            "user_id": user_id,
            "username": payload.get("username", ""),
            "registration_date": datetime.utcnow().isoformat(),
            "profile_completeness": 20,  # Basic registration complete
            "extracted_skills": {},
            "skill_vector": {},
            "last_updated": datetime.utcnow().isoformat()
        }
        
        self.update_state(user_id, profile_data)
        
        # Emit profile created event
        self.emit_event(
            "profile.created",
            None,  # Broadcast to all interested agents
            user_id,
            {
                "username": payload.get("username", ""),
                "profile_completeness": 20,
                "skills_extracted": False
            }
        )
        
        return {"status": "profile_initialized", "completeness": 20}
    
    def _handle_resume_upload(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle resume upload and process for skill extraction"""
        user_id = event.user_id
        payload = event.payload
        resume_text = payload.get("resume_text", "")
        
        if not resume_text:
            return {"error": "No resume text provided"}
        
        # Extract skills from resume text
        extracted_skills = self._extract_skills_from_text(resume_text)
        skill_vector = self._generate_skill_vector(extracted_skills)
        
        # Update user state
        profile_update = {
            "resume_text": resume_text,
            "extracted_skills": extracted_skills,
            "skill_vector": skill_vector,
            "profile_completeness": self._calculate_completeness(extracted_skills),
            "last_updated": datetime.utcnow().isoformat(),
            "skills_extraction_date": datetime.utcnow().isoformat()
        }
        
        self.update_state(user_id, profile_update)
        
        # Emit skills extracted event
        self.emit_event(
            "skills.extracted",
            None,  # Broadcast to learning path and assessment agents
            user_id,
            {
                "extracted_skills": extracted_skills,
                "skill_vector": skill_vector,
                "skill_categories": list(extracted_skills.keys()),
                "total_skills": sum(len(skills) for skills in extracted_skills.values())
            }
        )
        
        return {
            "status": "skills_extracted",
            "extracted_skills": extracted_skills,
            "skill_count": sum(len(skills) for skills in extracted_skills.values()),
            "completeness": profile_update["profile_completeness"]
        }
    
    def _handle_profile_update(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle profile update requests"""
        user_id = event.user_id
        payload = event.payload
        
        # Get current state
        current_state = self.get_state(user_id)
        if not current_state:
            return {"error": "User profile not found"}
        
        # Update fields
        updates = payload.get("updates", {})
        current_state.update(updates)
        current_state["last_updated"] = datetime.utcnow().isoformat()
        
        self.update_state(user_id, current_state)
        
        # If resume text was updated, re-extract skills
        if "resume_text" in updates:
            return self._handle_resume_upload(AgentEvent(
                event_type="resume.uploaded",
                source_agent="ProfileAgent",
                target_agent=None,
                user_id=user_id,
                payload={"resume_text": updates["resume_text"]},
                timestamp=datetime.utcnow(),
                event_id=f"profile_update_{user_id}"
            ))
        
        return {"status": "profile_updated", "updates": list(updates.keys())}
    
    def _handle_skills_assessment(self, event: AgentEvent) -> Dict[str, Any]:
        """Handle completed skills assessment to refine skill vector"""
        user_id = event.user_id
        payload = event.payload
        
        assessment_results = payload.get("assessment_results", {})
        current_state = self.get_state(user_id)
        
        if not current_state:
            return {"error": "User profile not found"}
        
        # Refine skill vector based on assessment performance
        refined_vector = self._refine_skill_vector(
            current_state.get("skill_vector", {}),
            assessment_results
        )
        
        # Update state
        profile_update = {
            "skill_vector": refined_vector,
            "assessment_date": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "profile_completeness": 100  # Assessment complete
        }
        
        self.update_state(user_id, profile_update)
        
        # Emit refined skills event
        self.emit_event(
            "skills.refined",
            None,
            user_id,
            {
                "refined_skill_vector": refined_vector,
                "assessment_scores": assessment_results,
                "profile_completeness": 100
            }
        )
        
        return {"status": "skills_refined", "skill_vector": refined_vector}
    
    def _extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract technical skills from resume text using NLP and keyword matching"""
        text_lower = text.lower()
        extracted_skills = {}
        
        for category, keywords in self.skill_categories.items():
            found_skills = []
            
            for skill in keywords:
                # Use regex for better matching
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            
            if found_skills:
                extracted_skills[category] = found_skills
        
        # Additional NLP-based extraction (simplified version)
        # In production, this would use more sophisticated NLP models
        tech_patterns = [
            r'\b\w+\.js\b',  # JavaScript frameworks/libraries
            r'\bAPI\b',       # API mentions
            r'\bRESTful?\b',  # REST API
            r'\bGraphQL\b',   # GraphQL
            r'\bMicroservices?\b'  # Microservices
        ]
        
        additional_skills = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            additional_skills.extend([match.lower() for match in matches])
        
        if additional_skills:
            extracted_skills["additional_technologies"] = list(set(additional_skills))
        
        return extracted_skills
    
    def _generate_skill_vector(self, extracted_skills: Dict[str, List[str]]) -> Dict[str, float]:
        """Generate numerical skill vector for ML processing"""
        skill_vector = {}
        
        # Weight different categories
        category_weights = {
            "programming_languages": 1.0,
            "web_technologies": 0.8,
            "databases": 0.7,
            "cloud_platforms": 0.9,
            "data_science": 0.9,
            "mobile_development": 0.8,
            "devops_tools": 0.7,
            "frameworks": 0.6,
            "additional_technologies": 0.5
        }
        
        for category, skills in extracted_skills.items():
            weight = category_weights.get(category, 0.5)
            
            # Calculate category strength based on number of skills
            skill_count = len(skills)
            max_skills_in_category = len(self.skill_categories.get(category, []))
            
            if max_skills_in_category > 0:
                category_strength = min(skill_count / max_skills_in_category, 1.0) * weight
            else:
                category_strength = min(skill_count / 10, 1.0) * weight  # Fallback
            
            skill_vector[category] = round(category_strength, 3)
            
            # Add individual skill weights
            for skill in skills:
                skill_vector[f"skill_{skill}"] = weight
        
        return skill_vector
    
    def _calculate_completeness(self, extracted_skills: Dict[str, List[str]]) -> int:
        """Calculate profile completeness percentage"""
        base_score = 40  # Resume uploaded
        
        # Add points for different skill categories
        category_points = min(len(extracted_skills) * 10, 50)  # Max 50 points
        
        # Add points for skill diversity
        total_skills = sum(len(skills) for skills in extracted_skills.values())
        skill_points = min(total_skills * 2, 20)  # Max 20 points
        
        return min(base_score + category_points + skill_points, 100)
    
    def _refine_skill_vector(self, current_vector: Dict[str, float], 
                           assessment_results: Dict[str, Any]) -> Dict[str, float]:
        """Refine skill vector based on assessment performance"""
        refined_vector = current_vector.copy()
        
        # Adjust skills based on assessment scores
        for skill_area, score in assessment_results.items():
            if score >= 0.8:  # High performance
                skill_key = f"skill_{skill_area.lower()}"
                if skill_key in refined_vector:
                    refined_vector[skill_key] = min(refined_vector[skill_key] * 1.2, 1.0)
            elif score < 0.6:  # Low performance
                skill_key = f"skill_{skill_area.lower()}"
                if skill_key in refined_vector:
                    refined_vector[skill_key] = refined_vector[skill_key] * 0.8
        
        return refined_vector
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get complete user profile data"""
        return self.get_state(user_id)
    
    def get_skill_gaps(self, user_id: str, target_skills: List[str]) -> Dict[str, Any]:
        """Identify skill gaps for learning path generation"""
        profile = self.get_state(user_id)
        if not profile:
            return {"error": "Profile not found"}
        
        skill_vector = profile.get("skill_vector", {})
        gaps = []
        
        for target_skill in target_skills:
            skill_key = f"skill_{target_skill.lower()}"
            current_level = skill_vector.get(skill_key, 0.0)
            
            if current_level < 0.7:  # Threshold for proficiency
                gaps.append({
                    "skill": target_skill,
                    "current_level": current_level,
                    "gap_severity": "high" if current_level < 0.3 else "medium"
                })
        
        return {
            "skill_gaps": gaps,
            "total_gaps": len(gaps),
            "profile_completeness": profile.get("profile_completeness", 0)
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities"""
        return {
            "agent_name": "ProfileAgent",
            "version": "1.0.0",
            "capabilities": [
                "skill_extraction",
                "resume_analysis", 
                "profile_management",
                "skill_vector_generation",
                "gap_analysis"
            ],
            "supported_events": [
                "user.registered",
                "resume.uploaded", 
                "profile.update_requested",
                "skills.assessment_completed"
            ],
            "emitted_events": [
                "profile.created",
                "skills.extracted",
                "skills.refined"
            ],
            "skill_categories": list(self.skill_categories.keys()),
            "total_skill_keywords": sum(len(keywords) for keywords in self.skill_categories.values())
        }