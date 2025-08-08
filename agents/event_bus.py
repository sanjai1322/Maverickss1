"""
Event Bus - Central Message Hub
===============================

Manages communication between all agents in the Mavericks platform.
Provides event routing, persistence, and delivery guarantees.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from collections import defaultdict, deque
from threading import Lock, Thread
import time
import uuid

from .base_agent import AgentEvent

logger = logging.getLogger(__name__)

class EventBus:
    """
    Central message bus for agent communication.
    
    Features:
    - Event routing and delivery
    - Event persistence and replay
    - Dead letter queue for failed deliveries
    - Event analytics and monitoring
    """
    
    def __init__(self, max_event_history: int = 10000):
        self.subscribers = defaultdict(list)  # event_type -> [agents]
        self.event_history = deque(maxlen=max_event_history)
        self.failed_events = deque(maxlen=1000)  # Dead letter queue
        self.delivery_stats = defaultdict(int)
        self.lock = Lock()
        self.running = True
        
        # Start background cleanup thread
        self.cleanup_thread = Thread(target=self._cleanup_old_events, daemon=True)
        self.cleanup_thread.start()
        
    def subscribe(self, event_type: str, agent) -> bool:
        """Subscribe an agent to specific event types"""
        with self.lock:
            if agent not in self.subscribers[event_type]:
                self.subscribers[event_type].append(agent)
                logger.info(f"Agent {agent.agent_name} subscribed to {event_type}")
                return True
            return False
    
    def unsubscribe(self, event_type: str, agent) -> bool:
        """Unsubscribe an agent from event types"""
        with self.lock:
            if agent in self.subscribers[event_type]:
                self.subscribers[event_type].remove(agent)
                logger.info(f"Agent {agent.agent_name} unsubscribed from {event_type}")
                return True
            return False
    
    def emit(self, event: AgentEvent) -> str:
        """
        Emit an event to all subscribed agents.
        Returns the event ID for tracking.
        """
        try:
            with self.lock:
                # Store event in history
                self.event_history.append(event)
                
                # Get subscribers for this event type
                subscribers = self.subscribers.get(event.event_type, [])
                
                # If target_agent is specified, filter subscribers
                if event.target_agent:
                    subscribers = [agent for agent in subscribers 
                                 if agent.agent_name == event.target_agent]
                
                logger.info(f"Emitting event {event.event_type} from {event.source_agent} "
                           f"to {len(subscribers)} subscribers")
                
                # Deliver to each subscriber
                for agent in subscribers:
                    try:
                        result = agent.process_event(event)
                        self.delivery_stats[f"{agent.agent_name}_success"] += 1
                        
                        if result:
                            logger.debug(f"Agent {agent.agent_name} processed event "
                                       f"{event.event_id} with result: {result}")
                            
                    except Exception as e:
                        logger.error(f"Failed to deliver event {event.event_id} "
                                   f"to agent {agent.agent_name}: {str(e)}")
                        
                        # Add to dead letter queue
                        self.failed_events.append({
                            'event': event,
                            'target_agent': agent.agent_name,
                            'error': str(e),
                            'timestamp': datetime.utcnow()
                        })
                        self.delivery_stats[f"{agent.agent_name}_failed"] += 1
                
                return event.event_id
                
        except Exception as e:
            logger.error(f"Failed to emit event {event.event_type}: {str(e)}")
            return ""
    
    def get_events_for_user(self, user_id: str, 
                           event_types: Optional[List[str]] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events for a specific user"""
        with self.lock:
            events = []
            for event in reversed(self.event_history):
                if event.user_id == user_id:
                    if not event_types or event.event_type in event_types:
                        events.append(event.to_dict())
                        if len(events) >= limit:
                            break
            return events
    
    def get_event_analytics(self) -> Dict[str, Any]:
        """Get event bus analytics and statistics"""
        with self.lock:
            event_type_counts = defaultdict(int)
            user_activity = defaultdict(int)
            
            for event in self.event_history:
                event_type_counts[event.event_type] += 1
                user_activity[event.user_id] += 1
            
            return {
                'total_events': len(self.event_history),
                'failed_events': len(self.failed_events),
                'event_types': dict(event_type_counts),
                'user_activity': dict(user_activity),
                'delivery_stats': dict(self.delivery_stats),
                'subscribers': {
                    event_type: len(agents) 
                    for event_type, agents in self.subscribers.items()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def replay_events_for_user(self, user_id: str, agent,
                              event_types: Optional[List[str]] = None) -> int:
        """Replay historical events for a user to an agent"""
        with self.lock:
            replayed = 0
            for event in self.event_history:
                if event.user_id == user_id:
                    if not event_types or event.event_type in event_types:
                        try:
                            agent.process_event(event)
                            replayed += 1
                        except Exception as e:
                            logger.error(f"Failed to replay event {event.event_id}: {str(e)}")
            
            logger.info(f"Replayed {replayed} events for user {user_id} to agent {agent.agent_name}")
            return replayed
    
    def clear_user_events(self, user_id: str) -> int:
        """Clear all events for a specific user (GDPR compliance)"""
        with self.lock:
            original_count = len(self.event_history)
            self.event_history = deque(
                [event for event in self.event_history if event.user_id != user_id],
                maxlen=self.event_history.maxlen
            )
            removed = original_count - len(self.event_history)
            
            # Also clear from failed events
            self.failed_events = deque(
                [failed for failed in self.failed_events 
                 if failed['event'].user_id != user_id],
                maxlen=self.failed_events.maxlen
            )
            
            logger.info(f"Cleared {removed} events for user {user_id}")
            return removed
    
    def _cleanup_old_events(self):
        """Background thread to cleanup old events and failed deliveries"""
        while self.running:
            try:
                time.sleep(3600)  # Run every hour
                
                # Clean up old failed events (older than 24 hours)
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                with self.lock:
                    original_failed = len(self.failed_events)
                    self.failed_events = deque(
                        [failed for failed in self.failed_events 
                         if failed['timestamp'] > cutoff_time],
                        maxlen=self.failed_events.maxlen
                    )
                    
                    cleaned = original_failed - len(self.failed_events)
                    if cleaned > 0:
                        logger.info(f"Cleaned up {cleaned} old failed events")
                        
            except Exception as e:
                logger.error(f"Error in event cleanup: {str(e)}")
    
    def shutdown(self):
        """Shutdown the event bus and cleanup resources"""
        self.running = False
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        logger.info("Event bus shutdown complete")