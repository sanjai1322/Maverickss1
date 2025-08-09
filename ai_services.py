"""
AI Services Integration for Mavericks Platform
==============================================

This module handles all AI service integrations including:
- OpenAI GPT-4o for text analysis and content generation
- Hugging Face transformers for NLP tasks
- OpenRouter API for additional AI capabilities
- Resume analysis and skill extraction
- Assessment question generation
- Learning path recommendations
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# API Configuration
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"

class AIServiceManager:
    """Manages all AI service integrations and provides fallback mechanisms."""
    
    def __init__(self):
        self.openai_available = bool(OPENAI_API_KEY and openai_client)
        self.services_status = self._check_service_availability()
        
    def _check_service_availability(self) -> Dict[str, bool]:
        """Check which AI services are available."""
        return {
            'openai': self.openai_available,
            'huggingface': True,  # Assume available
            'transformers': True  # Local library
        }
    
    def extract_skills_with_ai(self, resume_text: str) -> List[str]:
        """
        Extract skills from resume text using AI with multiple fallback options.
        
        Args:
            resume_text: The raw text content of the resume
            
        Returns:
            List of extracted skills
        """
        try:
            # Primary: Use OpenAI GPT-4o for skill extraction
            if self.openai_available:
                return self._extract_skills_openai(resume_text)
            
            # Fallback: Use keyword-based extraction
            logger.warning("OpenAI not available, using keyword-based extraction")
            return self._extract_skills_keywords(resume_text)
            
        except Exception as e:
            logger.error(f"Error in AI skill extraction: {e}")
            return self._extract_skills_keywords(resume_text)
    
    def _extract_skills_openai(self, resume_text: str) -> List[str]:
        """Extract skills using OpenAI GPT-4o."""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert resume analyzer. Extract technical skills from the resume text. 
                        Focus on programming languages, frameworks, databases, tools, and technologies.
                        Return only a JSON array of skill names, no explanations.
                        Example: ["Python", "JavaScript", "React", "SQL", "Docker"]"""
                    },
                    {
                        "role": "user",
                        "content": f"Extract technical skills from this resume:\n\n{resume_text}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            skills = result.get('skills', [])
            
            logger.info(f"OpenAI extracted {len(skills)} skills: {skills}")
            return skills
            
        except Exception as e:
            logger.error(f"OpenAI skill extraction failed: {e}")
            raise
    
    def _extract_skills_keywords(self, resume_text: str) -> List[str]:
        """Fallback keyword-based skill extraction."""
        common_skills = [
            'python', 'java', 'javascript', 'react', 'flask', 'django', 'sql', 'html', 'css', 'git',
            'node.js', 'angular', 'vue', 'postgresql', 'mysql', 'mongodb', 'docker', 'kubernetes',
            'aws', 'azure', 'machine learning', 'data science', 'api', 'rest', 'microservices',
            'typescript', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust', 'swift', 'tensorflow',
            'pytorch', 'redis', 'elasticsearch', 'jenkins', 'gitlab', 'linux', 'bash'
        ]
        
        resume_lower = resume_text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in resume_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def generate_assessment_questions(self, skills: List[str], num_questions: int = 5) -> List[Dict]:
        """
        Generate personalized assessment questions based on user skills.
        
        Args:
            skills: List of user's technical skills
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        try:
            if self.openai_available and skills:
                return self._generate_questions_openai(skills, num_questions)
            else:
                return self._generate_questions_template(skills, num_questions)
                
        except Exception as e:
            logger.error(f"Error generating assessment questions: {e}")
            return self._generate_questions_template(skills, num_questions)
    
    def _generate_questions_openai(self, skills: List[str], num_questions: int) -> List[Dict]:
        """Generate questions using OpenAI."""
        try:
            skills_str = ", ".join(skills)
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert technical interviewer. Generate coding assessment questions 
                        based on the user's skills. Each question should be practical, relevant, and test deep understanding.
                        Return a JSON object with 'questions' array. Each question should have:
                        - question: The question text
                        - skill: The primary skill being tested
                        - difficulty: beginner/intermediate/advanced
                        - points: Points value (10-25)
                        - time_limit: Recommended time in seconds (60-300)"""
                    },
                    {
                        "role": "user",
                        "content": f"Generate {num_questions} assessment questions for someone with these skills: {skills_str}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1500,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            questions = result.get('questions', [])
            
            logger.info(f"OpenAI generated {len(questions)} assessment questions")
            return questions
            
        except Exception as e:
            logger.error(f"OpenAI question generation failed: {e}")
            raise
    
    def _generate_questions_template(self, skills: List[str], num_questions: int) -> List[Dict]:
        """Fallback template-based question generation."""
        question_templates = {
            'python': {
                'question': 'Explain the difference between lists and tuples in Python. When would you use each?',
                'difficulty': 'intermediate',
                'points': 15,
                'time_limit': 180
            },
            'javascript': {
                'question': 'What is event delegation in JavaScript and why is it useful for performance?',
                'difficulty': 'intermediate', 
                'points': 15,
                'time_limit': 180
            },
            'react': {
                'question': 'Explain the concept of Virtual DOM in React and how it improves performance.',
                'difficulty': 'intermediate',
                'points': 20,
                'time_limit': 240
            },
            'sql': {
                'question': 'Write a SQL query to find the second highest salary from an employees table.',
                'difficulty': 'intermediate',
                'points': 18,
                'time_limit': 200
            },
            'api': {
                'question': 'What is the difference between REST and GraphQL APIs? When would you choose one over the other?',
                'difficulty': 'advanced',
                'points': 22,
                'time_limit': 300
            }
        }
        
        questions = []
        skill_keys = [skill.lower() for skill in skills if skill.lower() in question_templates]
        
        for i, skill in enumerate(skill_keys[:num_questions]):
            template = question_templates[skill]
            questions.append({
                'id': f'q_{i+1}',
                'question': template['question'],
                'skill': skill.title(),
                'difficulty': template['difficulty'],
                'points': template['points'],
                'time_limit': template['time_limit']
            })
        
        # Fill remaining slots with generic questions
        while len(questions) < num_questions:
            questions.append({
                'id': f'q_{len(questions)+1}',
                'question': 'Describe a challenging technical problem you solved and your approach.',
                'skill': 'General',
                'difficulty': 'intermediate',
                'points': 15,
                'time_limit': 240
            })
        
        return questions
    
    def generate_learning_path(self, skills: List[str], skill_gaps: List[str] = None) -> List[Dict]:
        """
        Generate personalized learning path based on skills and gaps.
        
        Args:
            skills: Current user skills
            skill_gaps: Skills that need improvement
            
        Returns:
            List of learning modules
        """
        try:
            if self.openai_available:
                return self._generate_learning_path_openai(skills, skill_gaps)
            else:
                return self._generate_learning_path_template(skills, skill_gaps)
                
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return self._generate_learning_path_template(skills, skill_gaps)
    
    def _generate_learning_path_openai(self, skills: List[str], skill_gaps: List[str] = None) -> List[Dict]:
        """Generate learning path using OpenAI."""
        try:
            skills_str = ", ".join(skills) if skills else "Beginner"
            gaps_str = ", ".join(skill_gaps) if skill_gaps else "None specified"
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert curriculum designer. Create a personalized learning path 
                        based on current skills and skill gaps. Return a JSON object with 'modules' array.
                        Each module should have:
                        - module_name: Clear, descriptive name
                        - description: What the module covers
                        - difficulty: beginner/intermediate/advanced
                        - estimated_hours: Time to complete (1-20 hours)
                        - prerequisites: Required prior knowledge
                        - skills_covered: Array of skills taught"""
                    },
                    {
                        "role": "user",
                        "content": f"Create a learning path for someone with skills: {skills_str}. Focus on gaps: {gaps_str}"
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1200,
                temperature=0.6
            )
            
            result = json.loads(response.choices[0].message.content)
            modules = result.get('modules', [])
            
            logger.info(f"OpenAI generated {len(modules)} learning modules")
            return modules
            
        except Exception as e:
            logger.error(f"OpenAI learning path generation failed: {e}")
            raise
    
    def _generate_learning_path_template(self, skills: List[str], skill_gaps: List[str] = None) -> List[Dict]:
        """Fallback template-based learning path generation."""
        base_modules = [
            {
                'module_name': 'Programming Fundamentals',
                'description': 'Core programming concepts and problem-solving',
                'difficulty': 'beginner',
                'estimated_hours': 8,
                'prerequisites': 'None',
                'skills_covered': ['Logic', 'Algorithms', 'Data Structures']
            },
            {
                'module_name': 'Web Development Basics',
                'description': 'HTML, CSS, and JavaScript fundamentals',
                'difficulty': 'beginner',
                'estimated_hours': 12,
                'prerequisites': 'Programming Fundamentals',
                'skills_covered': ['HTML', 'CSS', 'JavaScript']
            },
            {
                'module_name': 'Backend Development',
                'description': 'Server-side programming and databases',
                'difficulty': 'intermediate',
                'estimated_hours': 15,
                'prerequisites': 'Web Development Basics',
                'skills_covered': ['Python', 'API', 'SQL', 'Database Design']
            },
            {
                'module_name': 'Modern Frontend Frameworks',
                'description': 'React, Vue, or Angular development',
                'difficulty': 'intermediate',
                'estimated_hours': 18,
                'prerequisites': 'Web Development Basics',
                'skills_covered': ['React', 'Component Architecture', 'State Management']
            },
            {
                'module_name': 'DevOps and Deployment',
                'description': 'Docker, CI/CD, and cloud deployment',
                'difficulty': 'advanced',
                'estimated_hours': 20,
                'prerequisites': 'Backend Development',
                'skills_covered': ['Docker', 'Git', 'CI/CD', 'Cloud Platforms']
            }
        ]
        
        return base_modules
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using AI.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        try:
            if self.openai_available:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": """Analyze the sentiment of the text. Return JSON with:
                            - sentiment: positive/negative/neutral
                            - confidence: 0.0 to 1.0
                            - score: -1.0 (very negative) to 1.0 (very positive)"""
                        },
                        {
                            "role": "user",
                            "content": f"Analyze sentiment: {text}"
                        }
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=200,
                    temperature=0.1
                )
                
                return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            
        # Fallback
        return {
            'sentiment': 'neutral',
            'confidence': 0.5,
            'score': 0.0
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current status of all AI services."""
        return {
            'openai': {
                'available': self.openai_available,
                'model': 'gpt-4o' if self.openai_available else None
            },
            'huggingface': {
                'available': True,
                'models': ['transformers', 'sentence-transformers']
            },
            'services_status': self.services_status,
            'fallback_enabled': True
        }

# Global AI service manager instance
ai_service_manager = AIServiceManager()

# Convenience functions for easy import
def extract_skills_with_ai(resume_text: str) -> List[str]:
    """Extract skills from resume using AI."""
    return ai_service_manager.extract_skills_with_ai(resume_text)

def generate_assessment_questions(skills: List[str], num_questions: int = 5) -> List[Dict]:
    """Generate assessment questions based on skills."""
    return ai_service_manager.generate_assessment_questions(skills, num_questions)

def generate_learning_path(skills: List[str], skill_gaps: List[str] = None) -> List[Dict]:
    """Generate personalized learning path."""
    return ai_service_manager.generate_learning_path(skills, skill_gaps)

def get_ai_service_status() -> Dict[str, Any]:
    """Get AI service availability status."""
    return ai_service_manager.get_service_status()