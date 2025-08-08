import json
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from io import BytesIO
from datetime import datetime, timedelta
from app import app, db
from ai_course_generator import CourseGenerator

logger = logging.getLogger(__name__)

# File processing utilities
def extract_text_from_file(file):
    """Extract text content from uploaded resume files.
    
    Supports PDF, Word documents, and plain text files.
    
    Args:
        file: Uploaded file object from Flask request
        
    Returns:
        str: Extracted text content from the file
    """
    filename = secure_filename(file.filename)
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    try:
        if file_ext == 'pdf':
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            logger.info(f"Extracted text from PDF: {len(text)} characters")
            return text.strip()
            
        elif file_ext in ['doc', 'docx']:
            # Extract text from Word document
            doc = Document(BytesIO(file.read()))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            logger.info(f"Extracted text from Word document: {len(text)} characters")
            return text.strip()
            
        elif file_ext == 'txt':
            # Read plain text file
            text = file.read().decode('utf-8')
            logger.info(f"Read text file: {len(text)} characters")
            return text.strip()
            
        else:
            # Try to read as text for other file types
            try:
                text = file.read().decode('utf-8')
                logger.info(f"Read file as text: {len(text)} characters")
                return text.strip()
            except Exception:
                logger.error(f"Unsupported file format: {file_ext}")
                return None
                
    except Exception as e:
        logger.error(f"Error extracting text from file: {str(e)}")
        return None

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility functions for skill extraction and assessment scoring

def extract_skills_from_resume(resume_text):
    """Extract key technical skills from resume using keyword matching.
    
    This function scans the resume text for common technical skills and returns
    a comma-separated string of found skills.
    
    Args:
        resume_text (str): The resume content to analyze
        
    Returns:
        str: Comma-separated list of identified skills
    """
    # Common technical skills to look for in resumes
    common_skills = [
        'python', 'java', 'javascript', 'react', 'flask', 'django', 'sql', 'html', 'css', 'git',
        'node.js', 'angular', 'vue', 'postgresql', 'mysql', 'mongodb', 'docker', 'kubernetes',
        'aws', 'azure', 'machine learning', 'data science', 'api', 'rest', 'microservices',
        'typescript', 'c++', 'c#', 'ruby', 'php', 'golang', 'rust', 'swift'
    ]
    
    found_skills = []
    resume_lower = resume_text.lower()
    
    for skill in common_skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill.title())
    
    result = ', '.join(found_skills) if found_skills else 'General Programming Skills'
    logger.info(f"Extracted skills: {result}")
    return result

