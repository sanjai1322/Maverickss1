"""
Business Logic and Service Layer
===============================

This file contains all the business logic and utility functions that support
the application's core functionality:

1. File Processing Services:
   - Resume text extraction from PDF, Word, and text files
   - File validation and security checks

2. Skill Analysis Services:
   - Skill extraction from resume text using keyword matching
   - Skill validation and categorization

3. Assessment Services:
   - Assessment scoring algorithms
   - Quiz response evaluation
   - Progress calculation

4. Learning Path Services:
   - Automated learning path generation
   - Module recommendation
   - Progress tracking

5. AI Integration Services:
   - Course generation using AI
   - Content personalization
   - Recommendation algorithms

Each service function includes detailed documentation explaining:
- What it does
- Input parameters and expected types
- Return values and formats
- Error handling approach
"""

import json
import logging
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Set up logging for this module
logger = logging.getLogger(__name__)

# Constants for file processing
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB maximum file size

# Constants for skill extraction
COMMON_SKILLS = [
    'python', 'java', 'javascript', 'react', 'flask', 'django', 'sql', 'html', 'css', 'git',
    'node.js', 'angular', 'vue', 'postgresql', 'mysql', 'mongodb', 'docker', 'kubernetes',
    'aws', 'azure', 'machine learning', 'data science', 'api', 'rest', 'microservices',
    'typescript', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust', 'swift', 'tensorflow',
    'pytorch', 'redis', 'elasticsearch', 'jenkins', 'gitlab', 'linux', 'bash'
]

# Constants for assessment scoring
TECHNICAL_KEYWORDS = [
    'algorithm', 'database', 'framework', 'api', 'testing', 'debugging', 'optimization',
    'architecture', 'scalability', 'performance', 'security', 'agile', 'git', 'deployment',
    'containerization', 'microservices', 'devops', 'ci/cd', 'monitoring', 'logging'
]


# ============================================================================
# FILE PROCESSING SERVICES
# ============================================================================

def extract_text_from_file(file) -> Optional[str]:
    """
    Extract text content from uploaded resume files.
    
    Supports multiple file formats and provides robust error handling.
    This is a critical function that processes user-uploaded resumes.
    
    Args:
        file: Uploaded file object from Flask request.files
        
    Returns:
        str: Extracted text content from the file, or None if extraction fails
        
    Raises:
        None - All exceptions are caught and logged, function returns None on error
    """
    if not file or not file.filename:
        logger.warning("No file provided for text extraction")
        return None
    
    filename = secure_filename(file.filename)
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    logger.info(f"Attempting to extract text from file: {filename} (type: {file_ext})")
    
    try:
        if file_ext == 'pdf':
            return _extract_from_pdf(file)
        elif file_ext in ['doc', 'docx']:
            return _extract_from_word(file)
        elif file_ext == 'txt':
            return _extract_from_text(file)
        else:
            # Try to read as text for unknown file types
            return _extract_as_fallback_text(file)
            
    except Exception as e:
        logger.error(f"Error extracting text from file {filename}: {str(e)}")
        return None


def _extract_from_pdf(file) -> str:
    """Extract text from PDF files using PyPDF2."""
    pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
    text = ""
    
    for page_num, page in enumerate(pdf_reader.pages):
        try:
            page_text = page.extract_text()
            text += page_text + "\n"
        except Exception as e:
            logger.warning(f"Error extracting text from PDF page {page_num}: {e}")
            continue
    
    logger.info(f"Extracted {len(text)} characters from PDF")
    return text.strip()


def _extract_from_word(file) -> str:
    """Extract text from Word documents (.doc/.docx) using python-docx."""
    doc = Document(BytesIO(file.read()))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    logger.info(f"Extracted {len(text)} characters from Word document")
    return text.strip()


def _extract_from_text(file) -> str:
    """Extract text from plain text files."""
    text = file.read().decode('utf-8')
    
    logger.info(f"Read {len(text)} characters from text file")
    return text.strip()


