# Overview

The Skill Assessment Platform "Mavericks" is an AI-powered web application that analyzes resumes and conducts technical skill assessments. The system extracts technical skills from resume text using AI and provides interactive assessments to evaluate candidates' technical capabilities. Now featuring AI-powered tailored course recommendations with real-time progress tracking, built with Flask and PostgreSQL for comprehensive skill development and monitoring.

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
- **Web Framework**: Flask with CORS enabled for API compatibility
- **AI Integration**: Hugging Face transformers for NLP tasks including skill extraction and text generation
- **Session Management**: Flask sessions with configurable secret key for user state
- **Request Processing**: Form-based data submission with flash messaging for user feedback

## Database Design
- **Storage**: PostgreSQL database with comprehensive user management and course tracking
- **User Management Schema**: 
  - Users: Store username, extracted skills, assessment scores, resume text, and timestamps
  - TailoredCourse: AI-generated courses with completion tracking
  - CourseModule: Individual learning modules within courses
  - ProgressTracking: Real-time activity and progress monitoring
  - LearningPath: Traditional learning path modules
  - Hackathon: Challenge submissions and scoring
- **Admin Management Schema**:
  - AdminUser: Administrator accounts with authentication
  - UserActivity: Detailed user activity logs for analytics
  - UserReport: Generated reports for users and administrators
  - SystemAnalytics: Platform-wide metrics and performance data
  - Achievement: User badges and achievement tracking system
- **Data Format**: Skills and course data stored as JSON strings for flexible structure
- **Connection Management**: SQLAlchemy ORM with connection pooling and pre-ping for reliability

## AI/ML Components
- **Resume Analysis**: OpenRouter API (openai/gpt-oss-20b:free) for advanced resume parsing and skill extraction
- **Course Generation**: AI-powered creation of personalized learning paths based on skill gaps
- **Progress Analytics**: Real-time AI feedback and adaptive recommendations
- **Assessment Scoring**: Automated evaluation of assessment responses
- **Fallback Systems**: Local processing when AI services are unavailable
- **Performance**: Efficient API integration with error handling and fallback mechanisms

## Application Flow
- **Onboarding**: Interactive guided tour for new users explaining platform features
- **Profile Creation**: Users submit username and resume text for AI analysis
- **Skill Extraction**: AI models process resume content to identify technical skills
- **Assessment**: Multi-question technical evaluation with open-ended responses
- **Assessment Panel**: AI-powered coding exercise generation with upload/connect capabilities
- **AI Course Generation**: Personalized learning paths created based on resume analysis
- **Real-time Progress Tracking**: Monitor learning activities and course completion with detailed timestamps
- **Progress Dashboard**: Enhanced timeline showing each step completion with hover details
- **Manual Overrides**: User-accessible buttons for Re-assess, Update Profile, and Request Review
- **Admin Management**: Complete admin dashboard for user oversight and analytics
- **Gen AI Documentation**: Comprehensive overview of all AI technologies and models used
- **Data Persistence**: All user data and results stored in PostgreSQL for session continuity

## Recent Changes (2025-08-08)
- **Assessment Navigation Fixed**: Removed duplicate assessment links from header navigation
- **Assessment Panel Rebuilt**: Created simplified, working assessment panel with proper form inputs
- **Admin Dashboard Fixed**: Resolved template errors and missing metrics data
- **API Integration Verified**: All backend endpoints tested and working (generate_exercise, submit_exercise, get_exercise_hint)
- **Form Input Issues Resolved**: Fixed JavaScript template errors and form field mapping
- **Session Management**: Improved user authentication and session handling

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