# Overview

The Skill Assessment Platform "Mavericks" is a comprehensive agent-based coding platform that automates coding skill assessment, provides personalized learning paths, facilitates engaging hackathons, and offers full visibility into user progress. The platform uses a decomposed agent architecture with a central message bus, gamification features including leaderboards, and AI-powered agents for profile analysis, assessment generation, and learning path recommendations. Built with Flask and PostgreSQL for scalable, enterprise-ready skill development and monitoring.

# User Preferences

Preferred communication style: Simple, everyday language.
UI Design: Clean, professional interface with Poppins font and subtle animations.
Branding: "Mavericks" with rocket theme and blue gradient color scheme.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme for responsive UI
- **Static Assets**: Vanilla JavaScript for interactivity, Font Awesome icons for visual elements
- **Navigation**: Multi-page application with profile creation, assessment taking, and progress tracking
- **Form Handling**: Client-side validation with auto-save functionality and character counters
- **Onboarding System**: Interactive guided tour with tooltip overlays and step-by-step navigation

## Backend Architecture
- **Web Framework**: Flask with CORS enabled for API compatibility and comprehensive agent API endpoints
- **Agent System**: Event-driven architecture with 6 specialized agents communicating through central EventBus
  - **ProfileAgent**: Resume analysis and skill extraction using AI/NLP
  - **AssessmentAgent**: Automated exercise generation and solution evaluation
  - **GamificationAgent**: Points, badges, achievements, and leaderboard management
  - **LearningPathAgent**: Personalized curriculum generation and progress tracking
  - **HackathonAgent**: Coding competition management with automated scoring
  - **AnalyticsAgent**: Comprehensive platform analytics and user behavior insights
- **Event Bus**: Asynchronous message passing with event history and analytics
- **Session Management**: Flask sessions with configurable secret key for user state
- **Request Processing**: Form-based data submission with flash messaging and agent integration

## Database Design
- **Storage**: PostgreSQL database with comprehensive agent-based user management and tracking
- **Core Schema**: 
  - **Users**: Enhanced with agent system fields (profile, gamification, learning, analytics data)
  - **AssessmentAttempt**: Detailed assessment tracking with skill breakdown and performance metrics
  - **UserAchievement**: Badge and achievement system with criteria tracking
  - **LearningModule**: Individual learning modules within paths with progress tracking
  - **Hackathon**: Enhanced hackathon submissions with team management and evaluation data
  - **PlatformEvent**: Complete event tracking for agent system analytics
- **Legacy Schema**:
  - TailoredCourse: AI-generated courses with completion tracking
  - CourseModule: Individual learning modules within courses
  - ProgressTracking: Real-time activity and progress monitoring
  - LearningPath: Traditional learning path modules
- **Admin Management Schema**:
  - AdminUser: Administrator accounts with authentication
  - UserActivity: Detailed user activity logs for analytics
  - UserReport: Generated reports for users and administrators
  - SystemAnalytics: Platform-wide metrics and performance data
- **Data Format**: Agent data stored as JSON strings with structured event payloads
- **Connection Management**: SQLAlchemy ORM with connection pooling and pre-ping for reliability

## AI/ML Components
- **Agent-Based AI Integration**: Each agent incorporates AI capabilities for specialized tasks
  - **ProfileAgent**: OpenRouter API and Hugging Face transformers for resume analysis and skill extraction
  - **AssessmentAgent**: AI-powered exercise generation with automated solution evaluation
  - **LearningPathAgent**: Intelligent curriculum creation based on skill gaps and learning patterns
  - **GamificationAgent**: Smart engagement mechanics with adaptive difficulty and reward systems
  - **HackathonAgent**: Automated challenge generation and performance evaluation
  - **AnalyticsAgent**: Predictive insights and trend analysis for user behavior
- **Event-Driven AI Processing**: Agents respond to events with contextual AI analysis
- **Fallback Systems**: Local processing when AI services are unavailable with graceful degradation
- **Performance**: Efficient API integration with error handling and comprehensive logging