def _extract_as_fallback_text(file) -> Optional[str]:
    """Try to read unknown file types as text files."""
    try:
        text = file.read().decode('utf-8')
        logger.info(f"Read file as text: {len(text)} characters")
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to read file as text: {e}")
        return None


def allowed_file(filename: str) -> bool:
    """
    Check if uploaded file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def validate_file_size(file, max_size: int = MAX_FILE_SIZE) -> bool:
    """
    Validate that uploaded file doesn't exceed size limits.
    
    Args:
        file: Uploaded file object
        max_size: Maximum allowed file size in bytes
        
    Returns:
        bool: True if file size is acceptable, False otherwise
    """
    if not hasattr(file, 'seek') or not hasattr(file, 'tell'):
        return True  # Can't check size, assume it's okay
    
    try:
        # Get current position
        current_pos = file.tell()
        
        # Seek to end to get file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        
        # Return to original position
        file.seek(current_pos)
        
        return file_size <= max_size
    except Exception as e:
        logger.warning(f"Could not validate file size: {e}")
        return True  # If we can't check, assume it's okay


# ============================================================================
# SKILL ANALYSIS SERVICES
# ============================================================================

def extract_skills_from_resume(resume_text: str) -> str:
    """
    Extract key technical skills from resume using intelligent keyword matching.
    
    This function analyzes resume text to identify technical skills, programming
    languages, frameworks, and tools mentioned. It uses a comprehensive list
    of industry-standard skills and returns a formatted string.
    
    Args:
        resume_text: The complete resume content to analyze
        
    Returns:
        str: Comma-separated list of identified skills, or default message if none found
    """
    if not resume_text or len(resume_text.strip()) < 10:
        logger.warning("Resume text too short for skill extraction")
        return 'General Programming Skills'
    
    found_skills = []
    resume_lower = resume_text.lower()
    
    # Track skill categories for better organization
    skill_categories = {
        'programming_languages': [],
        'frameworks': [],
        'databases': [],
        'tools': [],
        'cloud_platforms': [],
        'other': []
    }
    
    # Categorize skills as we find them
    for skill in COMMON_SKILLS:
        if skill.lower() in resume_lower:
            skill_title = skill.title()
            found_skills.append(skill_title)
            
            # Categorize the skill for better analysis
            if skill in ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust', 'swift']:
                skill_categories['programming_languages'].append(skill_title)
            elif skill in ['react', 'flask', 'django', 'angular', 'vue', 'tensorflow', 'pytorch']:
                skill_categories['frameworks'].append(skill_title)
            elif skill in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch']:
                skill_categories['databases'].append(skill_title)
            elif skill in ['git', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'linux', 'bash']:
                skill_categories['tools'].append(skill_title)
            elif skill in ['aws', 'azure']:
                skill_categories['cloud_platforms'].append(skill_title)
            else:
                skill_categories['other'].append(skill_title)
    
    # Generate result with fallback
    if found_skills:
        result = ', '.join(sorted(found_skills))
        logger.info(f"Extracted {len(found_skills)} skills from resume: {result}")
        
        # Log skill distribution for analytics
        category_counts = {cat: len(skills) for cat, skills in skill_categories.items() if skills}
        logger.debug(f"Skill distribution: {category_counts}")
        
        return result
    else:
        logger.info("No specific technical skills found in resume, using default")
        return 'General Programming Skills'


def categorize_skills(skills_string: str) -> Dict[str, List[str]]:
    """
    Categorize a comma-separated list of skills into logical groups.
    
    Args:
        skills_string: Comma-separated string of skills
        
    Returns:
        dict: Skills organized by category
    """
    if not skills_string:
        return {}
    
    skills = [skill.strip() for skill in skills_string.split(',')]
    categories = {
        'Programming Languages': [],
        'Frameworks & Libraries': [],
        'Databases': [],
        'Tools & Platforms': [],
        'Cloud Services': [],
        'Other': []
    }
    
    for skill in skills:
        skill_lower = skill.lower()
        
        if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'swift']):
            categories['Programming Languages'].append(skill)
        elif any(fw in skill_lower for fw in ['react', 'flask', 'django', 'angular', 'vue', 'tensorflow', 'pytorch', 'express', 'spring']):
            categories['Frameworks & Libraries'].append(skill)
        elif any(db in skill_lower for db in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'oracle']):
            categories['Databases'].append(skill)
        elif any(tool in skill_lower for tool in ['git', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'linux', 'bash', 'npm', 'webpack']):
            categories['Tools & Platforms'].append(skill)
        elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'heroku', 'digitalocean']):
            categories['Cloud Services'].append(skill)
        else:
            categories['Other'].append(skill)
    
    # Remove empty categories
    return {cat: skills for cat, skills in categories.items() if skills}


# ============================================================================
# ASSESSMENT SERVICES
# ============================================================================

def calculate_assessment_score(quiz_responses: Dict[str, str]) -> Tuple[int, Dict[str, Any]]:
    """
    Calculate comprehensive assessment score based on response quality and technical depth.
    
    Scoring algorithm breakdown:
    - Base score: 60 points (for participation)
    - Length bonus: Up to 30 points for detailed responses
    - Technical keyword bonus: Up to 10 points for technical terminology
    - Quality indicators: Additional analysis for depth and accuracy
    
    Args:
        quiz_responses: Dictionary mapping questions to user responses
        
    Returns:
        tuple: (final_score, detailed_breakdown)
            - final_score: Integer score from 0-100
            - detailed_breakdown: Dictionary with scoring details and analysis
    """
    if not quiz_responses:
        logger.warning("No quiz responses provided for scoring")
        return 0, {'error': 'No responses provided'}
    
    base_score = 60  # Participation points
    max_length_bonus = 30
    max_keyword_bonus = 10
    
    # Calculate total response length
    total_length = sum(len(str(response).strip()) for response in quiz_responses.values())
    
    # Length-based scoring: reward detailed responses
    length_bonus = min(max_length_bonus, total_length // 50)
    
    # Technical keyword scoring: reward technical depth
    keyword_count = 0
    found_keywords = []
    
    for response in quiz_responses.values():
        if not response:
            continue
            
        response_lower = str(response).lower()
        for keyword in TECHNICAL_KEYWORDS:
            if keyword in response_lower and keyword not in found_keywords:
                keyword_count += 1
                found_keywords.append(keyword)
    
    keyword_bonus = min(max_keyword_bonus, keyword_count * 2)
    
    # Quality indicators analysis
    quality_indicators = _analyze_response_quality(quiz_responses)
    
    # Calculate final score
    final_score = base_score + length_bonus + keyword_bonus
    final_score = min(100, final_score)  # Cap at 100
    
    # Detailed breakdown for analytics and feedback
    breakdown = {
        'final_score': final_score,
        'base_score': base_score,
        'length_bonus': length_bonus,
        'keyword_bonus': keyword_bonus,
        'total_length': total_length,
        'keyword_count': keyword_count,
        'found_keywords': found_keywords,
        'quality_indicators': quality_indicators,
        'scoring_details': {
            'participation': base_score,
            'detail_level': length_bonus,
            'technical_depth': keyword_bonus
        }
    }
    
    logger.info(f"Assessment scoring complete: base={base_score}, length_bonus={length_bonus}, "
               f"keyword_bonus={keyword_bonus}, final={final_score}")
    
    return final_score, breakdown


def _analyze_response_quality(responses: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyze the quality of assessment responses for additional insights.
    
    Args:
        responses: Dictionary of question-response pairs
        
    Returns:
        dict: Quality analysis including various indicators
    """
    quality_metrics = {
        'average_response_length': 0,
        'empty_responses': 0,
        'detailed_responses': 0,
        'technical_terms_used': 0,
        'overall_engagement': 'low'
    }
    
    if not responses:
        return quality_metrics
    
    total_responses = len(responses)
    total_length = 0
    empty_count = 0
    detailed_count = 0
    
    for response in responses.values():
        response_str = str(response).strip()
        response_length = len(response_str)
        total_length += response_length
        
        if response_length == 0:
            empty_count += 1
        elif response_length > 100:  # Consider responses over 100 chars as detailed
            detailed_count += 1
    
    quality_metrics['average_response_length'] = total_length // total_responses if total_responses > 0 else 0
    quality_metrics['empty_responses'] = empty_count
    quality_metrics['detailed_responses'] = detailed_count
    
    # Determine overall engagement level
    if empty_count == total_responses:
        quality_metrics['overall_engagement'] = 'none'
    elif empty_count > total_responses // 2:
        quality_metrics['overall_engagement'] = 'low'
    elif detailed_count > total_responses // 2:
        quality_metrics['overall_engagement'] = 'high'
    else:
        quality_metrics['overall_engagement'] = 'medium'
    
    return quality_metrics


