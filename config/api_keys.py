"""
API Keys Configuration for Mavericks Platform
Store your actual API keys here instead of using environment variables
"""

# =============================================================================
# API KEYS CONFIGURATION
# =============================================================================
# Replace the placeholder values below with your actual API keys

# OpenRouter API (Primary LLM Service for resume analysis and course generation)
OPENROUTER_API_KEY = "your_openrouter_api_key_here"

# Hugging Face API (For NLP models like DistilGPT2, BERT, Sentence Transformers)
HUGGINGFACE_API_KEY = "your_huggingface_api_key_here"

# OpenAI API (Backup LLM service)
OPENAI_API_KEY = "your_openai_api_key_here"

# Codex API (For advanced code generation - optional)
CODEX_API_KEY = "your_codex_api_key_here"

# Session Security (Change this to a random string for production)
SESSION_SECRET = "mavericks-super-secret-key-2025-change-in-production"

# Database URL (Leave empty to use environment variable)
# The system will automatically use the Replit PostgreSQL database
DATABASE_URL = ""

# =============================================================================
# API SERVICE ENDPOINTS
# =============================================================================

# OpenRouter Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-oss-20b:free"  # Free model

# Hugging Face Configuration
HUGGINGFACE_BASE_URL = "https://api-inference.huggingface.co"
HUGGINGFACE_MODELS = {
    "codet5": "Salesforce/codet5-base",
    "distilgpt2": "distilgpt2", 
    "sentence_transformer": "sentence-transformers/all-MiniLM-L6-v2",
    "bert": "bert-base-uncased"
}

# OpenAI Configuration
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-3.5-turbo"

# =============================================================================
# API CONFIGURATION SETTINGS
# =============================================================================

# Rate Limiting
API_RATE_LIMIT = 60  # requests per minute
API_TIMEOUT = 30     # seconds

# Service Headers
API_HEADERS = {
    "openrouter": {
        "Content-Type": "application/json",
        "User-Agent": "Mavericks-Platform/1.0",
        "HTTP-Referer": "https://mavericks-platform.replit.app",
        "X-Title": "Mavericks Coding Platform"
    },
    "huggingface": {
        "Content-Type": "application/json",
        "User-Agent": "Mavericks-Platform/1.0"
    },
    "openai": {
        "Content-Type": "application/json",
        "User-Agent": "Mavericks-Platform/1.0"
    }
}

# =============================================================================
# INSTRUCTIONS FOR SETUP
# =============================================================================
"""
HOW TO GET API KEYS:

1. OpenRouter (Primary AI Service):
   - Go to: https://openrouter.ai/
   - Sign up for a free account
   - Navigate to API Keys section
   - Create a new API key
   - Replace OPENROUTER_API_KEY above

2. Hugging Face (NLP Models):
   - Go to: https://huggingface.co/
   - Create a free account
   - Go to Settings > Access Tokens
   - Create a new token with "Read" permissions
   - Replace HUGGINGFACE_API_KEY above

3. OpenAI (Backup Service):
   - Go to: https://platform.openai.com/
   - Create account and add billing
   - Go to API Keys section
   - Create new API key
   - Replace OPENAI_API_KEY above

4. Database Setup:
   - Update DATABASE_URL with your PostgreSQL connection string
   - Format: postgresql://username:password@host:port/database_name

5. Session Security:
   - Generate a random string for SESSION_SECRET
   - Use: python -c "import secrets; print(secrets.token_hex(32))"
"""

# =============================================================================
# SERVICE AVAILABILITY CHECK
# =============================================================================

def check_api_key_validity():
    """Check which API keys are configured"""
    services = {
        "OpenRouter": OPENROUTER_API_KEY != "your_openrouter_api_key_here" and OPENROUTER_API_KEY.strip() != "",
        "Hugging Face": HUGGINGFACE_API_KEY != "your_huggingface_api_key_here" and HUGGINGFACE_API_KEY.strip() != "",
        "OpenAI": OPENAI_API_KEY != "your_openai_api_key_here" and OPENAI_API_KEY.strip() != "",
        "Codex": CODEX_API_KEY != "your_codex_api_key_here" and CODEX_API_KEY.strip() != ""
    }
    
    return services

def get_configured_services():
    """Get list of properly configured services"""
    validity = check_api_key_validity()
    return [service for service, is_valid in validity.items() if is_valid]

def get_missing_services():
    """Get list of services that need API key configuration"""
    validity = check_api_key_validity()
    return [service for service, is_valid in validity.items() if not is_valid]