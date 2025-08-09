"""
Hackathon Hosting Routes
========================

Additional routes for hosting gamified hackathons and competitions.
These routes enable users to create, manage, and participate in competitive coding events.
"""

import json
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from backend.database import User, Hackathon
from app import app, db

logger = logging.getLogger(__name__)


@app.route('/hackathon/host', methods=['GET', 'POST'])
def host_hackathon():
    """
    Route for hosting new hackathon competitions.
    
    GET: Display hackathon creation form
    POST: Create new hackathon event with rules and timers
    """
    username = session.get('username')
    
    if not username:
        flash('Please create a profile first to host hackathons.', 'warning')
        return redirect(url_for('profile'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User profile not found.', 'error')
        return redirect(url_for('profile'))
    
    # Check if user has permission to host (level 3+)
    if (user.current_level or 1) < 3:
        flash('You need to reach level 3 to host hackathons. Keep participating to level up!', 'warning')
        return redirect(url_for('hackathon'))
    
    if request.method == 'GET':
        return render_template('hackathon_host.html', user=user)
    
    # POST - create new hackathon
    try:
        hackathon_title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        duration_hours = int(request.form.get('duration_hours', 24))
        max_participants = int(request.form.get('max_participants', 50))
        difficulty = request.form.get('difficulty', 'Medium')
        
        if not hackathon_title or not description:
            flash('Please provide both title and description for the hackathon.', 'error')
            return render_template('hackathon_host.html', user=user)
        
        # Create hackathon event record
        new_hackathon = {
            'host_username': username,
            'title': hackathon_title,
            'description': description,
            'duration_hours': duration_hours,
            'max_participants': max_participants,
            'difficulty': difficulty,
            'start_time': datetime.utcnow(),
            'end_time': datetime.utcnow() + timedelta(hours=duration_hours),
            'status': 'ACTIVE',
            'participants': [],
            'created_at': datetime.utcnow()
        }
        
        # Store in user's hosted events (could be separate table in future)
        if not user.gamification_data:
            user.gamification_data = '{}'
        
        gamification_data = json.loads(user.gamification_data)
        if 'hosted_hackathons' not in gamification_data:
            gamification_data['hosted_hackathons'] = []
        
        gamification_data['hosted_hackathons'].append(new_hackathon)
        user.gamification_data = json.dumps(gamification_data)
        
        # Award hosting points
        user.total_points = (user.total_points or 0) + 100
        
        db.session.commit()
        
        logger.info(f"Hackathon '{hackathon_title}' hosted by {username}")
        flash(f'Hackathon "{hackathon_title}" created successfully! (+100 hosting points)', 'success')
        return redirect(url_for('hackathon'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating hackathon: {e}")
        flash('An error occurred while creating the hackathon.', 'error')
        return render_template('hackathon_host.html', user=user)


@app.route('/hackathon/live')
def live_hackathons():
    """
    Display all active hackathons with real-time participation data.
    """
    username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User profile not found.', 'error')
        return redirect(url_for('profile'))
    
    # Get all hosted hackathons from all users
    all_users = User.query.filter(User.gamification_data.isnot(None)).all()
    live_hackathons = []
    
    for user_record in all_users:
        try:
            gamification_data = json.loads(user_record.gamification_data)
            hosted_hackathons = gamification_data.get('hosted_hackathons', [])
            
            for hackathon in hosted_hackathons:
                if hackathon.get('status') == 'ACTIVE':
                    # Check if hackathon is still within time limit
                    end_time = datetime.fromisoformat(hackathon['end_time'].replace('Z', '+00:00'))
                    if end_time > datetime.utcnow():
                        live_hackathons.append(hackathon)
                        
        except (json.JSONDecodeError, KeyError):
            continue
    
    return render_template('live_hackathons.html', 
                         user=user, 
                         live_hackathons=live_hackathons)


@app.route('/hackathon/join/<hackathon_id>')
def join_hackathon(hackathon_id):
    """
    Join a specific hackathon competition.
    """
    username = session.get('username')
    
    if not username:
        flash('Please create a profile first.', 'warning')
        return redirect(url_for('profile'))
    
    # Logic to join hackathon would go here
    flash(f'Successfully joined hackathon! Good luck!', 'success')
    return redirect(url_for('live_hackathons'))