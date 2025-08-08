"""
Agent-Based Coding Platform Architecture
=======================================

This module implements a comprehensive agent-based architecture for the Mavericks
coding platform, featuring autonomous agents that collaborate through a message bus
to provide personalized learning, assessment, and hackathon experiences.

Agent Types:
- ProfileAgent: User skill analysis and profile management
- AssessmentAgent: Automated coding skill evaluation
- LearningPathAgent: Personalized curriculum generation
- HackathonAgent: Challenge management and evaluation
- GamificationAgent: Points, badges, and leaderboards
- AnalyticsAgent: Performance insights and reporting

Each agent operates independently, processes events, and emits structured messages
through the central EventBus for seamless coordination.
"""

# Import statement handling with graceful fallbacks
try:
    from .base_agent import BaseAgent
    from .event_bus import EventBus
    from .profile_agent import ProfileAgent
    from .assessment_agent import AssessmentAgent
    from .learning_path_agent import LearningPathAgent
    from .hackathon_agent import HackathonAgent
    from .gamification_agent import GamificationAgent
    from .analytics_agent import AnalyticsAgent
except ImportError as e:
    import logging
    logging.warning(f"Some agents could not be imported: {e}")
    
    # Provide minimal fallback classes if needed
    BaseAgent = None
    EventBus = None

__all__ = [
    'BaseAgent', 
    'EventBus', 
    'ProfileAgent', 
    'AssessmentAgent', 
    'LearningPathAgent',
    'HackathonAgent', 
    'GamificationAgent', 
    'AnalyticsAgent'
]