def generate_assessment_feedback(score: int, breakdown: Dict[str, Any]) -> str:
    """
    Generate personalized feedback based on assessment performance.
    
    Args:
        score: Final assessment score
        breakdown: Detailed scoring breakdown
        
    Returns:
        str: Personalized feedback message
    """
    if score >= 90:
        feedback = "Excellent work! Your responses demonstrate strong technical knowledge and attention to detail."
    elif score >= 80:
        feedback = "Great job! You show solid understanding with room for even more detailed explanations."
    elif score >= 70:
        feedback = "Good performance! Consider providing more technical details in your responses."
    elif score >= 60:
        feedback = "Nice effort! Focus on expanding your answers with more specific technical information."
    else:
        feedback = "Keep learning! Try to provide more comprehensive responses that demonstrate your technical understanding."
    
    # Add specific suggestions based on breakdown
    suggestions = []
    
    if breakdown.get('length_bonus', 0) < 15:
        suggestions.append("Provide more detailed explanations in your responses.")
    
    if breakdown.get('keyword_bonus', 0) < 5:
        suggestions.append("Include more technical terminology to demonstrate your knowledge.")
    
    if breakdown.get('quality_indicators', {}).get('empty_responses', 0) > 0:
        suggestions.append("Try to answer all questions to maximize your score.")
    
    if suggestions:
        feedback += " Suggestions for improvement: " + " ".join(suggestions)
    
    return feedback


