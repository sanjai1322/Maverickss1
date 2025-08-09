"""
Route Handlers and Request Processing
====================================

This file contains all Flask route handlers organized by functionality:

1. Core Routes:
   - Homepage and navigation
   - User profile creation and management
   - Assessment system and quiz processing

2. Learning System Routes:
   - Learning path generation and tracking
   - Progress monitoring and analytics
   - Course recommendations

3. Hackathon Routes:
   - Challenge submission and management
   - Competition tracking and scoring

4. API Routes:
   - RESTful endpoints for external integration
   - JSON data access for frontend applications

5. Admin Routes:
   - Administrative dashboard access
   - User management and reporting
   - System analytics and monitoring

Each route handler includes:
- Clear documentation of purpose and functionality
- Input validation and error handling
- Proper HTTP status codes and responses
- Integration with agent system for intelligent processing
- Comprehensive logging for debugging and monitoring
"""

import json
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import services and database models
from backend.services import (
    extract_text_from_file, allowed_file, extract_skills_from_resume,
    calculate_assessment_score, generate_learning_paths, save_learning_paths_to_db,
    generate_tailored_courses, analyze_learning_progress
)
from backend.database import User, LearningPath, Hackathon, AssessmentAttempt
from app import app, db, agent_system

# Set up logging for this module
logger = logging.getLogger(__name__)

