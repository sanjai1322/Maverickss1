import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from io import BytesIO
from datetime import datetime

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create a Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with SQLAlchemy
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    db.create_all()
    logger.info("Database tables created successfully")

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
            except:
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
                new_user = User(
                    username=username, 
                    skills=skills, 
                    resume_text=resume_text,
                    profile_created_at=current_time,
                    skills_evaluated_at=current_time
                )
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
            'flask': ['Flask Routing', 'Database Integration', 'API Development'],
            'django': ['Django Models', 'Django Views', 'Django REST Framework'],
            'sql': ['SQL Basics', 'Advanced Queries', 'Database Design'],
            'machine learning': ['ML Fundamentals', 'Data Preprocessing', 'Model Training'],
            'api': ['API Design', 'RESTful Services', 'API Documentation'],
            'git': ['Version Control', 'Branching Strategies', 'Collaboration'],
            'docker': ['Containerization', 'Docker Compose', 'Deployment']
        }
        
        # Clear existing learning paths for user
        LearningPath.query.filter_by(username=username).delete()
        
        skills_list = [skill.strip().lower() for skill in skills.split(',')]
        
        for skill in skills_list:
            modules = skill_modules.get(skill, [f'{skill.title()} Fundamentals'])
            for i, module in enumerate(modules):
                learning_path = LearningPath(
                    username=username,
                    module_name=module,
                    estimated_time=60 + (i * 30),  # Increasing difficulty
                    completion_status='Not Started'
                )
                db.session.add(learning_path)
        
        db.session.commit()
        logger.info(f"Generated learning paths for {username} based on skills: {skills}")
        
    except Exception as e:
        logger.error(f"Error generating learning paths: {str(e)}")
        db.session.rollback()

# Learning Path Routes
@app.route('/learning_path')
@app.route('/learning_path/<username>')
def learning_path(username=None):
    """Display learning paths for a user."""
    if not username:
        username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        from models import User, LearningPath
        
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('profile'))
        
        learning_paths = LearningPath.query.filter_by(username=username).all()
        
        # If no learning paths exist, generate them
        if not learning_paths and user.skills:
            generate_learning_paths(username, user.skills)
            learning_paths = LearningPath.query.filter_by(username=username).all()
            user.learning_path_generated_at = datetime.utcnow()
            db.session.commit()
        
        return render_template('learning_path.html', 
                             user=user, 
                             learning_paths=learning_paths)
        
    except Exception as e:
        logger.error(f"Error fetching learning path: {str(e)}")
        flash('An error occurred while fetching learning paths.', 'error')
        return redirect(url_for('index'))