# ============================================================================
# LEARNING PATH SERVICES
# ============================================================================

def generate_learning_paths(username: str, skills: str) -> List[Dict[str, Any]]:
    """
    Generate personalized learning paths based on extracted skills.
    
    Creates a customized curriculum of learning modules that build upon
    the user's existing skills and address identified gaps.
    
    Args:
        username: User's username for personalization
        skills: Comma-separated string of user's skills
        
    Returns:
        list: List of learning path modules with details
    """
    if not username or not skills:
        logger.warning(f"Invalid parameters for learning path generation: username={username}, skills={skills}")
        return []
    
    skill_list = [skill.strip().lower() for skill in skills.split(',')]
    learning_modules = []
    
    # Define learning paths based on skill combinations
    learning_templates = {
        'python_backend': {
            'condition': lambda skills: 'python' in skills,
            'modules': [
                {'name': 'Advanced Python Concepts', 'time': 180, 'description': 'Deep dive into Python advanced features'},
                {'name': 'Web API Development with Flask', 'time': 240, 'description': 'Build robust REST APIs'},
                {'name': 'Database Integration', 'time': 200, 'description': 'Connect Python apps to databases'},
                {'name': 'Testing and Debugging', 'time': 150, 'description': 'Write comprehensive tests'}
            ]
        },
        'javascript_frontend': {
            'condition': lambda skills: 'javascript' in skills or 'react' in skills,
            'modules': [
                {'name': 'Modern JavaScript (ES6+)', 'time': 160, 'description': 'Master latest JavaScript features'},
                {'name': 'React.js Components', 'time': 220, 'description': 'Build dynamic user interfaces'},
                {'name': 'State Management', 'time': 180, 'description': 'Handle complex application state'},
                {'name': 'Frontend Testing', 'time': 140, 'description': 'Test React components and logic'}
            ]
        },
        'data_science': {
            'condition': lambda skills: any(skill in skills for skill in ['machine learning', 'data science', 'python']),
            'modules': [
                {'name': 'Data Analysis with Pandas', 'time': 200, 'description': 'Manipulate and analyze data'},
                {'name': 'Machine Learning Basics', 'time': 300, 'description': 'Introduction to ML algorithms'},
                {'name': 'Data Visualization', 'time': 150, 'description': 'Create compelling data visualizations'},
                {'name': 'Statistical Analysis', 'time': 180, 'description': 'Apply statistics to data problems'}
            ]
        },
        'fullstack_web': {
            'condition': lambda skills: len(set(skills) & {'javascript', 'python', 'sql', 'html', 'css'}) >= 3,
            'modules': [
                {'name': 'Full-Stack Architecture', 'time': 240, 'description': 'Design complete web applications'},
                {'name': 'Frontend-Backend Integration', 'time': 200, 'description': 'Connect frontend and backend'},
                {'name': 'Database Design', 'time': 180, 'description': 'Design efficient database schemas'},
                {'name': 'Deployment and DevOps', 'time': 220, 'description': 'Deploy applications to production'}
            ]
        },
        'general_programming': {
            'condition': lambda skills: True,  # Always applicable as fallback
            'modules': [
                {'name': 'Programming Fundamentals', 'time': 120, 'description': 'Core programming concepts'},
                {'name': 'Problem Solving Techniques', 'time': 150, 'description': 'Approach to solving coding problems'},
                {'name': 'Code Quality and Best Practices', 'time': 180, 'description': 'Write clean, maintainable code'},
                {'name': 'Version Control with Git', 'time': 100, 'description': 'Master Git workflow and collaboration'}
            ]
        }
    }
    
    # Find matching learning paths
    matched_paths = []
    for path_name, path_config in learning_templates.items():
        if path_config['condition'](skill_list):
            matched_paths.append((path_name, path_config))
    
    # If no specific paths match, use general programming
    if not matched_paths or len(matched_paths) == 1 and matched_paths[0][0] == 'general_programming':
        matched_paths = [('general_programming', learning_templates['general_programming'])]
    
    # Generate modules from matched paths
    for path_name, path_config in matched_paths[:2]:  # Limit to 2 paths to avoid overwhelming
        for module in path_config['modules']:
            learning_modules.append({
                'username': username,
                'module_name': module['name'],
                'estimated_time': module['time'],
                'description': module['description'],
                'path_category': path_name.replace('_', ' ').title(),
                'completion_status': 'Not Started'
            })
    
    logger.info(f"Generated {len(learning_modules)} learning modules for {username} "
               f"based on skills: {skills}")
    
    return learning_modules


