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
        
        return render_template('assessment_panel.html', user=user)
    
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
        
        # Get recent assessment attempts
        recent_attempts = AssessmentAttempt.query.filter_by(username=username)\
                                                .order_by(AssessmentAttempt.completed_at.desc())\
                                                .limit(5).all()
        
        # Generate progress analysis
        progress_analysis = analyze_learning_progress(username)
        
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
        
        # If no learning paths exist, generate them
        if not learning_paths and user.skills:
            learning_modules = generate_learning_paths(username, user.skills)
            save_learning_paths_to_db(learning_modules)
            learning_paths = LearningPath.query.filter_by(username=username).all()
        
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
        
        return render_template('hackathon.html', user=user, submissions=submissions)
    
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
        
        # Basic scoring based on submission quality
        submission_score = _calculate_hackathon_score(submission)
        
        # Create hackathon submission record
        hackathon_submission = Hackathon(
            username=username,
            challenge_name=challenge_name,
            submission=submission,
            score=submission_score,
            submitted_at=datetime.utcnow()
        )
        db.session.add(hackathon_submission)
        db.session.commit()
        
        logger.info(f"Hackathon submission by {username} - Challenge: {challenge_name}, Score: {submission_score}")
        
        flash(f'Hackathon submission successful! Score: {submission_score}/100', 'success')
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
    """Display user leaderboard with rankings."""
    try:
        # Get top users by points
        top_users = User.query.order_by(User.total_points.desc()).limit(20).all()
        
        return render_template('leaderboard.html', top_users=top_users)
        
    except Exception as e:
        logger.error(f"Error loading leaderboard: {e}")
        flash('An error occurred while loading the leaderboard.', 'error')
        return redirect(url_for('index'))


@app.route('/admin_dashboard')
def admin_dashboard():
    """Display admin dashboard (placeholder for now)."""
    try:
        # Basic admin dashboard - would need proper authentication in production
        users = User.query.all()
        total_users = len(users)
        
        return render_template('admin_dashboard.html', 
                             total_users=total_users,
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


@app.route('/api_status')
def api_status():
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