# API Configuration Guide

## Overview
This folder contains the API configuration system for the Mavericks platform. Instead of using environment variables or secret keys scattered throughout the code, all API configurations are centralized here.

## Files

### `api_keys.py` - Your API Keys Storage
This is where you store your actual API keys. **Important**: Replace the placeholder values with your real API keys.

```python
# Example configuration
OPENROUTER_API_KEY = "sk-or-v1-your-actual-key-here"
HUGGINGFACE_API_KEY = "hf_your-actual-key-here"
OPENAI_API_KEY = "sk-your-actual-key-here"
```

### `api_config.py` - Configuration Management
This file manages all API configurations and provides methods to:
- Check service availability
- Generate proper headers for API requests
- Handle service fallbacks
- Monitor API status

## Quick Setup

1. **Edit `api_keys.py`**:
   - Replace placeholder API keys with your actual keys
   - Keep `DATABASE_URL = ""` (uses Replit's database automatically)
   - Change `SESSION_SECRET` to a secure random string

2. **Get API Keys**:
   - **OpenRouter**: https://openrouter.ai/ (free tier available)
   - **Hugging Face**: https://huggingface.co/ (free tier available)  
   - **OpenAI**: https://platform.openai.com/ (requires billing)

3. **Test Configuration**:
   - Visit `/api-status` in your app to check configuration
   - Use the testing console to verify API connections

## Security Notes

- Never commit real API keys to version control
- Use strong random strings for session secrets
- Keep `api_keys.py` local to your development environment
- In production, use proper secret management services

## Service Priorities

1. **OpenRouter** - Primary AI service (free tier available)
2. **Hugging Face** - NLP models and transformers
3. **OpenAI** - Backup AI service (requires billing)
4. **Local Fallback** - Template-based processing when APIs unavailable

## Troubleshooting

### "API Key Missing" Errors
- Check that `api_keys.py` has been edited with real keys
- Ensure no typos in API key format
- Verify account status on the API provider's website

### Connection Issues
- Test API endpoints using the `/api-status` testing console
- Check API provider status pages for outages
- Verify API key permissions and usage limits

### Database Issues  
- Leave `DATABASE_URL = ""` to use Replit's database automatically
- Only set custom database URL for external PostgreSQL instances

## File Structure
```
config/
├── api_keys.py          # Your API keys (edit this file)
├── api_config.py        # Configuration logic (don't edit)
└── README.md           # This guide
```