"""
API Configuration for Mavericks Platform
Contains all API endpoints, keys, and service configurations
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class APIConfig:
    """Configuration class for all API services used in Mavericks"""
    
    # OpenRouter API (Primary LLM Service)
    OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-oss-20b:free"
    
    # Hugging Face API (NLP Models)
    HUGGINGFACE_API_KEY: str = os.environ.get("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_BASE_URL: str = "https://api-inference.huggingface.co"
    
    # CodeT5 Model Configuration
    CODET5_MODEL: str = "Salesforce/codet5-base"
    DISTILGPT2_MODEL: str = "distilgpt2"
    SENTENCE_TRANSFORMER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    BERT_MODEL: str = "bert-base-uncased"
    
    # OpenAI API (Backup/Alternative)
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Assessment Generation APIs
    CODEX_API_KEY: str = os.environ.get("CODEX_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    # Session Configuration
    SESSION_SECRET: str = os.environ.get("SESSION_SECRET", "mavericks-dev-secret-key-2025")
    
    # Rate Limiting
    API_RATE_LIMIT: int = 60  # requests per minute
    API_TIMEOUT: int = 30  # seconds
    
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
    required = []
    
    if not api_config.OPENROUTER_API_KEY:
        required.append("OPENROUTER_API_KEY")
    if not api_config.HUGGINGFACE_API_KEY:
        required.append("HUGGINGFACE_API_KEY")
    if not api_config.OPENAI_API_KEY:
        required.append("OPENAI_API_KEY")
        
    return required