@app.route('/api/learning_path/<username>')
def api_learning_path(username):
    """API endpoint to get learning paths for a user."""
    try:
        from models import LearningPath
        
        learning_paths = LearningPath.query.filter_by(username=username).all()
        
        if not learning_paths:
            return jsonify({'error': 'No learning path found'}), 404
        
        modules = [{
            'module_name': lp.module_name,
            'estimated_time': lp.estimated_time,
            'completion_status': lp.completion_status
        } for lp in learning_paths]
        
        return jsonify({'username': username, 'modules': modules})
        
    except Exception as e:
        logger.error(f"Error in API learning path: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/update_learning_path', methods=['POST'])
def update_learning_path():
    """Update completion status of a learning path module."""
    try:
        from models import LearningPath
        
        module_id = request.form.get('module_id')
        status = request.form.get('status')
        
        if not module_id or not status:
            flash('Invalid request.', 'error')
            return redirect(url_for('learning_path'))
        
        learning_path = LearningPath.query.get(module_id)
        if learning_path:
            learning_path.completion_status = status
            if status == 'Completed':
                learning_path.completed_at = datetime.utcnow()
            db.session.commit()
            flash(f'Module "{learning_path.module_name}" status updated to {status}!', 'success')
        else:
            flash('Module not found.', 'error')
        
        return redirect(url_for('learning_path'))
        
    except Exception as e:
        logger.error(f"Error updating learning path: {str(e)}")
        flash('An error occurred while updating the module.', 'error')
        return redirect(url_for('learning_path'))

# Hackathon Routes
@app.route('/hackathon', methods=['GET', 'POST'])
def hackathon():
    """Handle hackathon challenge submissions."""
    username = session.get('username')
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        try:
            from models import Hackathon
            
            challenge_name = request.form.get('challenge_name')
            submission = request.form.get('submission')
            
            if not challenge_name or not submission:
                flash('Please provide both challenge name and submission.', 'error')
                return render_template('hackathon.html', username=username)
            
            hackathon_submission = Hackathon(
                username=username,
                challenge_name=challenge_name,
                submission=submission
            )
            db.session.add(hackathon_submission)
            db.session.commit()
            
            flash(f'Hackathon submission for "{challenge_name}" submitted successfully!', 'success')
            logger.info(f"Hackathon submission for {username}: {challenge_name}")
            
            return redirect(url_for('hackathon'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in hackathon submission: {str(e)}")
            flash('An error occurred while submitting your hackathon entry.', 'error')
    
    try:
        from models import Hackathon
        
        # Get user's previous submissions
        submissions = Hackathon.query.filter_by(username=username).order_by(Hackathon.submitted_at.desc()).all()
        
        return render_template('hackathon.html', 
                             username=username, 
                             submissions=submissions)
        
    except Exception as e:
        logger.error(f"Error fetching hackathon submissions: {str(e)}")
        flash('An error occurred while loading hackathon data.', 'error')
        return redirect(url_for('index'))

@app.route('/api/hackathon', methods=['POST'])
def api_hackathon():
    """API endpoint for hackathon submissions."""
    try:
        from models import Hackathon
        
        data = request.get_json()
        username = data.get('username')
        challenge_name = data.get('challenge_name')
        submission = data.get('submission')
        
        if not all([username, challenge_name, submission]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        hackathon_submission = Hackathon(
            username=username,
            challenge_name=challenge_name,
            submission=submission
        )
        db.session.add(hackathon_submission)
        db.session.commit()
        
        logger.info(f"API Hackathon submission for {username}: {challenge_name}")
        return jsonify({
            'username': username,
            'challenge_name': challenge_name,
            'message': 'Submission successful'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in API hackathon submission: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Leaderboard Routes
@app.route('/leaderboard')
def leaderboard():
    """Display top users by assessment scores."""
    try:
        from models import User
        
        # Get top users with scores, excluding null scores
        top_users = User.query.filter(User.scores.isnot(None)).all()
        
        # Parse scores and sort
        leaderboard_data = []
        for user in top_users:
            try:
                score_data = json.loads(user.scores)
                total_score = score_data.get('total_score', 0)
                leaderboard_data.append({
                    'username': user.username,
                    'score': total_score,
                    'skills': user.skills,
                    'assessment_date': user.assessment_completed_at
                })
            except (json.JSONDecodeError, AttributeError):
                # Handle legacy score format
                try:
                    score = int(user.scores)
                    leaderboard_data.append({
                        'username': user.username,
                        'score': score,
                        'skills': user.skills,
                        'assessment_date': user.assessment_completed_at
                    })
                except (ValueError, TypeError):
                    continue
        
        # Sort by score descending and take top 10
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
        top_10 = leaderboard_data[:10]
        
        return render_template('leaderboard.html', leaderboard=top_10)
        
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        flash('An error occurred while loading the leaderboard.', 'error')
        return redirect(url_for('index'))

@app.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint to get top users leaderboard."""
    try:
        from models import User
        
        # Get top users with scores
        top_users = User.query.filter(User.scores.isnot(None)).all()
        
        leaderboard_data = []
        for user in top_users:
            try:
                score_data = json.loads(user.scores)
                total_score = score_data.get('total_score', 0)
                leaderboard_data.append({
                    'username': user.username,
                    'score': total_score
                })
            except (json.JSONDecodeError, AttributeError):
                try:
                    score = int(user.scores)
                    leaderboard_data.append({
                        'username': user.username,
                        'score': score
                    })
                except (ValueError, TypeError):
                    continue
        
        # Sort by score and take top 5
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
        top_5 = leaderboard_data[:5]
        
        return jsonify({'leaderboard': top_5})
        
    except Exception as e:
        logger.error(f"Error in API leaderboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
