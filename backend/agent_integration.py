"""
Agent System Integration Layer
=============================

This file provides integration between the Flask application and the agent system.
It serves as a bridge between web requests and intelligent agent processing.

Key Components:
1. Agent System Wrapper: Manages agent lifecycle and communication
2. Event Processing: Handles event emission and routing to appropriate agents
3. API Endpoints: Provides RESTful access to agent functionality
4. Status Monitoring: Tracks agent health and performance
5. Error Handling: Graceful degradation when agents are unavailable

The agent system consists of 6 specialized agents:
- ProfileAgent: Resume analysis and skill extraction
- AssessmentAgent: Exercise generation and evaluation
- GamificationAgent: Points, badges, and achievements
- LearningPathAgent: Personalized curriculum creation
- HackathonAgent: Coding competition management
- AnalyticsAgent: Platform analytics and insights
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from flask import jsonify, request, session

# Import agent system components with error handling
try:
    from agents import (
        EventBus, ProfileAgent, AssessmentAgent, 
        LearningPathAgent, HackathonAgent, 
        GamificationAgent, AnalyticsAgent
    )
    AGENTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Agent system not available: {e}")
    AGENTS_AVAILABLE = False

from app import app

logger = logging.getLogger(__name__)


class AgentSystemManager:
    """
    Central manager for the agent system integration.
    
    Provides high-level interface for interacting with agents,
    manages their lifecycle, and handles error conditions gracefully.
    """
    
    def __init__(self, flask_app=None):
        self.app = flask_app
        self.event_bus = None
        self.agents = {}
        self.initialized = False
        self.health_status = {}
        
        if flask_app and AGENTS_AVAILABLE:
            self.init_app(flask_app)
        elif not AGENTS_AVAILABLE:
            logger.warning("Agent system unavailable - running in fallback mode")
    
    def init_app(self, flask_app):
        """
        Initialize the agent system with Flask application.
        
        Sets up:
        - Event bus for inter-agent communication
        - Individual agent instances
        - API route registration
        - Health monitoring
        """
        if not AGENTS_AVAILABLE:
            logger.warning("Cannot initialize agent system - agents not available")
            return False
        
        try:
            # Initialize event bus with appropriate configuration
            self.event_bus = EventBus(max_event_history=5000)
            
            # Initialize all agents
            self.agents = {
                'profile': ProfileAgent(self.event_bus),
                'assessment': AssessmentAgent(self.event_bus),
                'learning_path': LearningPathAgent(self.event_bus),
                'hackathon': HackathonAgent(self.event_bus),
                'gamification': GamificationAgent(self.event_bus),
                'analytics': AnalyticsAgent(self.event_bus)
            }
            
            logger.info(f"Initialized {len(self.agents)} agents successfully")
            
            # Register API routes for agent interaction
            self._register_agent_routes(flask_app)
            
            # Initialize health monitoring
            self._update_health_status()
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent system: {e}")
            self.initialized = False
            return False
    
    def emit_event(self, event_type: str, event_data: Dict[str, Any], 
                   username: Optional[str] = None) -> bool:
        """
        Emit an event to the agent system for processing.
        
        Args:
            event_type: Type of event (e.g., 'user.registered', 'assessment.completed')
            event_data: Event payload data
            username: User associated with this event
            
        Returns:
            bool: True if event was emitted successfully, False otherwise
        """
        if not self.initialized:
            logger.warning(f"Cannot emit event {event_type} - agent system not initialized")
            return False
        
        try:
            # Add standard metadata to event
            enriched_data = {
                **event_data,
                'timestamp': datetime.utcnow().isoformat(),
                'username': username or session.get('username'),
                'session_id': session.get('session_id', 'unknown'),
                'source': 'web_application'
            }
            
            # Emit event to all listening agents
            self.event_bus.emit(event_type, enriched_data)
            
            logger.debug(f"Event emitted: {event_type} for user {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")
            return False
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all agents and the event bus.
        
        Returns:
            dict: Status information for monitoring and debugging
        """
        if not self.initialized:
            return {
                'initialized': False,
                'agent_count': 0,
                'error': 'Agent system not initialized'
            }
        
        try:
            status = {
                'initialized': True,
                'agent_count': len(self.agents),
                'event_bus_health': self.event_bus.get_health_status() if hasattr(self.event_bus, 'get_health_status') else 'unknown',
                'agents': {}
            }
            
            # Get status for each agent
            for agent_name, agent in self.agents.items():
                try:
                    if hasattr(agent, 'get_status'):
                        agent_status = agent.get_status()
                    else:
                        agent_status = {'status': 'active', 'type': type(agent).__name__}
                    
                    status['agents'][agent_name] = agent_status
                    
                except Exception as e:
                    status['agents'][agent_name] = {'status': 'error', 'error': str(e)}
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {'initialized': False, 'error': str(e)}
    
    def process_user_registration(self, username: str, resume_text: str, skills: str) -> Dict[str, Any]:
        """
        Process new user registration through the agent system.
        
        Triggers:
        - ProfileAgent: Analyze resume and extract detailed skills
        - GamificationAgent: Initialize user points and achievements
        - AnalyticsAgent: Record user registration event
        
        Args:
            username: New user's username
            resume_text: Extracted resume content
            skills: Initially extracted skills
            
        Returns:
            dict: Processing results and any recommendations
        """
        if not self.initialized:
            return {'success': False, 'error': 'Agent system unavailable'}
        
        try:
            # Emit user registration event
            registration_data = {
                'username': username,
                'resume_text': resume_text,
                'initial_skills': skills,
                'registration_time': datetime.utcnow().isoformat()
            }
            
            success = self.emit_event('user.registered', registration_data, username)
            
            if success:
                logger.info(f"User registration processed by agents: {username}")
                return {
                    'success': True,
                    'message': 'User registration processed by agent system',
                    'events_triggered': ['user.registered']
                }
            else:
                return {'success': False, 'error': 'Failed to emit registration event'}
                
        except Exception as e:
            logger.error(f"Error processing user registration for {username}: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_assessment_completion(self, username: str, responses: Dict[str, str], 
                                   score: int) -> Dict[str, Any]:
        """
        Process assessment completion through the agent system.
        
        Triggers:
        - AssessmentAgent: Analyze responses and generate recommendations
        - GamificationAgent: Award points and check for achievements
        - LearningPathAgent: Update learning recommendations
        - AnalyticsAgent: Record assessment performance
        """
        if not self.initialized:
            return {'success': False, 'error': 'Agent system unavailable'}
        
        try:
            assessment_data = {
                'username': username,
                'responses': responses,
                'score': score,
                'completion_time': datetime.utcnow().isoformat()
            }
            
            success = self.emit_event('assessment.completed', assessment_data, username)
            
            if success:
                logger.info(f"Assessment completion processed by agents: {username} (score: {score})")
                return {
                    'success': True,
                    'message': 'Assessment completion processed by agent system',
                    'events_triggered': ['assessment.completed']
                }
            else:
                return {'success': False, 'error': 'Failed to emit assessment event'}
                
        except Exception as e:
            logger.error(f"Error processing assessment completion for {username}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _register_agent_routes(self, flask_app):
        """Register API routes for agent system interaction."""
        
        @flask_app.route('/api/agents/status')
        def api_agent_status():
            """Get agent system status."""
            return jsonify(self.get_agent_status())
        
        @flask_app.route('/api/agents/events', methods=['POST'])
        def api_emit_event():
            """Manually emit an event to the agent system."""
            try:
                data = request.get_json()
                event_type = data.get('event_type')
                event_data = data.get('event_data', {})
                username = data.get('username')
                
                if not event_type:
                    return jsonify({'error': 'event_type is required'}), 400
                
                success = self.emit_event(event_type, event_data, username)
                
                if success:
                    return jsonify({'success': True, 'message': 'Event emitted successfully'})
                else:
                    return jsonify({'success': False, 'error': 'Failed to emit event'}), 500
                    
            except Exception as e:
                logger.error(f"Error in manual event emission: {e}")
                return jsonify({'error': str(e)}), 500
        
        @flask_app.route('/api/agents/event_history')
        def api_event_history():
            """Get recent event history from the event bus."""
            try:
                if hasattr(self.event_bus, 'get_event_history'):
                    history = self.event_bus.get_event_history()
                    return jsonify({'events': history})
                else:
                    return jsonify({'error': 'Event history not available'}), 404
                    
            except Exception as e:
                logger.error(f"Error getting event history: {e}")
                return jsonify({'error': str(e)}), 500
        
        @flask_app.route('/api/agents/<agent_name>/status')
        def api_individual_agent_status(agent_name):
            """Get status of a specific agent."""
            try:
                if agent_name not in self.agents:
                    return jsonify({'error': f'Agent {agent_name} not found'}), 404
                
                agent = self.agents[agent_name]
                if hasattr(agent, 'get_status'):
                    status = agent.get_status()
                else:
                    status = {'status': 'active', 'type': type(agent).__name__}
                
                return jsonify(status)
                
            except Exception as e:
                logger.error(f"Error getting status for agent {agent_name}: {e}")
                return jsonify({'error': str(e)}), 500
    
    def _update_health_status(self):
        """Update internal health status tracking."""
        try:
            self.health_status = {
                'last_check': datetime.utcnow().isoformat(),
                'agent_count': len(self.agents),
                'event_bus_active': self.event_bus is not None,
                'overall_health': 'healthy' if self.initialized else 'unhealthy'
            }
            
        except Exception as e:
            logger.error(f"Error updating health status: {e}")
            self.health_status = {
                'last_check': datetime.utcnow().isoformat(),
                'overall_health': 'error',
                'error': str(e)
            }


# ============================================================================
# GLOBAL AGENT SYSTEM MANAGER INSTANCE
# ============================================================================

# Create global instance that will be initialized by app.py
agent_manager = AgentSystemManager()


def init_agent_system(flask_app):
    """
    Initialize the global agent system manager.
    
    Called from app.py during application startup.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        AgentSystemManager: Initialized manager instance
    """
    global agent_manager
    
    if agent_manager.init_app(flask_app):
        logger.info("Agent system integration initialized successfully")
    else:
        logger.warning("Agent system integration failed - running in fallback mode")
    
    return agent_manager


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def emit_user_event(event_type: str, event_data: Dict[str, Any], 
                   username: Optional[str] = None) -> bool:
    """
    Convenience function to emit user-related events.
    
    Args:
        event_type: Type of event to emit
        event_data: Event payload
        username: Username (defaults to session username)
        
    Returns:
        bool: True if successful, False otherwise
    """
    return agent_manager.emit_event(event_type, event_data, username)


def get_agent_recommendations(username: str) -> Dict[str, Any]:
    """
    Get personalized recommendations from all agents for a user.
    
    Args:
        username: User to get recommendations for
        
    Returns:
        dict: Compiled recommendations from all agents
    """
    if not agent_manager.initialized:
        return {'error': 'Agent system unavailable'}
    
    try:
        # This would trigger agents to generate recommendations
        # Implementation depends on specific agent capabilities
        recommendations = {
            'username': username,
            'generated_at': datetime.utcnow().isoformat(),
            'sources': []
        }
        
        # In a full implementation, this would query each agent
        # for their specific recommendations
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting agent recommendations for {username}: {e}")
        return {'error': str(e)}


def is_agent_system_available() -> bool:
    """
    Check if the agent system is available and functioning.
    
    Returns:
        bool: True if agent system is available, False otherwise
    """
    return AGENTS_AVAILABLE and agent_manager.initialized