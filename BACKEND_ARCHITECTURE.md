# Backend Architecture - Mavericks Platform

## Overview

The Mavericks platform backend is built with Flask and PostgreSQL, featuring a comprehensive agent-based architecture for intelligent skill assessment and learning path generation.

## Core Architecture Components

### 1. Application Entry Point (`app.py`)
- **Flask Application Setup**: Core Flask app with PostgreSQL integration
- **Database Configuration**: SQLAlchemy ORM with connection pooling
- **Agent System Initialization**: Bootstraps 6 specialized AI agents
- **Route Registration**: Imports all route handlers and API endpoints
- **Security Configuration**: Session management and middleware setup

### 2. Database Layer (`backend/database.py`)
```python
# Core Models:
- User: Central user model with skills, progress, and agent data
- LearningPath: Personalized learning modules and progress tracking  
- AssessmentAttempt: Quiz results and performance analytics
- Hackathon: Competition submissions and evaluation data
- UserAchievement: Gamification badges and achievements
- PlatformEvent: Agent system event logging and analytics
```

### 3. Route Handlers (`backend/route_handlers.py`)
- **Core Routes**: Homepage, profile creation, assessment processing
- **Learning System**: Path generation, progress tracking, course recommendations
- **Hackathon Management**: Challenge submission, competition scoring
- **API Endpoints**: RESTful services for external integration
- **Admin Interface**: User management, analytics dashboard

### 4. Business Logic (`backend/services.py`)
- **File Processing**: PDF/Word resume text extraction
- **Skill Analysis**: Keyword-based skill extraction from resumes
- **Assessment Scoring**: Automated quiz evaluation algorithms
- **Learning Path Generation**: AI-powered curriculum creation
- **Progress Analytics**: Learning outcome analysis and recommendations

### 5. Agent Integration (`backend/agent_integration.py`)
- **Agent Manager**: Lifecycle management for 6 specialized agents
- **Event Bus**: Asynchronous inter-agent communication
- **API Endpoints**: External access to agent functionality
- **Health Monitoring**: Agent status and performance tracking
- **Error Handling**: Graceful degradation when agents unavailable

## AI Agent System

### 6 Specialized Agents:

1. **ProfileAgent**: Resume analysis and skill extraction using NLP
2. **AssessmentAgent**: Automated exercise generation and solution evaluation  
3. **LearningPathAgent**: Personalized curriculum creation based on skill gaps
4. **GamificationAgent**: Points, badges, achievements, and engagement mechanics
5. **HackathonAgent**: Coding competition management with automated scoring
6. **AnalyticsAgent**: Platform analytics, user behavior insights, and predictions

### Event-Driven Communication:
```python
# Event Examples:
- user.registered → ProfileAgent processes resume
- skills.extracted → AssessmentAgent generates quiz
- assessment.completed → LearningPathAgent creates curriculum
- hackathon.submission_made → GamificationAgent awards points
```

## React Integration Layer

### Frontend Architecture:
- **React Components**: Modern JavaScript components for interactive features
- **Timer System**: Real-time assessment timers with auto-save functionality
- **Dynamic Quizzes**: Skill-based question generation from resume analysis
- **Progress Tracking**: Visual progress indicators and analytics charts
- **State Management**: Local storage for session persistence

### React-Compatible Features:
- **Assessment Quiz Component**: Timer-based skill assessment with auto-submission
- **Learning Path Tracker**: Dynamic progress visualization
- **Skill Display Component**: Resume skill tag visualization
- **Hackathon Dashboard**: Competition management interface

## Data Flow Architecture

### User Journey with Agents:
1. **Profile Creation**: User uploads resume → ProfileAgent extracts skills
2. **Skill Processing**: Skills stored → AssessmentAgent generates personalized quiz
3. **Assessment**: User takes quiz → GamificationAgent awards points
4. **Learning Path**: Assessment results → LearningPathAgent creates curriculum
5. **Progress Tracking**: All activities → AnalyticsAgent provides insights
6. **Hackathon Participation**: Competitions → HackathonAgent manages scoring

### Database Relationships:
```
User (1) → (many) LearningPath
User (1) → (many) AssessmentAttempt  
User (1) → (many) Hackathon
User (1) → (many) UserAchievement
User (1) → (many) PlatformEvent
```

## API Architecture

### RESTful Endpoints:
- `/api/agents/status` - Agent system health check
- `/api/agents/profile/<username>` - User profile data  
- `/api/agents/assessment/<username>` - Assessment results
- `/api/agents/learning_path/<username>` - Learning curriculum
- `/api/agents/analytics/<username>` - User analytics
- `/api/agents/gamification/<username>` - Points and achievements

### Dynamic Assessment API:
- Skill-based question generation
- Real-time timer management
- Auto-save functionality
- Comprehensive scoring system

## Security & Performance

### Security Features:
- Session-based authentication
- File upload validation and sanitization
- SQL injection prevention via ORM
- CORS configuration for API access

### Performance Optimizations:
- Database connection pooling
- Event-driven agent processing
- Client-side state caching
- Efficient skill extraction algorithms

## Development Workflow

### Key Files for Development:
1. `app.py` - Main application configuration
2. `backend/route_handlers.py` - Add new routes and endpoints
3. `backend/services.py` - Implement business logic
4. `backend/database.py` - Define new database models
5. `static/js/react-components.js` - Add React functionality
6. `static/js/assessment-timer.js` - Timer and quiz management

### Agent System Extension:
- Agents communicate via EventBus
- Add new event types in `agents/event_bus.py`
- Implement agent logic in `agents/` directory
- Register events in `backend/agent_integration.py`

This architecture provides a scalable, intelligent platform for skill assessment and personalized learning with full React compatibility and comprehensive agent-based automation.