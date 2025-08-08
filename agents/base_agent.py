"""
Base Agent Class
================

Provides the foundation for all agents in the Mavericks platform.
Each agent can process events, maintain state, and emit structured messages.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class AgentEvent:
    """Structured event format for inter-agent communication"""
    event_type: str
    source_agent: str
    target_agent: Optional[str]
    user_id: str
    payload: Dict[str, Any]
    timestamp: datetime
    event_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentEvent':
        """Create event from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class BaseAgent(ABC):
    """
    Base class for all agents in the Mavericks platform.
    
    Provides common functionality for event processing, state management,
    and communication through the central message bus.
    """
    
    def __init__(self, agent_name: str, event_bus=None):
        self.agent_name = agent_name
        self.event_bus = event_bus
        self.state = {}
        self.subscribed_events = set()
        self.logger = logging.getLogger(f"agent.{agent_name}")
        
    def subscribe_to_event(self, event_type: str):
        """Subscribe to specific event types"""
        self.subscribed_events.add(event_type)
        if self.event_bus:
            self.event_bus.subscribe(event_type, self)
    
    def emit_event(self, event_type: str, target_agent: Optional[str], 
                   user_id: str, payload: Dict[str, Any]) -> str:
        """Emit an event to the message bus"""
        if not self.event_bus:
            self.logger.warning("No event bus configured")
            return ""
            
        event = AgentEvent(
            event_type=event_type,
            source_agent=self.agent_name,
            target_agent=target_agent,
            user_id=user_id,
            payload=payload,
            timestamp=datetime.utcnow(),
            event_id=f"{self.agent_name}_{event_type}_{datetime.utcnow().timestamp()}"
        )
        
        return self.event_bus.emit(event)
    
    @abstractmethod
    def process_event(self, event: AgentEvent) -> Optional[Dict[str, Any]]:
        """
        Process an incoming event and return optional response data.
        Each agent must implement this method.
        """
        pass
    
    def get_state(self, user_id: str) -> Dict[str, Any]:
        """Get agent state for a specific user"""
        return self.state.get(user_id, {})
    
    def update_state(self, user_id: str, state_update: Dict[str, Any]):
        """Update agent state for a specific user"""
        if user_id not in self.state:
            self.state[user_id] = {}
        self.state[user_id].update(state_update)
    
    def clear_state(self, user_id: str):
        """Clear agent state for a specific user"""
        if user_id in self.state:
            del self.state[user_id]
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and supported operations"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """Return agent health status"""
        return {
            'agent_name': self.agent_name,
            'status': 'healthy',
            'subscribed_events': list(self.subscribed_events),
            'active_users': len(self.state),
            'timestamp': datetime.utcnow().isoformat()
        }