def save_learning_paths_to_db(learning_modules: List[Dict[str, Any]]):
    """
    Save generated learning paths to the database.
    
    Args:
        learning_modules: List of learning module dictionaries
    """
    from backend.database import LearningPath
    from app import db
    
    try:
        for module_data in learning_modules:
            # Check if module already exists
            existing = LearningPath.query.filter_by(
                username=module_data['username'],
                module_name=module_data['module_name']
            ).first()
            
            if not existing:
                learning_path = LearningPath(
                    username=module_data['username'],
                    module_name=module_data['module_name'],
                    estimated_time=module_data['estimated_time'],
                    completion_status=module_data['completion_status']
                )
                db.session.add(learning_path)
        
        db.session.commit()
        logger.info(f"Saved {len(learning_modules)} learning modules to database")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving learning paths to database: {e}")
        raise


# ============================================================================
# AI INTEGRATION SERVICES
# ============================================================================

def generate_tailored_courses(username: str, resume_text: str, skills: str) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered personalized courses based on user profile.
    
    This function integrates with AI services to create customized learning
    content that matches the user's skill level and learning objectives.
    
    Args:
        username: User's username
        resume_text: Full resume content for context
        skills: Extracted skills string
        
    Returns:
        dict: Generated course data, or None if generation fails
    """
    try:
        # Import AI course generator (avoiding circular imports)
        from ai_course_generator import CourseGenerator
        
        generator = CourseGenerator()
        course_data = generator.generate_course(username, resume_text, skills)
        
        if course_data:
            logger.info(f"Generated AI course for {username}: {course_data.get('title', 'Unknown')}")
            return course_data
        else:
            logger.warning(f"AI course generation failed for {username}")
            return None
            
    except Exception as e:
        logger.error(f"Error in AI course generation for {username}: {e}")
        return None


def analyze_learning_progress(username: str) -> Dict[str, Any]:
    """
    Analyze user's learning progress and generate insights.
    
    Args:
        username: User's username
        
    Returns:
        dict: Progress analysis with recommendations
    """
    from backend.database import User, LearningPath, AssessmentAttempt
    
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'error': 'User not found'}
        
        # Get learning paths and progress
        learning_paths = LearningPath.query.filter_by(username=username).all()
        assessment_attempts = AssessmentAttempt.query.filter_by(username=username).all()
        
        # Calculate progress metrics
        total_modules = len(learning_paths)
        completed_modules = len([lp for lp in learning_paths if lp.completion_status == 'Completed'])
        in_progress_modules = len([lp for lp in learning_paths if lp.completion_status == 'In Progress'])
        
        completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        # Assessment analysis
        latest_assessment = max(assessment_attempts, key=lambda x: x.started_at) if assessment_attempts else None
        assessment_score = latest_assessment.total_score if latest_assessment else None
        
        # Generate recommendations
        recommendations = _generate_learning_recommendations(
            completion_rate, assessment_score, user.skills, learning_paths
        )
        
        progress_analysis = {
            'username': username,
            'total_modules': total_modules,
            'completed_modules': completed_modules,
            'in_progress_modules': in_progress_modules,
            'completion_rate': round(completion_rate, 2),
            'latest_assessment_score': assessment_score,
            'total_points': user.total_points,
            'current_level': user.current_level,
            'recommendations': recommendations,
            'analysis_date': datetime.utcnow().isoformat()
        }
        
        return progress_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing learning progress for {username}: {e}")
        return {'error': 'Analysis failed'}


def _generate_learning_recommendations(completion_rate: float, assessment_score: Optional[int], 
                                     skills: str, learning_paths: List) -> List[str]:
    """Generate personalized learning recommendations based on progress data."""
    recommendations = []
    
    if completion_rate < 25:
        recommendations.append("Start with the first module in your learning path to build momentum.")
    elif completion_rate < 50:
        recommendations.append("You're making good progress! Continue with your current modules.")
    elif completion_rate < 75:
        recommendations.append("Great progress! Focus on completing your remaining modules.")
    else:
        recommendations.append("Excellent progress! Consider exploring advanced topics or new skill areas.")
    
    if assessment_score and assessment_score < 70:
        recommendations.append("Review fundamental concepts before moving to advanced topics.")
    elif assessment_score and assessment_score > 85:
        recommendations.append("Your strong assessment performance suggests you're ready for challenging projects.")
    
    # Skill-specific recommendations
    if skills and 'python' in skills.lower():
        recommendations.append("Consider building a Python project to apply your skills practically.")
    
    if not learning_paths:
        recommendations.append("Complete your profile assessment to receive personalized learning paths.")
    
    return recommendations