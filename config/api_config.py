"""
API Configuration for Mavericks Platform
Contains all API endpoints, keys, and service configurations
Uses config/api_keys.py for actual API key storage
"""

from dataclasses import dataclass
from typing import Dict, Optional

# Import API keys from local file instead of environment variables
try:
    from config.api_keys import *
except ImportError:
    # Fallback to environment variables if api_keys.py doesn't exist
    import os
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY", "")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    CODEX_API_KEY = os.environ.get("CODEX_API_KEY", "")
    SESSION_SECRET = os.environ.get("SESSION_SECRET", "mavericks-dev-secret-key-2025")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    
    # Default configurations
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = "openai/gpt-oss-20b:free"
    HUGGINGFACE_BASE_URL = "https://api-inference.huggingface.co"
    OPENAI_BASE_URL = "https://api.openai.com/v1" 
    OPENAI_MODEL = "gpt-3.5-turbo"
    API_RATE_LIMIT = 60
    API_TIMEOUT = 30

@dataclass
class APIConfig:
    """Configuration class for all API services used in Mavericks"""
    
    # API Keys from api_keys.py file
    OPENROUTER_API_KEY: str = OPENROUTER_API_KEY
    OPENROUTER_BASE_URL: str = OPENROUTER_BASE_URL
    OPENROUTER_MODEL: str = OPENROUTER_MODEL
    
    HUGGINGFACE_API_KEY: str = HUGGINGFACE_API_KEY
    HUGGINGFACE_BASE_URL: str = HUGGINGFACE_BASE_URL
    
    OPENAI_API_KEY: str = OPENAI_API_KEY
    OPENAI_BASE_URL: str = OPENAI_BASE_URL
    OPENAI_MODEL: str = OPENAI_MODEL
    
    CODEX_API_KEY: str = CODEX_API_KEY
    
    # Configuration from api_keys.py
    DATABASE_URL: str = DATABASE_URL
    SESSION_SECRET: str = SESSION_SECRET
    
    # Rate Limiting
    API_RATE_LIMIT: int = API_RATE_LIMIT  # requests per minute
    API_TIMEOUT: int = API_TIMEOUT  # seconds
    
    def get_headers(self, service: str) -> Dict[str, str]:
        """Get headers for specific API service"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mavericks-Platform/1.0"
        }
        
        if service == "openrouter":
            headers["Authorization"] = f"Bearer {self.OPENROUTER_API_KEY}"
            headers["HTTP-Referer"] = "https://mavericks-platform.replit.app"
            headers["X-Title"] = "Mavericks Coding Platform"
            
        elif service == "huggingface":
            headers["Authorization"] = f"Bearer {self.HUGGINGFACE_API_KEY}"
            
        elif service == "openai":
            headers["Authorization"] = f"Bearer {self.OPENAI_API_KEY}"
            
        return headers
    
    def is_service_available(self, service: str) -> bool:
        """Check if API service is configured and available"""
        service_keys = {
            "openrouter": self.OPENROUTER_API_KEY,
            "huggingface": self.HUGGINGFACE_API_KEY,
            "openai": self.OPENAI_API_KEY,
            "codex": self.CODEX_API_KEY
        }
        
        return bool(service_keys.get(service))
    
    def get_primary_llm_config(self) -> Dict[str, str]:
        """Get primary LLM configuration based on available services"""
        if self.is_service_available("openrouter"):
            return {
                "service": "openrouter",
                "base_url": self.OPENROUTER_BASE_URL,
                "model": self.OPENROUTER_MODEL,
                "api_key": self.OPENROUTER_API_KEY
            }
        elif self.is_service_available("openai"):
            return {
                "service": "openai", 
                "base_url": self.OPENAI_BASE_URL,
                "model": self.OPENAI_MODEL,
                "api_key": self.OPENAI_API_KEY
            }
        else:
            return {
                "service": "fallback",
                "base_url": "",
                "model": "local",
                "api_key": ""
            }

# Global API configuration instance
api_config = APIConfig()

# API Service Status
API_SERVICES = {
    "OpenRouter": {
        "description": "Primary LLM service for resume analysis and course generation",
        "model": "openai/gpt-oss-20b:free",
        "status": "configured" if api_config.is_service_available("openrouter") else "needs_key",
        "features": ["Resume Analysis", "Course Generation", "Assessment Creation"]
    },
    "Hugging Face": {
        "description": "NLP models for text processing and embeddings",
        "model": "Multiple models (DistilGPT2, BERT, Sentence Transformers)",
        "status": "configured" if api_config.is_service_available("huggingface") else "needs_key", 
        "features": ["Skill Extraction", "Text Classification", "Embeddings"]
    },
    "OpenAI": {
        "description": "Backup LLM service",
        "model": "gpt-3.5-turbo",
        "status": "configured" if api_config.is_service_available("openai") else "needs_key",
        "features": ["Text Generation", "Code Analysis", "Question Generation"]
    },
    "Local Models": {
        "description": "Fallback local processing",
        "model": "Rule-based + Local NLP",
        "status": "always_available",
        "features": ["Basic Skill Extraction", "Template-based Courses"]
    }
}

def get_required_api_keys():
    """Return list of API keys that need to be configured"""
    try:
        from config.api_keys import get_missing_services
        return get_missing_services()
    except ImportError:
        # Fallback method
        required = []
        if not api_config.OPENROUTER_API_KEY:
            required.append("OPENROUTER_API_KEY")
        if not api_config.HUGGINGFACE_API_KEY:
            required.append("HUGGINGFACE_API_KEY")
        if not api_config.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY")
        return required