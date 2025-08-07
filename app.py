import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401

    db.create_all()

# Utility functions for skill extraction and scoring
def extract_skills_from_resume(resume_text):
    """Extract skills from resume using keyword matching"""
    common_skills = ['python', 'java', 'javascript', 'react', 'flask', 'django', 'sql', 'html', 'css', 'git', 
                    'node.js', 'angular', 'vue', 'postgresql', 'mysql', 'mongodb', 'docker', 'kubernetes', 
                    'aws', 'azure', 'machine learning', 'data science', 'api', 'rest', 'microservices']
    found_skills = []
    resume_lower = resume_text.lower()
    for skill in common_skills:
        if skill.lower() in resume_lower:
            found_skills.append(skill.title())
    return ', '.join(found_skills) if found_skills else 'General Programming Skills'

def calculate_assessment_score(quiz_responses):
    """Calculate assessment score based on response quality"""
    base_score = 60
    total_length = sum(len(response.strip()) for response in quiz_responses.values())
    
    # Bonus points for detailed responses
    length_bonus = min(30, total_length // 50)
    
    # Bonus for technical keywords
    technical_keywords = ['algorithm', 'database', 'framework', 'api', 'testing', 'debugging', 'optimization',
                         'architecture', 'scalability', 'performance', 'security', 'agile', 'git']
    keyword_count = 0
    for response in quiz_responses.values():
        response_lower = response.lower()
        keyword_count += sum(1 for keyword in technical_keywords if keyword in response_lower)
    
    keyword_bonus = min(10, keyword_count * 2)
    
    final_score = base_score + length_bonus + keyword_bonus
    return min(100, final_score)  # Cap at 100

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        resume_text = request.form.get('resume')
        
        if not username or not resume_text:
            flash('Please provide both username and resume text.', 'error')
            return render_template('profile.html')
        
        try:
            from models import User  # Import here to avoid circular import
            
            # Extract skills using keyword matching
            skills = extract_skills_from_resume(resume_text)
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                # Update existing user
                existing_user.skills = skills
                existing_user.resume_text = resume_text
                flash(f'Profile updated successfully for {username}!', 'success')
            else:
                # Create new user
                new_user = User(username=username, skills=skills, resume_text=resume_text)
                db.session.add(new_user)
                flash(f'Profile created successfully for {username}!', 'success')
            
            db.session.commit()
            session['username'] = username
            logger.info(f"Profile processed for {username}")
            return redirect(url_for('assessment'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating profile: {str(e)}")
            flash('An error occurred while creating your profile. Please try again.', 'error')
    
    return render_template('profile.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    username = session.get('username')
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        quiz_responses = {
            'question1': request.form.get('question1', ''),
            'question2': request.form.get('question2', ''),
            'question3': request.form.get('question3', ''),
            'question4': request.form.get('question4', ''),
            'question5': request.form.get('question5', '')
        }
        
        # Calculate score
        score = calculate_assessment_score(quiz_responses)
        
        try:
            from models import User  # Import here to avoid circular import
            
            # Save score to database
            user = User.query.filter_by(username=username).first()
            if user:
                user.scores = json.dumps({'total_score': score, 'responses': quiz_responses})
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

@app.route('/progress')
@app.route('/progress/<username>')
def progress(username=None):
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
            return redirect(url_for('profile'))
        
        # Parse scores if available
        score_data = None
        if user_data.scores:
            try:
                score_data = json.loads(user_data.scores)
            except json.JSONDecodeError:
                # Handle old format (simple score string)
                score_data = {'total_score': int(user_data.scores), 'responses': {}}
        
        return render_template('progress.html', 
                             user_data=user_data, 
                             score_data=score_data)
        
    except Exception as e:
        logger.error(f"Error fetching progress: {str(e)}")
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