## Application Flow
- **Agent-Driven User Journey**: Every user action triggers agent processing for intelligent responses
- **Profile Creation**: Users submit username and resume → ProfileAgent processes via EventBus
- **Skill Extraction**: ProfileAgent analyzes resume content and emits skill data for other agents
- **Gamification Initialization**: GamificationAgent creates user profile with initial points and achievements
- **Assessment Generation**: AssessmentAgent creates personalized coding challenges based on extracted skills
- **Learning Path Creation**: LearningPathAgent generates customized curricula from assessment results
- **Progress Tracking**: AnalyticsAgent monitors all user activities and generates insights
- **Hackathon Participation**: HackathonAgent manages competitions with automated scoring and ranking
- **Real-time Analytics**: All agents contribute data for comprehensive user analytics dashboard
- **Event-Based Communication**: Agents communicate asynchronously through EventBus for scalable processing
- **API Integration**: Comprehensive agent API endpoints for external integration and monitoring
- **Data Persistence**: Agent state and event history stored in PostgreSQL for reliability and analysis

## Recent Changes (2025-08-09)
- **Backend Modularization**: Complete reorganization of backend code into separate modular files:
  - backend/database.py: All database models with comprehensive documentation
  - backend/route_handlers.py: All Flask routes with detailed explanations
  - backend/services.py: Business logic and utility functions
  - backend/admin_models.py: Administrative models and tracking
  - backend/agent_integration.py: Agent system integration layer
- **Code Documentation**: Added extensive comments explaining each component's purpose and functionality
- **Import Structure Cleanup**: Resolved circular import issues and simplified file dependencies
- **Route Completion**: Added all missing routes (admin dashboard, user management, API endpoints)
- **Security Improvements**: Proper client/server separation and robust error handling
- **Deployment Ready**: Application successfully migrated to Replit environment and running properly

## Previous Changes (2025-08-08)
- **Complete Agent System Architecture**: Built comprehensive 6-agent system with EventBus communication
- **Database Schema Enhancement**: Extended models with agent-specific fields and comprehensive tracking
- **API Integration**: Added 15+ agent API endpoints for external integration and monitoring
- **Event-Driven Architecture**: Implemented asynchronous agent communication with event history
- **Real-time Processing**: All user actions processed through agent system for intelligent responses
- **Scalable Design**: Event-driven architecture supports horizontal scaling and microservices transition

# External Dependencies

## API Configuration System
- **Centralized Config**: `config/api_keys.py` stores all API keys instead of environment variables
- **Service Management**: `config/api_config.py` handles service availability, headers, and fallbacks
- **Status Monitoring**: Real-time API service monitoring and testing console
- **Documentation**: Complete setup guide in `config/README.md`

## AI/ML Services
- **OpenRouter GPT**: Primary LLM service using `openai/gpt-oss-20b:free` model
- **Hugging Face Transformers**: Core NLP library for text processing and skill extraction
- **Sentence Transformers**: Specifically "all-MiniLM-L6-v2" model for text embeddings
- **DistilGPT2**: Text generation model for assessment processing
- **OpenAI GPT-3.5**: Backup LLM service for additional AI capabilities

## Web Framework Dependencies
- **Flask**: Primary web framework with Jinja2 templating
- **Flask-CORS**: Cross-origin resource sharing for API endpoints
- **Werkzeug**: WSGI utilities including ProxyFix middleware

## Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant
- **Font Awesome 6**: Icon library for UI elements
- **Vanilla JavaScript**: Client-side interactivity without additional frameworks

## Database
- **PostgreSQL**: Production-grade database with comprehensive user management and course tracking
- **SQLAlchemy ORM**: Database connectivity with connection pooling and pre-ping for reliability
- **Environment Variables**: Secure database connection using DATABASE_URL

## Development Tools
- **Python Logging**: Application monitoring and debugging
- **Environment Variables**: Configuration management for secrets and settings