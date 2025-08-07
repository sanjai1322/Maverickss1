# Overview

The Skill Assessment Platform is an AI-powered web application that analyzes resumes and conducts technical skill assessments. The system extracts technical skills from resume text using natural language processing and provides interactive assessments to evaluate candidates' technical capabilities. Built with Flask and utilizing Hugging Face transformers, the platform offers a complete solution for skill evaluation and progress tracking.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme for responsive UI
- **Static Assets**: Vanilla JavaScript for interactivity, Font Awesome icons for visual elements
- **Navigation**: Multi-page application with profile creation, assessment taking, and progress tracking
- **Form Handling**: Client-side validation with auto-save functionality and character counters

## Backend Architecture
- **Web Framework**: Flask with CORS enabled for API compatibility
- **AI Integration**: Hugging Face transformers for NLP tasks including skill extraction and text generation
- **Session Management**: Flask sessions with configurable secret key for user state
- **Request Processing**: Form-based data submission with flash messaging for user feedback

## Database Design
- **Storage**: SQLite database with single users table
- **Schema**: Users store username, extracted skills (JSON string), assessment scores (JSON string), resume text, and timestamps
- **Data Format**: Skills and scores stored as JSON strings for flexible data structure
- **Connection Management**: Context-based database connections with row factory for easier data access

## AI/ML Components
- **Text Analysis**: Transformer models for resume parsing and skill extraction
- **Assessment Scoring**: Automated evaluation of assessment responses
- **Model Loading**: Pre-trained models from Hugging Face including sentence transformers and text generation models
- **Performance**: Models loaded at application startup for faster response times

## Application Flow
- **Profile Creation**: Users submit username and resume text for AI analysis
- **Skill Extraction**: NLP models process resume content to identify technical skills
- **Assessment**: Multi-question technical evaluation with open-ended responses
- **Progress Tracking**: Dashboard displaying extracted skills and assessment scores
- **Data Persistence**: All user data and results stored in SQLite for session continuity

# External Dependencies

## AI/ML Services
- **Hugging Face Transformers**: Core NLP library for text processing and skill extraction
- **Sentence Transformers**: Specifically "all-MiniLM-L6-v2" model for text embeddings
- **DistilGPT2**: Text generation model for assessment processing
- **NumPy**: Numerical computing support for AI model operations

## Web Framework Dependencies
- **Flask**: Primary web framework with Jinja2 templating
- **Flask-CORS**: Cross-origin resource sharing for API endpoints
- **Werkzeug**: WSGI utilities including ProxyFix middleware

## Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant
- **Font Awesome 6**: Icon library for UI elements
- **Vanilla JavaScript**: Client-side interactivity without additional frameworks

## Database
- **SQLite**: Embedded database for user data and assessment results
- **Built-in Python sqlite3**: Database connectivity and operations

## Development Tools
- **Python Logging**: Application monitoring and debugging
- **Environment Variables**: Configuration management for secrets and settings