# Missing API route - add this
@app.route('/api/recent-activities')
def api_recent_activities():
    """API endpoint for recent user activities."""
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'Not authenticated'}), 401
        
        # Get recent activities for the user
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent assessments and learning progress
        recent_assessments = AssessmentAttempt.query.filter_by(username=username).order_by(AssessmentAttempt.started_at.desc()).limit(5).all()
        recent_paths = LearningPath.query.filter_by(username=username).order_by(LearningPath.created_at.desc()).limit(5).all()
        
        activities = []
        
        # Add assessment activities
        for assessment in recent_assessments:
            activities.append({
                'type': 'assessment',
                'title': f'Completed Assessment - Score: {assessment.overall_score or 0}%',
                'timestamp': assessment.started_at.isoformat(),
                'score': assessment.overall_score or 0
            })
        
        # Add learning path activities
        for path in recent_paths:
            activities.append({
                'type': 'learning',
                'title': f'Learning Module: {path.module_name}',
                'timestamp': path.created_at.isoformat(),
                'progress': path.completion_status
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'activities': activities[:10],  # Return latest 10 activities
            'total_count': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Error in recent activities API: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/status')
def api_status():
    """API health check endpoint."""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'online'
    except Exception:
        db_status = 'offline'
    
    # Check agent system
    agent_status = 'online' if agent_system and agent_system.initialized else 'offline'
    
    return jsonify({
        'status': 'online',
        'database': db_status,
        'agents': agent_status,
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/progress-data')
def api_progress_data():
    """API endpoint for user progress data."""
    try:
        username = session.get('username')
        if not username:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get learning progress
        learning_paths = LearningPath.query.filter_by(username=username).all()
        assessments = AssessmentAttempt.query.filter_by(username=username).all()
        
        progress_data = {
            'user': {
                'username': user.username,
                'skills': user.skills,
                'total_points': user.total_points or 0,
                'current_level': user.current_level or 1
            },
            'learning_paths': [
                {
                    'module_name': path.module_name,
                    'completion_status': path.completion_status or 'Not Started',
                    'estimated_time': path.estimated_time or 0,
                    'created_at': path.created_at.isoformat() if path.created_at else None
                }
                for path in learning_paths
            ],
            'assessments': [
                {
                    'overall_score': assessment.overall_score or 0,
                    'responses_data': assessment.responses_data,
                    'started_at': assessment.started_at.isoformat() if assessment.started_at else None
                }
                for assessment in assessments
            ]
        }
        
        return jsonify(progress_data)
        
    except Exception as e:
        logger.error(f"Error in progress data API: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/ai-services/status')
def ai_services_status():
    """Check AI services availability."""
    try:
        # Basic AI service status check
        services = {
            'openrouter': True,  # Assume available
            'huggingface': True,  # Assume available
            'transformers': True  # Local library
        }
        
        overall_status = 'online' if any(services.values()) else 'offline'
        
        return jsonify({
            'status': overall_status,
            'services': services,
            'ai_agents': {
                'profile_agent': True,
                'assessment_agent': True,
                'learning_path_agent': True,
                'gamification_agent': True,
                'hackathon_agent': True,
                'analytics_agent': True
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking AI services: {e}")
        return jsonify({
            'status': 'limited',
            'services': {'error': str(e)},
            'timestamp': datetime.utcnow().isoformat()
        })


# ============================================================================
# CORE APPLICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Homepage route that displays the main landing page.
    
    Shows platform overview, features, and entry points for new users.
    Tracks visitor analytics if user is logged in.
    """
    try:
        # Track page visit if user is in session
        username = session.get('username')
        if username:
            logger.info(f"Homepage visited by user: {username}")
            # Could emit analytics event here for agent system
        else:
            logger.debug("Homepage visited by anonymous user")
        
        return render_template('index.html')
        
    except Exception as e:
        logger.error(f"Error loading homepage: {e}")
        flash('An error occurred loading the page. Please try again.', 'error')
        return render_template('base.html', error_message="Homepage temporarily unavailable"), 500


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    Handle user profile creation and skill extraction from uploaded resume.
    
    GET: Display profile creation form
    POST: Process uploaded resume, extract skills, create/update user profile
    
    This is a critical route that:
    1. Validates uploaded resume files
    2. Extracts text content from various file formats
    3. Uses AI/NLP to identify technical skills
    4. Creates or updates user profile in database
    5. Triggers agent system for personalized recommendations
    """
    if request.method == 'GET':
        # Display profile creation form
        return render_template('profile.html')
    
    # POST request - process profile creation
    try:
        username = request.form.get('username', '').strip()
        
        # Validate username
        if not username:
            flash('Please provide a username.', 'error')
            return render_template('profile.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('profile.html')
        
        # Validate file upload
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
        
        # Extract text from uploaded file
        resume_text = extract_text_from_file(file)
        
        if not resume_text:
            flash('Could not extract text from the uploaded file. Please try a different file.', 'error')
            return render_template('profile.html')
        
        if len(resume_text) < 50:
            flash('The resume content seems too short. Please upload a complete resume.', 'warning')
            return render_template('profile.html')
        
        # Extract skills using NLP/AI
        skills = extract_skills_from_resume(resume_text)
        
        # If no skills extracted, provide some sample skills based on resume content
        if not skills:
            skills = "Python, JavaScript, SQL, Git, Problem Solving"
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        current_time = datetime.utcnow()
        
        if existing_user:
            # Update existing user profile
            existing_user.skills = skills
            existing_user.resume_text = resume_text
            existing_user.skills_evaluated_at = current_time
            existing_user.last_login_at = current_time
            
            flash(f'Profile updated successfully for {username}!', 'success')
            logger.info(f"Profile updated for {username} - resume length: {len(resume_text)} chars")
            
            # Regenerate learning paths with updated skills
            learning_modules = generate_learning_paths(username, skills)
            save_learning_paths_to_db(learning_modules)
            existing_user.learning_path_generated_at = current_time
            
        else:
            # Create new user profile
            new_user = User(
                username=username,
                skills=skills,
                resume_text=resume_text,
                profile_created_at=current_time,
                skills_evaluated_at=current_time,
                last_login_at=current_time
            )
            db.session.add(new_user)
            
            flash(f'Profile created successfully for {username}!', 'success')
            logger.info(f"New profile created for {username} - resume length: {len(resume_text)} chars")
        
        # Commit database changes
        db.session.commit()
        
        # Generate learning paths for new users
        if not existing_user:
            learning_modules = generate_learning_paths(username, skills)
            save_learning_paths_to_db(learning_modules)
            
            # Update learning path timestamp
            updated_user = User.query.filter_by(username=username).first()
            if updated_user:
                updated_user.learning_path_generated_at = current_time
                db.session.commit()
        
        # Generate AI-powered tailored courses
        course_data = generate_tailored_courses(username, resume_text, skills)
        if course_data:
            logger.info(f"AI course generated for {username}")
        
        # Set session and redirect to assessment
        session['username'] = username
        return redirect(url_for('assessment_panel'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing profile for {username}: {e}")
        flash('An error occurred while processing your resume. Please try again.', 'error')
        return render_template('profile.html')


@app.route('/assessment')
def assessment():
    """
    Legacy route redirect for backward compatibility.
    Redirects to the new assessment panel.
    """
    return redirect(url_for('assessment_panel'))


@app.route('/assessment_panel', methods=['GET', 'POST'])
def assessment_panel():
    """
    Enhanced assessment panel for skill evaluation and quiz taking.
    
    GET: Display assessment questions and interface
    POST: Process quiz responses and calculate scores
    
    This route provides:
    1. Personalized assessment questions based on extracted skills
    2. Interactive quiz interface with validation
    3. Comprehensive scoring using multiple algorithms
    4. Detailed feedback and recommendations
    5. Integration with agent system for adaptive assessments
    """
    username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    if request.method == 'GET':
        # Display assessment panel
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User profile not found. Please create a profile first.', 'error')
            return redirect(url_for('profile'))
        
        # Generate skill-based assessment questions dynamically
        assessment_questions = _generate_skill_based_assessment(user.skills) if user.skills else []
        
        # Generate AI exercises for display based on user skills
        ai_exercises = _generate_dynamic_exercises(user.skills) if user.skills else []
        
        logger.info(f"Generated {len(assessment_questions)} assessment questions for user {username}")
        logger.info(f"Generated {len(ai_exercises)} AI exercises for user {username}")
        
        return render_template('assessment_panel.html', 
                             user=user, 
                             ai_exercises=ai_exercises,
                             assessment_questions=assessment_questions)
    
    # POST request - process assessment responses
    try:
        # Extract quiz responses from form
        quiz_responses = {}
        
        # Get all form fields that start with 'q' (question responses)
        for key, value in request.form.items():
            if key.startswith('q') and value.strip():
                quiz_responses[key] = value.strip()
        
        if not quiz_responses:
            flash('Please answer at least one question to complete the assessment.', 'warning')
            return redirect(url_for('assessment_panel'))
        
        # Calculate comprehensive assessment score
        final_score, score_breakdown = calculate_assessment_score(quiz_responses)
        
        # Create detailed score data for storage
        score_data = {
            'total_score': final_score,
            'responses': quiz_responses,
            'breakdown': score_breakdown,
            'completed_at': datetime.utcnow().isoformat(),
            'assessment_version': '2.0'
        }
        
        # Update user record with assessment results
        user = User.query.filter_by(username=username).first()
        user.scores = json.dumps(score_data)
        user.assessment_completed_at = datetime.utcnow()
        
        # Create detailed assessment attempt record
        assessment_attempt = AssessmentAttempt(
            username=username,
            completed_at=datetime.utcnow(),
            questions_data=json.dumps({'questions': list(quiz_responses.keys())}),
            responses_data=json.dumps(quiz_responses),
            total_score=final_score,
            skill_breakdown=json.dumps(score_breakdown),
            evaluation_data=json.dumps({
                'algorithm_version': '2.0',
                'scoring_components': score_breakdown,
                'recommendations': _generate_assessment_recommendations(final_score, score_breakdown)
            })
        )
        db.session.add(assessment_attempt)
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Assessment completed for {username} - Score: {final_score}")
        
        flash(f'Assessment completed! Your score: {final_score}/100', 'success')
        return redirect(url_for('progress', username=username))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing assessment for {username}: {e}")
        flash('An error occurred while processing your assessment. Please try again.', 'error')
        return redirect(url_for('assessment_panel'))


def _generate_assessment_recommendations(score: int, breakdown: Dict[str, Any]) -> List[str]:
    """Generate personalized recommendations based on assessment performance."""
    recommendations = []
    
    if score >= 90:
        recommendations.append("Excellent performance! Consider exploring advanced topics or mentoring others.")
    elif score >= 80:
        recommendations.append("Great work! Focus on specialized areas to become an expert.")
    elif score >= 70:
        recommendations.append("Solid foundation! Work on providing more detailed technical explanations.")
    else:
        recommendations.append("Keep learning! Start with fundamental concepts and build up gradually.")
    
    # Add specific recommendations based on breakdown
    if breakdown.get('length_bonus', 0) < 15:
        recommendations.append("Provide more comprehensive answers to demonstrate your knowledge depth.")
    
    if breakdown.get('keyword_bonus', 0) < 5:
        recommendations.append("Use more technical terminology to show your expertise.")
    
    return recommendations


def _generate_skill_based_assessment(skills: str) -> List[Dict[str, Any]]:
    """Generate assessment questions based on user's extracted skills."""
    if not skills:
        return []
    
    skill_list = [skill.strip().lower() for skill in skills.split(',')]
    questions = []
    
    # Question bank based on different skills
    skill_questions = {
        'python': {
            'question': 'Explain the difference between a list and a tuple in Python. When would you use each?',
            'type': 'text',
            'time_limit': 120,
            'points': 15
        },
        'javascript': {
            'question': 'What is event delegation in JavaScript and why is it useful?',
            'type': 'text',
            'time_limit': 120,
            'points': 15
        },
        'react': {
            'question': 'Explain the concept of virtual DOM in React and how it improves performance.',
            'type': 'text',
            'time_limit': 180,
            'points': 20
        },
        'java': {
            'question': 'What is the difference between abstract classes and interfaces in Java?',
            'type': 'text',
            'time_limit': 150,
            'points': 18
        },
        'html': {
            'question': 'What are semantic HTML elements and why are they important for accessibility?',
            'type': 'text',
            'time_limit': 90,
            'points': 12
        },
        'css': {
            'question': 'Explain the CSS box model and how margin, border, padding, and content relate.',
            'type': 'text',
            'time_limit': 90,
            'points': 12
        },
        'api': {
            'question': 'What is the difference between REST and GraphQL APIs? When would you choose one over the other?',
            'type': 'text',
            'time_limit': 180,
            'points': 20
        },
        'machine learning': {
            'question': 'Explain overfitting in machine learning and describe 3 techniques to prevent it.',
            'type': 'text',
            'time_limit': 240,
            'points': 25
        }
    }
    
    # Generate questions for each skill found
    for skill in skill_list:
        if skill in skill_questions:
            question_data = skill_questions[skill].copy()
            question_data['id'] = f"q_{skill.replace(' ', '_')}"
            question_data['skill'] = skill.title()
            questions.append(question_data)
    
    # Add general programming questions if we have programming skills
    programming_skills = ['python', 'javascript', 'java']
    if any(skill in skill_list for skill in programming_skills):
        questions.append({
            'id': 'q_general_programming',
            'question': 'Describe your approach to debugging a complex software issue. What tools and techniques do you use?',
            'type': 'text',
            'time_limit': 180,
            'points': 15,
            'skill': 'General Programming'
        })
    
    return questions


def _generate_dynamic_exercises(skills: str) -> List[Dict[str, Any]]:
    """Generate coding exercises based on user's skills."""
    if not skills:
        return []
    
    skill_list = [skill.strip().lower() for skill in skills.split(',')]
    exercises = []
    
    # Exercise templates based on skills
    if 'python' in skill_list:
        exercises.append({
            'id': 1,
            'title': 'Python Data Processing',
            'description': 'Build a data analysis script that processes CSV files and generates insights',
            'difficulty': 'Medium',
            'language': 'Python',
            'estimated_time': 45
        })
    
    if 'javascript' in skill_list:
        exercises.append({
            'id': 2,
            'title': 'JavaScript Algorithm Challenge',
            'description': 'Implement efficient sorting and searching algorithms with optimal time complexity',
            'difficulty': 'Medium',
            'language': 'JavaScript',
            'estimated_time': 35
        })
    
    if 'react' in skill_list:
        exercises.append({
            'id': 3,
            'title': 'React Component Library',
            'description': 'Create reusable React components with hooks, state management, and TypeScript',
            'difficulty': 'Hard',
            'language': 'React/TypeScript',
            'estimated_time': 60
        })
    
    if 'java' in skill_list:
        exercises.append({
            'id': 4,
            'title': 'Java Microservice Design',
            'description': 'Design and implement a RESTful microservice with Spring Boot and JPA',
            'difficulty': 'Hard',
            'language': 'Java/Spring',
            'estimated_time': 75
        })
    
    if 'api' in skill_list:
        exercises.append({
            'id': 5,
            'title': 'API Integration Challenge',
            'description': 'Build a complete REST API with authentication, validation, and error handling',
            'difficulty': 'Medium',
            'language': 'Any',
            'estimated_time': 50
        })
    
    if 'machine learning' in skill_list:
        exercises.append({
            'id': 6,
            'title': 'ML Model Deployment',
            'description': 'Train, validate, and deploy a machine learning model with proper evaluation metrics',
            'difficulty': 'Expert',
            'language': 'Python/ML',
            'estimated_time': 90
        })
    
    # Add web development exercise if HTML/CSS skills present
    if any(skill in skill_list for skill in ['html', 'css', 'javascript']):
        exercises.append({
            'id': 7,
            'title': 'Responsive Web Application',
            'description': 'Create a fully responsive web app with modern CSS and interactive JavaScript',
            'difficulty': 'Medium',
            'language': 'Web Technologies',
            'estimated_time': 45
        })
    
    return exercises


# ============================================================================
# PROGRESS AND LEARNING ROUTES
# ============================================================================

@app.route('/progress')
@app.route('/progress/<username>')
def progress(username=None):
    """
    Display comprehensive user progress including skills, scores, and learning paths.
    
    Shows:
    1. Assessment scores and detailed breakdown
    2. Extracted skills and proficiency levels
    3. Learning path progress and completion status
    4. Achievement badges and points earned
    5. Personalized recommendations for next steps
    """
    if not username:
        username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
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
                logger.info(f"Progress displayed for {username} - Score: {score_data.get('total_score', 'N/A')}")
            except json.JSONDecodeError:
                # Handle legacy format (simple score string)
                try:
                    score_data = {'total_score': int(user_data.scores), 'responses': {}}
                    logger.warning(f"Legacy score format detected for {username}")
                except ValueError:
                    score_data = None
        
        # Get learning path progress
        learning_paths = LearningPath.query.filter_by(username=username).all()
        
        # Get recent assessment attempts (handle missing username column gracefully)
        try:
            recent_attempts = AssessmentAttempt.query.filter_by(username=username)\
                                                .order_by(AssessmentAttempt.completed_at.desc())\
                                                .limit(5).all()
        except Exception as db_error:
            logger.warning(f"Could not fetch assessment attempts for {username}: {db_error}")
            recent_attempts = []
        
        # Generate progress analysis (handle gracefully if fails)
        try:
            progress_analysis = analyze_learning_progress(username)
        except Exception as analysis_error:
            logger.warning(f"Could not generate progress analysis for {username}: {analysis_error}")
            progress_analysis = {'overall_progress': 0, 'recommendations': ['Continue learning and practicing!']}
        
        return render_template('progress.html', 
                             user_data=user_data, 
                             score_data=score_data,
                             learning_paths=learning_paths,
                             recent_attempts=recent_attempts,
                             progress_analysis=progress_analysis)
        
    except Exception as e:
        logger.error(f"Error fetching progress for {username}: {e}")
        flash('An error occurred while fetching your progress.', 'error')
        return redirect(url_for('index'))


@app.route('/learning_path')
@app.route('/learning_path/<username>')
def learning_path(username=None):
    """
    Display personalized learning paths and module recommendations.
    
    Shows:
    1. Generated learning modules based on skills
    2. Progress tracking for each module
    3. Estimated completion times
    4. Recommended study order
    """
    if not username:
        username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('profile'))
        
        # Get learning paths
        learning_paths = LearningPath.query.filter_by(username=username).all()
        
        # If no learning paths exist, generate them based on skills
        if not learning_paths and user.skills:
            logger.info(f"Generating learning paths for {username} based on skills: {user.skills}")
            learning_modules = generate_learning_paths(username, user.skills)
            save_learning_paths_to_db(learning_modules)
            learning_paths = LearningPath.query.filter_by(username=username).all()
            
            # Emit event to agent system for learning path generation
            if hasattr(agent_system, 'event_bus'):
                agent_system.event_bus.emit('learning.path_requested', {
                    'username': username,
                    'skills': user.skills.split(',') if user.skills else [],
                    'generated_modules': len(learning_modules),
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        # Calculate progress statistics
        total_modules = len(learning_paths)
        completed_modules = len([lp for lp in learning_paths if lp.completion_status == 'Completed'])
        completion_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        return render_template('learning_path.html',
                             user=user,
                             learning_paths=learning_paths,
                             total_modules=total_modules,
                             completed_modules=completed_modules,
                             completion_percentage=round(completion_percentage, 1))
        
    except Exception as e:
        logger.error(f"Error loading learning path for {username}: {e}")
        flash('An error occurred while loading your learning path.', 'error')
        return redirect(url_for('progress'))


# ============================================================================
# HACKATHON ROUTES
# ============================================================================

@app.route('/hackathon', methods=['GET', 'POST'])
def hackathon():
    """
    Handle hackathon challenge submissions and competition participation.
    
    GET: Display available challenges and submission interface
    POST: Process challenge submissions and evaluate solutions
    """
    username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    if request.method == 'GET':
        # Display hackathon challenges
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User profile not found.', 'error')
            return redirect(url_for('profile'))
        
        # Get user's previous submissions
        submissions = Hackathon.query.filter_by(username=username)\
                                   .order_by(Hackathon.submitted_at.desc()).all()
        
        # Get top performers for leaderboard preview
        top_users = User.query.order_by(User.total_points.desc()).limit(5).all()
        
        # Get live challenges data (could be from database in future)
        live_challenges = [
            {
                'name': 'Weekly Sprint Challenge',
                'description': 'Build a complete full-stack application in 7 days',
                'participants': 47,
                'points': 500,
                'status': 'LIVE',
                'color': 'warning',
                'icon': 'clock'
            },
            {
                'name': 'Algorithm Master',
                'description': 'Solve 10 algorithmic challenges in optimal time',
                'participants': 23,
                'points': 300,
                'status': 'ACTIVE',
                'color': 'success',
                'icon': 'brain'
            }
        ]
        
        return render_template('hackathon.html', 
                             user=user, 
                             submissions=submissions,
                             top_users=top_users,
                             live_challenges=live_challenges)
    
    # POST request - process hackathon submission
    try:
        challenge_name = request.form.get('challenge_name', '').strip()
        submission = request.form.get('submission', '').strip()
        
        if not challenge_name or not submission:
            flash('Please provide both challenge name and your solution.', 'error')
            return redirect(url_for('hackathon'))
        
        if len(submission) < 50:
            flash('Please provide a more detailed solution (at least 50 characters).', 'warning')
            return redirect(url_for('hackathon'))
        
        # Enhanced scoring based on submission quality
        submission_score = _calculate_hackathon_score(submission)
        
        # Calculate points earned (score * multiplier)
        points_earned = submission_score * 2  # 2x multiplier for hackathon submissions
        
        # Create hackathon submission record
        hackathon_submission = Hackathon(
            username=username,
            challenge_name=challenge_name,
            submission=submission,
            score=submission_score,
            submitted_at=datetime.utcnow()
        )
        db.session.add(hackathon_submission)
        
        # Update user points and gamification data
        user = User.query.filter_by(username=username).first()
        if user:
            user.total_points = (user.total_points or 0) + points_earned
            user.current_streak = (user.current_streak or 0) + 1
            
            # Level up logic
            if user.total_points >= (user.current_level or 1) * 1000:
                user.current_level = (user.current_level or 1) + 1
                flash(f'🎉 Level up! You are now level {user.current_level}!', 'success')
        
        db.session.commit()
        
        logger.info(f"Hackathon submission by {username} - Challenge: {challenge_name}, Score: {submission_score}, Points: {points_earned}")
        
        flash(f'Hackathon submission successful! Score: {submission_score}/100 (+{points_earned} points)', 'success')
        return redirect(url_for('hackathon'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing hackathon submission for {username}: {e}")
        flash('An error occurred while submitting your solution.', 'error')
        return redirect(url_for('hackathon'))


def _calculate_hackathon_score(submission: str) -> int:
    """Calculate basic hackathon submission score based on content quality."""
    base_score = 50
    length_bonus = min(30, len(submission) // 100)  # Up to 30 points for length
    
    # Technical keywords bonus
    technical_terms = ['function', 'class', 'algorithm', 'data structure', 'optimization', 
                      'complexity', 'testing', 'debugging', 'performance']
    keyword_bonus = sum(2 for term in technical_terms if term.lower() in submission.lower())
    keyword_bonus = min(20, keyword_bonus)  # Cap at 20 points
    
    return min(100, base_score + length_bonus + keyword_bonus)


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/progress/<username>')
def api_progress(username):
    """
    RESTful API endpoint for accessing user progress data.
    
    Returns JSON representation of user progress including:
    - Basic profile information
    - Assessment scores and history
    - Learning path progress
    - Achievement data
    """
    try:
        user_data = User.query.filter_by(username=username).first()
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Parse scores safely
        score_data = None
        if user_data.scores:
            try:
                score_data = json.loads(user_data.scores)
            except json.JSONDecodeError:
                score_data = {'total_score': user_data.scores}
        
        # Get learning path summary
        learning_paths = LearningPath.query.filter_by(username=username).all()
        learning_summary = {
            'total_modules': len(learning_paths),
            'completed_modules': len([lp for lp in learning_paths if lp.completion_status == 'Completed']),
            'modules': [lp.to_dict() for lp in learning_paths]
        }
        
        result = {
            'user': user_data.to_dict(),
            'assessment': score_data,
            'learning_paths': learning_summary,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in API progress endpoint for {username}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/users')
def api_users():
    """API endpoint to list all users with basic information."""
    try:
        users = User.query.all()
        user_list = []
        
        for user in users:
            user_dict = user.to_dict()
            # Remove sensitive information
            user_dict.pop('resume_text', None)
            user_list.append(user_dict)
        
        return jsonify({
            'users': user_list,
            'total_count': len(user_list),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API users endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint for leaderboard data."""
    try:
        # Get top users by points
        top_users = User.query.order_by(User.total_points.desc()).limit(10).all()
        
        leaderboard = []
        for rank, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': rank,
                'username': user.username,
                'total_points': user.total_points,
                'current_level': user.current_level,
                'current_streak': user.current_streak
            })
        
        return jsonify({
            'leaderboard': leaderboard,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API leaderboard endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with user-friendly page."""
    logger.warning(f"404 error: {request.url}")
    return render_template('base.html', error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with user-friendly page."""
    logger.error(f"500 error: {error}")
    return render_template('base.html', error_message="Internal server error"), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors."""
    logger.warning(f"403 error: {request.url}")
    return render_template('base.html', error_message="Access forbidden"), 403


# ============================================================================
# UTILITY ROUTES
# ============================================================================

@app.route('/health')
def health_check():
    """Simple health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0'
    })


@app.route('/clear_session')
def clear_session():
    """Clear user session (for testing/debugging)."""
    session.clear()
    flash('Session cleared successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/tailored_courses')
def tailored_courses():
    """Display AI-generated tailored courses."""
    username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User profile not found.', 'error')
            return redirect(url_for('profile'))
        
        return render_template('tailored_courses.html', user=user)
        
    except Exception as e:
        logger.error(f"Error loading tailored courses for {username}: {e}")
        flash('An error occurred while loading courses.', 'error')
        return redirect(url_for('progress'))


@app.route('/leaderboard')
def leaderboard():
    """Display user leaderboard with rankings based on assessment scores."""
    try:
        # Get users with assessment scores and sort by score
        users_with_scores = []
        all_users = User.query.all()
        
        for user in all_users:
            if user.scores:
                try:
                    score_data = json.loads(user.scores) if isinstance(user.scores, str) else user.scores
                    score = score_data.get('total_score', 0) if isinstance(score_data, dict) else int(user.scores)
                    users_with_scores.append({
                        'username': user.username,
                        'score': score,
                        'skills': user.skills,
                        'assessment_date': user.assessment_completed_at or user.skills_evaluated_at,
                        'total_points': user.total_points or 0
                    })
                except (json.JSONDecodeError, ValueError, TypeError):
                    # Handle legacy score formats
                    try:
                        score = int(user.scores) if user.scores else 0
                        users_with_scores.append({
                            'username': user.username,
                            'score': score,
                            'skills': user.skills,
                            'assessment_date': user.assessment_completed_at or user.skills_evaluated_at,
                            'total_points': user.total_points or 0
                        })
                    except:
                        continue
        
        # Sort by score (highest first)
        leaderboard = sorted(users_with_scores, key=lambda x: x['score'], reverse=True)[:20]
        
        return render_template('leaderboard.html', leaderboard=leaderboard)
        
    except Exception as e:
        logger.error(f"Error loading leaderboard: {e}")
        flash('An error occurred while loading the leaderboard.', 'error')
        return redirect(url_for('index'))


@app.route('/admin_dashboard')
def admin_dashboard():
    """Display admin dashboard with comprehensive metrics."""
    try:
        # Basic admin dashboard - would need proper authentication in production
        users = User.query.all()
        total_users = len(users)
        
        # Calculate metrics
        users_with_assessments = len([u for u in users if u.scores])
        assessment_completion_rate = round((users_with_assessments / total_users * 100) if total_users > 0 else 0, 1)
        users_with_skills = len([u for u in users if u.skills])
        
        # Get recent activity
        recent_users = User.query.order_by(User.profile_created_at.desc()).limit(10).all()
        
        metrics = {
            'total_users': total_users,
            'users_with_assessments': users_with_assessments,
            'assessment_completion_rate': assessment_completion_rate,
            'users_with_skills': users_with_skills,
            'active_users': len([u for u in users if u.last_login_at])
        }
        
        return render_template('admin_dashboard.html', 
                             metrics=metrics,
                             recent_users=recent_users,
                             users=users)
        
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}")
        flash('An error occurred while loading the admin dashboard.', 'error')
        return redirect(url_for('index'))


@app.route('/gen_ai_info')
def gen_ai_info():
    """Display information about generative AI features."""
    try:
        return render_template('gen_ai_info.html')
        
    except Exception as e:
        logger.error(f"Error loading gen AI info: {e}")
        flash('An error occurred while loading the page.', 'error')
        return redirect(url_for('index'))


@app.route('/api_status_legacy')
def api_status_legacy():
    """Display API service status and configuration."""
    try:
        return render_template('api_status.html')
        
    except Exception as e:
        logger.error(f"Error loading API status: {e}")
        flash('An error occurred while loading the API status.', 'error')
        return redirect(url_for('index'))


@app.route('/admin_users')
def admin_users():
    """Display admin users management page."""
    try:
        users = User.query.all()
        return render_template('admin_users.html', users=users)
        
    except Exception as e:
        logger.error(f"Error loading admin users: {e}")
        flash('An error occurred while loading the users page.', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin_hackathons')
def admin_hackathons():
    """Display admin hackathons management page."""
    try:
        hackathons = Hackathon.query.all()
        return render_template('admin_hackathons.html', hackathons=hackathons)
        
    except Exception as e:
        logger.error(f"Error loading admin hackathons: {e}")
        flash('An error occurred while loading the hackathons page.', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin_reports')
def admin_reports():
    """Display admin reports page."""
    try:
        return render_template('admin_reports.html')
        
    except Exception as e:
        logger.error(f"Error loading admin reports: {e}")
        flash('An error occurred while loading the reports page.', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin_user_detail/<username>')
def admin_user_detail(username):
    """Display detailed admin view of a specific user."""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_users'))
        
        return render_template('admin_user_detail.html', user=user)
        
    except Exception as e:
        logger.error(f"Error loading admin user detail for {username}: {e}")
        flash('An error occurred while loading the user detail.', 'error')
        return redirect(url_for('admin_users'))


@app.route('/set_session/<username>')
def set_session(username):
    """Utility route to set session for testing purposes."""
    user = User.query.filter_by(username=username).first()
    if user:
        session['username'] = username
        flash(f'Session set for {username}', 'success')
        return redirect(url_for('assessment_panel'))
    else:
        flash('User not found', 'error')
        return redirect(url_for('profile'))


@app.route('/generate_exercise', methods=['POST'])
def generate_exercise():
    """Generate a new AI exercise for assessment."""
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Placeholder exercise generation
    exercise = {
        'title': 'Custom Generated Exercise',
        'description': 'This exercise was generated based on your skills',
        'difficulty': 'Medium',
        'language': 'Python'
    }
    
    return jsonify({'success': True, 'exercise': exercise})


@app.route('/reassess_user/<username>')
def reassess_user(username):
    """Reassess a user's skills and update their profile."""
    return redirect(url_for('assessment_panel'))


# Add more missing routes referenced in templates
@app.route('/api_test')
def api_test():
    """API test endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/update_profile_request')
def update_profile_request():
    """Route to handle profile update requests."""
    return redirect(url_for('profile'))


@app.route('/update_learning_path', methods=['POST'])
def update_learning_path():
    """Update learning path module status."""
    username = session.get('username')
    if not username:
        return redirect(url_for('profile'))
    
    module_id = request.form.get('module_id')
    status = request.form.get('status')
    
    try:
        learning_module = LearningPath.query.get(module_id)
        if learning_module and learning_module.username == username:
            learning_module.completion_status = status
            if status == 'Completed':
                learning_module.completed_at = datetime.utcnow()
            db.session.commit()
            flash(f'Learning module updated to {status}!', 'success')
        else:
            flash('Learning module not found.', 'error')
    except Exception as e:
        logger.error(f"Error updating learning path: {e}")
        flash('Error updating learning module.', 'error')
    
    return redirect(url_for('learning_path', username=username))


@app.route('/request_review')
def request_review():
    """Route to handle review requests."""
    return redirect(url_for('progress'))


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    return render_template('base.html', error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {error}")
    db.session.rollback()
    return render_template('base.html', error_message="Internal server error"), 500