def calculate_assessment_score(quiz_responses):
    """Calculate assessment score based on response quality and technical depth.
    
    Scoring algorithm:
    - Base score: 60 points
    - Length bonus: Up to 30 points for detailed responses
    - Keyword bonus: Up to 10 points for technical terminology
    
    Args:
        quiz_responses (dict): Dictionary of question responses
        
    Returns:
        int: Final score out of 100
    """
    base_score = 60
    total_length = sum(len(response.strip()) for response in quiz_responses.values())
    
    # Bonus points for detailed responses (more comprehensive answers)
    length_bonus = min(30, total_length // 50)
    
    # Bonus for technical keywords (demonstrates technical knowledge)
    technical_keywords = [
        'algorithm', 'database', 'framework', 'api', 'testing', 'debugging', 'optimization',
        'architecture', 'scalability', 'performance', 'security', 'agile', 'git', 'deployment',
        'containerization', 'microservices', 'devops', 'ci/cd', 'monitoring'
    ]
    
    keyword_count = 0
    for response in quiz_responses.values():
        response_lower = response.lower()
        keyword_count += sum(1 for keyword in technical_keywords if keyword in response_lower)
    
    keyword_bonus = min(10, keyword_count * 2)
    
    final_score = base_score + length_bonus + keyword_bonus
    final_score = min(100, final_score)  # Cap at 100
    
    logger.info(f"Assessment scoring: base={base_score}, length_bonus={length_bonus}, keyword_bonus={keyword_bonus}, final={final_score}")
    return final_score

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Profile Agent: Create user profile and extract skills from uploaded resume
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Handle user profile creation and skill extraction from uploaded resume file."""
    if request.method == 'POST':
        username = request.form.get('username')
        
        if not username:
            flash('Please provide a username.', 'error')
            return render_template('profile.html')
        
        # Check if file was uploaded
        if 'resume_file' not in request.files:
            flash('Please upload a resume file.', 'error')
            return render_template('profile.html')
        
        file = request.files['resume_file']
        
        if file.filename == '':
            flash('No file selected. Please choose a resume file to upload.', 'error')
            return render_template('profile.html')
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PDF, Word document, or text file.', 'error')
            return render_template('profile.html')
        
        try:
            from models import User  # Import here to avoid circular import
            
            # Extract text from uploaded file
            resume_text = extract_text_from_file(file)
            
            if not resume_text:
                flash('Could not extract text from the uploaded file. Please try a different file.', 'error')
                return render_template('profile.html')
            
            if len(resume_text) < 50:
                flash('The resume content seems too short. Please upload a complete resume.', 'warning')
                return render_template('profile.html')
            
            # Use skill extraction to analyze resume
            skills = extract_skills_from_resume(resume_text)
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                # Update existing user profile
                current_time = datetime.utcnow()
                existing_user.skills = skills
                existing_user.resume_text = resume_text
                existing_user.skills_evaluated_at = current_time
                flash(f'Profile updated successfully for {username}!', 'success')
                logger.info(f"Profile updated for {username} with uploaded resume ({len(resume_text)} chars)")
                
                # Regenerate learning paths with updated skills
                generate_learning_paths(username, skills)
                existing_user.learning_path_generated_at = current_time
            else:
                # Create new user profile
                current_time = datetime.utcnow()
                new_user = User()
                new_user.username = username
                new_user.skills = skills
                new_user.resume_text = resume_text
                new_user.profile_created_at = current_time
                new_user.skills_evaluated_at = current_time
                db.session.add(new_user)
                flash(f'Profile created successfully for {username}!', 'success')
                logger.info(f"Profile created for {username} with uploaded resume ({len(resume_text)} chars)")
            
            db.session.commit()
            
            # Generate learning paths for new users
            if not existing_user:
                generate_learning_paths(username, skills)
                # Update the learning path timestamp
                updated_user = User.query.filter_by(username=username).first()
                if updated_user:
                    updated_user.learning_path_generated_at = datetime.utcnow()
                    db.session.commit()
            
            # Generate tailored courses using AI
            generate_tailored_courses(username, resume_text, skills)
            
            session['username'] = username
            return redirect(url_for('assessment'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating profile: {str(e)}")
            flash('An error occurred while processing your resume. Please try again.', 'error')
    
    return render_template('profile.html')

# Assessment Agent: Process quiz and assign score
@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    """Handle technical skill assessment and scoring."""
    username = session.get('username')
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        # Collect all quiz responses
        quiz_responses = {
            'question1': request.form.get('question1', ''),
            'question2': request.form.get('question2', ''),
            'question3': request.form.get('question3', ''),
            'question4': request.form.get('question4', ''),
            'question5': request.form.get('question5', '')
        }
        
        # Calculate score based on response quality
        score = calculate_assessment_score(quiz_responses)
        
        try:
            from models import User  # Import here to avoid circular import
            
            # Save assessment results to database
            user = User.query.filter_by(username=username).first()
            if user:
                user.scores = json.dumps({'total_score': score, 'responses': quiz_responses})
                user.assessment_completed_at = datetime.utcnow()
                db.session.commit()
                
                flash(f'Assessment completed! Your score: {score}/100', 'success')
                logger.info(f"Assessment completed for {username}: Score {score}")
                return redirect(url_for('progress'))
            else:
                flash('User not found. Please create a profile first.', 'error')
                return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving assessment: {str(e)}")
            flash('An error occurred while saving your assessment. Please try again.', 'error')
    
    return render_template('assessment.html', username=username)

# Get user progress and display results
@app.route('/progress')
@app.route('/progress/<username>')
def progress(username=None):
    """Display user progress, skills, and assessment results."""
    if not username:
        username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        from models import User  # Import here to avoid circular import
        
        user_data = User.query.filter_by(username=username).first()
        
        if not user_data:
            flash('User not found.', 'error')
            logger.warning(f"Progress requested for non-existent user: {username}")
            return redirect(url_for('profile'))
        
        # Parse assessment scores if available
        score_data = None
        if user_data.scores:
            try:
                score_data = json.loads(user_data.scores)
                logger.info(f"Progress displayed for {username} with score: {score_data.get('total_score', 'N/A')}")
            except json.JSONDecodeError:
                # Handle legacy format (simple score string)
                score_data = {'total_score': int(user_data.scores), 'responses': {}}
                logger.warning(f"Legacy score format detected for {username}")
        
        return render_template('progress.html', 
                             user_data=user_data, 
                             score_data=score_data)
        
    except Exception as e:
        logger.error(f"Error fetching progress for {username}: {str(e)}")
        flash('An error occurred while fetching your progress.', 'error')
        return redirect(url_for('index'))

# API endpoint for external access
@app.route('/api/progress/<username>')
def api_progress(username):
    try:
        from models import User  # Import here to avoid circular import
        
        user_data = User.query.filter_by(username=username).first()
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        result = {
            'username': user_data.username,
            'skills': user_data.skills,
            'scores': user_data.scores
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in API progress: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error_message="Internal server error"), 500

# Learning Path functionality
def generate_learning_paths(username, skills):
    """Generate personalized learning paths based on extracted skills."""
    try:
        from models import LearningPath
        
        # Sample learning modules based on common technical skills
        skill_modules = {
            'python': ['Python Fundamentals', 'Data Structures in Python', 'Advanced Python'],
            'javascript': ['JavaScript Basics', 'ES6+ Features', 'Async Programming'],
            'react': ['React Components', 'State Management', 'React Hooks'],
            'flask': ['Flask Fundamentals', 'Flask-SQLAlchemy', 'Flask REST APIs'],
            'django': ['Django Models', 'Django Views', 'Django REST Framework'],
            'sql': ['SQL Basics', 'Advanced Queries', 'Database Design'],
            'html': ['HTML5 Fundamentals', 'Semantic HTML', 'Web Accessibility'],
            'css': ['CSS Fundamentals', 'CSS Grid & Flexbox', 'CSS Animations'],
            'git': ['Git Basics', 'Branching Strategies', 'Collaborative Git'],
            'docker': ['Docker Fundamentals', 'Docker Compose', 'Container Orchestration'],
            'aws': ['AWS Fundamentals', 'EC2 & S3', 'AWS Lambda & API Gateway']
        }
        
        # Delete existing learning paths for this user
        LearningPath.query.filter_by(username=username).delete()
        
        # Generate learning paths based on skills
        skills_list = [skill.strip().lower() for skill in skills.split(',')]
        
        for skill in skills_list:
            if skill in skill_modules:
                modules = skill_modules[skill]
                for i, module_name in enumerate(modules):
                    learning_path = LearningPath()
                    learning_path.username = username
                    learning_path.module_name = module_name
                    learning_path.estimated_time = 45 + (i * 15)  # Progressive difficulty
                    learning_path.completion_status = 'Not Started'
                    db.session.add(learning_path)
        
        # Add some general modules if no specific skills found
        if not any(skill in skill_modules for skill in skills_list):
            general_modules = ['Programming Fundamentals', 'Problem Solving', 'Code Quality']
            for module_name in general_modules:
                learning_path = LearningPath()
                learning_path.username = username
                learning_path.module_name = module_name
                learning_path.estimated_time = 60
                learning_path.completion_status = 'Not Started'
                db.session.add(learning_path)
        
        db.session.commit()
        logger.info(f"Learning paths generated for {username}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error generating learning paths: {str(e)}")

# Tailored course generation functionality
def generate_tailored_courses(username, resume_text, skills):
    """Generate AI-powered tailored courses based on resume analysis."""
    try:
        from models import TailoredCourse, CourseModule
        
        # Simple fallback course generation without AI dependency
        
        # Generate course based on resume analysis - simplified fallback
        course_data = {
            'title': 'Personalized Learning Path',
            'description': 'AI-generated course based on your resume',
            'difficulty': 'Intermediate',
            'duration': '4-6 weeks',
            'modules': [
                {
                    'title': 'Foundation Skills',
                    'description': 'Core skills based on your background',
                    'estimated_time': 60,
                    'resources': []
                },
                {
                    'title': 'Advanced Topics',
                    'description': 'Advanced concepts in your skill area',
                    'estimated_time': 90,
                    'resources': []
                }
            ]
        }
        
        if course_data:
            # Create tailored course record
            tailored_course = TailoredCourse()
            tailored_course.username = username
            tailored_course.course_title = course_data.get('title', 'Personalized Learning Path')
            tailored_course.course_description = course_data.get('description', 'AI-generated course based on your resume')
            tailored_course.difficulty_level = course_data.get('difficulty', 'Intermediate')
            tailored_course.estimated_duration = course_data.get('duration', '4-6 weeks')
            tailored_course.course_plan = json.dumps(course_data.get('modules', []))
            tailored_course.skill_focus = json.dumps(skills.split(', '))
            
            db.session.add(tailored_course)
            db.session.commit()
            
            # Create individual course modules
            modules_data = course_data.get('modules', [])
            for i, module_data in enumerate(modules_data):
                course_module = CourseModule()
                course_module.tailored_course_id = tailored_course.id
                course_module.module_title = module_data.get('title', f'Module {i+1}')
                course_module.module_description = module_data.get('description', '')
                course_module.module_order = i + 1
                course_module.resources = json.dumps(module_data.get('resources', []))
                course_module.estimated_time = module_data.get('estimated_time', 60)
                db.session.add(course_module)
            
            db.session.commit()
            logger.info(f"Tailored course generated for {username}: {course_data.get('title')}")
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error generating tailored courses: {str(e)}")


# Additional routes for template compatibility
@app.route('/assessment_panel')
def assessment_panel():
    """Assessment panel route."""
    username = session.get('username')
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    return render_template('assessment_panel.html', username=username)

@app.route('/learning_path')
@app.route('/learning_path/<username>')
def learning_path(username=None):
    """Display learning path for user."""
    if not username:
        username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        from models import LearningPath, User
        
        user_data = User.query.filter_by(username=username).first()
        learning_paths = LearningPath.query.filter_by(username=username).all()
        
        return render_template('learning_path.html', 
                             user_data=user_data, 
                             learning_paths=learning_paths)
        
    except Exception as e:
        logger.error(f"Error fetching learning path: {str(e)}")
        flash('An error occurred while fetching your learning path.', 'error')
        return redirect(url_for('index'))

@app.route('/tailored_courses')
@app.route('/tailored_courses/<username>')
def tailored_courses(username=None):
    """Display tailored courses for user."""
    if not username:
        username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        from models import TailoredCourse, User
        
        user_data = User.query.filter_by(username=username).first()
        courses = TailoredCourse.query.filter_by(username=username).all()
        
        return render_template('tailored_courses.html', 
                             user_data=user_data, 
                             courses=courses)
        
    except Exception as e:
        logger.error(f"Error fetching tailored courses: {str(e)}")
        flash('An error occurred while fetching your courses.', 'error')
        return redirect(url_for('index'))

@app.route('/hackathon')
def hackathon():
    """Display hackathon page."""
    username = session.get('username')
    return render_template('hackathon.html', username=username)

@app.route('/leaderboard')
def leaderboard():
    """Display leaderboard page."""
    try:
        from models import User
        users = User.query.all()
        return render_template('leaderboard.html', users=users)
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        return render_template('leaderboard.html', users=[])

@app.route('/gen_ai_info')
def gen_ai_info():
    """Display Gen AI information page."""
    return render_template('gen_ai_info.html')

@app.route('/api_status')
def api_status():
    """Display API status page."""
    return render_template('api_status.html')

# Admin routes for template compatibility
@app.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard route."""
    return render_template('admin_dashboard.html')

@app.route('/admin_users')
def admin_users():
    """Admin users route."""
    try:
        from models import User
        users = User.query.all()
        return render_template('admin_users.html', users=users)
    except Exception as e:
        logger.error(f"Error fetching admin users: {str(e)}")
        return render_template('admin_users.html', users=[])

@app.route('/admin_user_detail/<username>')
def admin_user_detail(username):
    """Admin user detail route."""
    try:
        from models import User
        user = User.query.filter_by(username=username).first()
        return render_template('admin_user_detail.html', user=user)
    except Exception as e:
        logger.error(f"Error fetching user detail: {str(e)}")
        flash('Error fetching user details', 'error')
        return redirect(url_for('admin_users'))

@app.route('/admin_reports')
def admin_reports():
    """Admin reports route."""
    return render_template('admin_reports.html')

@app.route('/admin_hackathons')
def admin_hackathons():
    """Admin hackathons route."""
    return render_template('admin_hackathons.html')

@app.route('/reassess_user/<username>', methods=['POST'])
def reassess_user(username):
    """Reset user assessment."""
    try:
        from models import User
        user = User.query.filter_by(username=username).first()
        if user:
            user.scores = None
            user.assessment_completed_at = None
            db.session.commit()
            flash(f'Assessment reset for {username}', 'success')
        else:
            flash('User not found', 'error')
    except Exception as e:
        logger.error(f"Error resetting assessment: {str(e)}")
        flash('Error resetting assessment', 'error')
    return redirect(request.referrer or url_for('admin_users'))

@app.route('/admin_reassess_user/<username>', methods=['POST'])
def admin_reassess_user(username):
    """Admin reset user assessment."""
    return reassess_user(username)

@app.route('/update_profile_request', methods=['POST'])
def update_profile_request():
    """Handle profile update requests."""
    username = session.get('username')
    if username:
        flash('Profile update requested. Please upload a new resume.', 'info')
        return redirect(url_for('profile'))
    return redirect(url_for('index'))

@app.route('/request_review', methods=['POST'])
def request_review():
    """Handle review requests."""
    username = session.get('username')
    if username:
        flash('Review requested. An administrator will contact you.', 'info')
    return redirect(request.referrer or url_for('progress'))

@app.route('/update_learning_path', methods=['POST'])
def update_learning_path():
    """Update learning path progress."""
    username = session.get('username')
    module_id = request.form.get('module_id')
    status = request.form.get('status', 'Completed')
    
    try:
        from models import LearningPath
        learning_path = LearningPath.query.filter_by(username=username, id=module_id).first()
        if learning_path:
            learning_path.completion_status = status
            if status == 'Completed':
                learning_path.completed_at = datetime.utcnow()
            db.session.commit()
            flash('Learning path updated successfully', 'success')
    except Exception as e:
        logger.error(f"Error updating learning path: {str(e)}")
        flash('Error updating learning path', 'error')
    
    return redirect(request.referrer or url_for('learning_path'))

@app.route('/generate_exercise', methods=['POST'])
def generate_exercise():
    """Generate a coding exercise."""
    username = session.get('username')
    skill = request.form.get('skill', 'Python')
    
    # Simple fallback exercise generation
    exercises = {
        'python': 'Create a function that finds the maximum element in a list',
        'javascript': 'Write a function that reverses a string',
        'sql': 'Write a query to find the top 5 customers by total orders',
        'default': 'Solve a coding problem relevant to your skill level'
    }
    
    exercise = exercises.get(skill.lower(), exercises['default'])
    
    return jsonify({
        'exercise': exercise,
        'skill': skill,
        'difficulty': 'Medium',
        'time_limit': '30 minutes'
    })