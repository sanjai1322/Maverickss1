"""
Agent System Integration
========================

Integrates the agent-based architecture with the Flask application.
Provides centralized agent management, event routing, and API endpoints.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import jsonify, request

# Import agents with error handling
try:
    from agents import (
        EventBus, ProfileAgent, AssessmentAgent, 
        LearningPathAgent, HackathonAgent, 
        GamificationAgent, AnalyticsAgent
    )
    agents_available = True
except ImportError as e:
    logging.warning(f"Agent system not available: {e}")
    agents_available = False

logger = logging.getLogger(__name__)

class AgentSystem:
    """
    Central agent management system for the Mavericks platform.
    
    Orchestrates communication between agents, manages the event bus,
    and provides API endpoints for agent interactions.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.event_bus = None
        self.agents = {}
        self.initialized = False
        
        if app and agents_available:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize agent system with Flask app"""
        if not agents_available:
            logger.warning("Agent system initialization skipped - agents not available")
            return
        
        try:
            # Initialize event bus
            self.event_bus = EventBus(max_event_history=5000)
            
            # Initialize agents
            self.agents = {
                'profile': ProfileAgent(self.event_bus),
                'assessment': AssessmentAgent(self.event_bus), 
                'learning_path': LearningPathAgent(self.event_bus),
                'hackathon': HackathonAgent(self.event_bus),
                'gamification': GamificationAgent(self.event_bus),
                'analytics': AnalyticsAgent(self.event_bus)
            }
            
            logger.info(f"Initialized {len(self.agents)} agents with event bus")
            
            # Register API routes
            self._register_routes(app)
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent system: {e}")
            self.initialized = False
    
    def _register_routes(self, app):
        """Register agent system API routes"""
        
        @app.route('/api/agents/status')
        def agents_status():
            """Get status of all agents"""
            if not self.initialized:
                return jsonify({"error": "Agent system not initialized"}), 500
            
            status = {}
            for name, agent in self.agents.items():
                try:
                    status[name] = agent.health_check()
                except Exception as e:
                    status[name] = {"status": "error", "error": str(e)}
            
            return jsonify({
                "agent_system_status": "operational" if self.initialized else "offline",
                "event_bus_stats": self.event_bus.get_event_analytics() if self.event_bus else {},
                "agents": status
            })
        
        @app.route('/api/agents/capabilities')
        def agents_capabilities():
            """Get capabilities of all agents"""
            if not self.initialized:
                return jsonify({"error": "Agent system not initialized"}), 500
            
            capabilities = {}
            for name, agent in self.agents.items():
                try:
                    capabilities[name] = agent.get_capabilities()
                except Exception as e:
                    capabilities[name] = {"error": str(e)}
            
            return jsonify(capabilities)
        
        @app.route('/api/agents/analytics/overview')
        def analytics_overview():
            """Get platform analytics overview"""
            if not self.initialized or 'analytics' not in self.agents:
                return jsonify({"error": "Analytics agent not available"}), 500
            
            try:
                overview = self.agents['analytics'].get_platform_overview()
                return jsonify(overview)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/agents/analytics/user/<user_id>')
        def user_analytics(user_id):
            """Get analytics for specific user"""
            if not self.initialized or 'analytics' not in self.agents:
                return jsonify({"error": "Analytics agent not available"}), 500
            
            try:
                analytics = self.agents['analytics'].get_user_analytics(user_id)
                return jsonify(analytics)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/agents/gamification/profile/<user_id>')
        def gamification_profile(user_id):
            """Get gamification profile for user"""
            if not self.initialized or 'gamification' not in self.agents:
                return jsonify({"error": "Gamification agent not available"}), 500
            
            try:
                profile = self.agents['gamification'].get_user_profile(user_id)
                return jsonify(profile)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/agents/gamification/leaderboard')
        def gamification_leaderboard():
            """Get platform leaderboard"""
            if not self.initialized or 'gamification' not in self.agents:
                return jsonify({"error": "Gamification agent not available"}), 500
            
            try:
                category = request.args.get('category', 'total_points')
                limit = int(request.args.get('limit', 50))
                leaderboard = self.agents['gamification'].get_leaderboard(category, limit)
                return jsonify(leaderboard)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/agents/learning/dashboard/<user_id>')
        def learning_dashboard(user_id):
            """Get learning dashboard for user"""
            if not self.initialized or 'learning_path' not in self.agents:
                return jsonify({"error": "Learning path agent not available"}), 500
            
            try:
                dashboard = self.agents['learning_path'].get_user_learning_dashboard(user_id)
                return jsonify(dashboard)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/agents/hackathon/status/<hackathon_id>')
        def hackathon_status(hackathon_id):
            """Get hackathon status"""
            if not self.initialized or 'hackathon' not in self.agents:
                return jsonify({"error": "Hackathon agent not available"}), 500
            
            try:
                status = self.agents['hackathon'].get_hackathon_status(hackathon_id)
                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/agents/events/user/<user_id>')
        def user_events(user_id):
            """Get recent events for user"""
            if not self.initialized or not self.event_bus:
                return jsonify({"error": "Event bus not available"}), 500
            
            try:
                event_types = request.args.get('event_types')
                event_types = event_types.split(',') if event_types else None
                limit = int(request.args.get('limit', 50))
                
                events = self.event_bus.get_events_for_user(user_id, event_types, limit)
                return jsonify(events)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def emit_event(self, event_type: str, user_id: str, payload: Dict[str, Any], 
                   source_agent: str = "system", target_agent: Optional[str] = None) -> str:
        """Emit an event through the agent system"""
        if not self.initialized or not self.event_bus:
            logger.warning("Cannot emit event - agent system not initialized")
            return ""
        
        try:
            from agents.base_agent import AgentEvent
            
            event = AgentEvent(
                event_type=event_type,
                source_agent=source_agent,
                target_agent=target_agent,
                user_id=user_id,
                payload=payload,
                timestamp=datetime.utcnow(),
                event_id=f"{source_agent}_{event_type}_{datetime.utcnow().timestamp()}"
            )
            
            return self.event_bus.emit(event)
            
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")
            return ""
    
    def get_agent(self, agent_name: str):
        """Get specific agent by name"""
        return self.agents.get(agent_name)
    
    def process_user_registration(self, user_id: str, username: str, **kwargs) -> Dict[str, Any]:
        """Process new user registration through agent system"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        event_id = self.emit_event(
            "user.registered",
            user_id,
            {"username": username, **kwargs},
            "system"
        )
        
        return {"status": "user_registration_processed", "event_id": event_id}
    
    def process_resume_upload(self, user_id: str, resume_text: str) -> Dict[str, Any]:
        """Process resume upload through agent system"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        event_id = self.emit_event(
            "resume.uploaded",
            user_id,
            {"resume_text": resume_text},
            "system"
        )
        
        return {"status": "resume_processed", "event_id": event_id}
    
    def process_assessment_completion(self, user_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process assessment completion through agent system"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        event_id = self.emit_event(
            "assessment.completed",
            user_id,
            {"final_results": results},
            "system"
        )
        
        return {"status": "assessment_processed", "event_id": event_id}
    
    def process_exercise_submission(self, user_id: str, exercise_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process exercise submission through agent system"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        event_id = self.emit_event(
            "exercise.solution_submitted",
            user_id,
            exercise_data,
            "system"
        )
        
        return {"status": "exercise_processed", "event_id": event_id}
    
    def process_hackathon_submission(self, user_id: str, hackathon_id: str, 
                                   submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process hackathon submission through agent system"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        event_id = self.emit_event(
            "hackathon.submission_made",
            user_id,
            {
                "hackathon_id": hackathon_id,
                "submission_data": submission_data
            },
            "system"
        )
        
        return {"status": "hackathon_submission_processed", "event_id": event_id}
    
    def process_daily_login(self, user_id: str) -> Dict[str, Any]:
        """Process daily login through agent system"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        event_id = self.emit_event(
            "user.daily_login",
            user_id,
            {"login_time": datetime.utcnow().isoformat()},
            "system"
        )
        
        return {"status": "daily_login_processed", "event_id": event_id}
    
    def get_user_profile_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user profile data from all agents"""
        if not self.initialized:
            return {"error": "Agent system not initialized"}
        
        profile_data = {"user_id": user_id}
        
        try:
            # Get profile agent data
            if 'profile' in self.agents:
                profile_data['profile'] = self.agents['profile'].get_user_profile(user_id)
            
            # Get gamification data
            if 'gamification' in self.agents:
                profile_data['gamification'] = self.agents['gamification'].get_user_profile(user_id)
            
            # Get learning data
            if 'learning_path' in self.agents:
                profile_data['learning'] = self.agents['learning_path'].get_user_learning_dashboard(user_id)
            
            # Get analytics data
            if 'analytics' in self.agents:
                profile_data['analytics'] = self.agents['analytics'].get_user_analytics(user_id)
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error getting user profile data: {e}")
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown the agent system"""
        if self.event_bus:
            self.event_bus.shutdown()
        
        logger.info("Agent system shutdown complete")

# Global agent system instance
agent_system = AgentSystem()

def init_agent_system(app):
    """Initialize agent system with Flask app"""
    global agent_system
    agent_system.init_app(app)
    return agent_system