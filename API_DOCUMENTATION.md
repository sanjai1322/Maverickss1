# Mavericks Platform API Documentation

## Overview

The Mavericks platform includes 4 main API endpoints that provide real-time data and status monitoring for the AI-powered learning system.

## API Endpoints

### 1. `/api/status` - System Health Monitoring

**Purpose**: Check overall platform health and component status

**Response Example**:
```json
{
  "status": "online",
  "database": "online", 
  "agents": "online",
  "version": "1.0.0",
  "timestamp": "2025-08-09T05:44:19.718394"
}
```

**Why We Use It**:
- Monitor if the Flask server is running properly
- Check database connectivity 
- Verify all 6 AI agents are initialized
- Provide system diagnostics for troubleshooting

### 2. `/api/ai-services/status` - AI Agent System Status

**Purpose**: Monitor the 6 specialized AI agents and their capabilities

**Response Example**:
```json
{
  "status": "online",
  "services": {
    "openrouter": true,
    "huggingface": true, 
    "transformers": true
  },
  "ai_agents": {
    "profile_agent": true,
    "assessment_agent": true,
    "learning_path_agent": true,
    "gamification_agent": true,
    "hackathon_agent": true,
    "analytics_agent": true
  },
  "timestamp": "2025-08-09T05:44:20.431168"
}
```

**Why We Use It**:
- Verify AI agents are running (ProfileAgent, AssessmentAgent, etc.)
- Check external AI service availability (OpenRouter, Hugging Face)
- Monitor machine learning model availability
- Enable fallback logic when AI services are unavailable

### 3. `/api/recent-activities` - User Activity Tracking

**Purpose**: Retrieve recent user activities and progress

**Response Example**:
```json
{
  "activities": [
    {
      "type": "assessment",
      "title": "Completed Assessment - Score: 85%",
      "timestamp": "2025-08-09T05:30:00",
      "score": 85
    },
    {
      "type": "learning", 
      "title": "Learning Module: Python Data Structures",
      "timestamp": "2025-08-09T05:25:00",
      "progress": "In Progress"
    }
  ],
  "total_count": 2
}
```

**Why We Use It**:
- Track user learning progress in real-time
- Display activity feeds in the dashboard
- Monitor engagement and completion rates
- Provide data for analytics and recommendations

### 4. `/api/progress-data` - Comprehensive User Analytics

**Purpose**: Provide detailed user progress and learning analytics

**Response Example**:
```json
{
  "user": {
    "username": "john_doe",
    "skills": "Python, JavaScript, React, Java",
    "total_points": 450,
    "current_level": 3
  },
  "learning_paths": [
    {
      "module_name": "Advanced Python Programming",
      "completion_status": "In Progress", 
      "estimated_time": 120,
      "created_at": "2025-08-09T05:00:00"
    }
  ],
  "assessments": [
    {
      "overall_score": 85,
      "responses_data": "{...}",
      "started_at": "2025-08-09T05:30:00"
    }
  ]
}
```

**Why We Use It**:
- Generate personalized learning recommendations
- Track skill development over time
- Create visual progress charts and analytics
- Support gamification features (points, levels, achievements)

## API Integration Features

### Real-time Status Monitoring
- Continuous health checks every 30 seconds
- Visual status indicators in the user interface
- Automatic fallback when services are unavailable

### Dynamic Assessment System
- Questions generated based on extracted resume skills
- Real-time timer management with auto-save
- Comprehensive scoring with skill-weighted points

### Learning Path Intelligence
- AI-powered curriculum generation
- Progress tracking across multiple modules
- Adaptive difficulty based on performance

### Agent System Communication
- Event-driven architecture with 6 specialized agents
- Asynchronous processing for scalability
- Comprehensive logging and error handling

## Security Features

- Session-based authentication for user-specific data
- Input validation and sanitization
- Error handling with graceful degradation
- CORS configuration for secure API access

## Use Cases

1. **Dashboard Analytics**: Real-time progress visualization
2. **Learning Recommendations**: AI-powered next steps
3. **Assessment Scoring**: Automated evaluation and feedback
4. **Progress Tracking**: Comprehensive learning analytics
5. **System Monitoring**: Health checks and service status
6. **Mobile Integration**: RESTful API for mobile apps

This API architecture enables the platform to provide intelligent, personalized learning experiences while maintaining system reliability and performance.