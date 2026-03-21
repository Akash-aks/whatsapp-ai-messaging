"""
Configuration module for WhatsApp AI Automation
UPDATED: Now includes Ollama (offline) and Google Gemini (free) support
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration settings"""
    
    # Application Info
    APP_NAME = "WhatsApp AI Message Automation"
    APP_VERSION = "1.0.0"
    
    # Directory Paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    
    # Create directories if they don't exist
    LOGS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    
    # AI Model Configuration
    AI_MODELS = {
        # FREE MODELS (No API key needed)
        "Llama 3.2 (Offline - Free)": {
            "provider": "ollama",
            "model": "llama3.2",
            "max_tokens": 500,
            "description": "Fast, runs on your computer, no internet needed"
        },
        "Mistral (Offline - Free)": {
            "provider": "ollama",
            "model": "mistral",
            "max_tokens": 500,
            "description": "Better quality, runs offline, 4GB model"
        },
        "Gemini Pro (Online - Free)": {
            "provider": "google",
            "model": "gemini-2.5-flash",
            "max_tokens": 500,
            "description": "Google's AI, free tier, good quality"
        },
        
        # PREMIUM MODELS (API key required, but free credits available)
        "Claude Sonnet 4": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500,
            "description": "Best quality, requires API key"
        },
        "Claude Haiku 4": {
            "provider": "anthropic",
            "model": "claude-haiku-4-20250101",
            "max_tokens": 500,
            "description": "Fast & affordable, requires API key"
        },
        "GPT-4": {
            "provider": "openai",
            "model": "gpt-4-turbo-preview",
            "max_tokens": 500,
            "description": "OpenAI's best, requires API key"
        },
        "GPT-3.5": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "max_tokens": 500,
            "description": "Fast OpenAI model, requires API key"
        }
    }
    
    # API Keys (from environment variables)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  # NEW!
    
    # Ollama Configuration (for offline models)
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")  # NEW!
    
    # WhatsApp Automation Settings
    WHATSAPP_WEB_URL = "https://web.whatsapp.com"
    MESSAGE_DELAY_MIN = 5  # Minimum seconds between messages
    MESSAGE_DELAY_MAX = 10  # Maximum seconds between messages
    BROWSER_WAIT_TIMEOUT = 30  # Seconds to wait for elements
    
    # Excel Settings
    SUPPORTED_EXCEL_FORMATS = [".xlsx", ".xls"]
    MAX_CONTACTS = 1000  # Maximum contacts per batch
    
    # GUI Settings
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 700
    PREVIEW_WINDOW_WIDTH = 800
    PREVIEW_WINDOW_HEIGHT = 600
    
    # Logging Settings
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE = LOGS_DIR / "app.log"
    LOG_LEVEL = "INFO"
    
    # Default Prompts
    DEFAULT_AI_PROMPT = """You are a professional message writer. Improve the following message to make it more engaging, 
professional, and personalized. Keep the core meaning but enhance the tone and structure. 
Make it concise and impactful. The message is: {message}"""
    
    @classmethod
    def validate_api_keys(cls):
        """Validate that required API keys are present"""
        issues = []
        
        # Check if ANY AI option is available
        has_anthropic = bool(cls.ANTHROPIC_API_KEY)
        has_openai = bool(cls.OPENAI_API_KEY)
        has_google = bool(cls.GOOGLE_API_KEY)
        has_ollama = cls._check_ollama_available()
        
        if not (has_anthropic or has_openai or has_google or has_ollama):
            issues.append(
                "No AI services available!\n\n"
                "FREE OPTIONS:\n"
                "• Install Ollama for offline AI (https://ollama.com/download)\n"
                "• Get Google Gemini API key (https://makersuite.google.com/app/apikey)\n\n"
                "PAID OPTIONS:\n"
                "• Set ANTHROPIC_API_KEY in .env file\n"
                "• Set OPENAI_API_KEY in .env file"
            )
        
        return issues
    
    @classmethod
    def _check_ollama_available(cls):
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_HOST}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @classmethod
    def get_available_models(cls):
        """Get list of available AI models based on configured services"""
        available = []
        
        # Check Ollama (offline, free)
        if cls._check_ollama_available():
            available.extend([
                "Llama 3.2 (Offline - Free)",
                "Mistral (Offline - Free)"
            ])
        
        # Check Google Gemini (online, free)
        if cls.GOOGLE_API_KEY:
            available.append("Gemini Pro (Online - Free)")
        
        # Check Anthropic (paid)
        if cls.ANTHROPIC_API_KEY:
            available.extend([
                "Claude Sonnet 4",
                "Claude Haiku 4"
            ])
        
        # Check OpenAI (paid)
        if cls.OPENAI_API_KEY:
            available.extend([
                "GPT-4",
                "GPT-3.5"
            ])
        
        # If nothing available, show all (with warnings)
        if not available:
            available = [
                "Llama 3.2 (Offline - Free)",
                "Gemini Pro (Online - Free)",
                "Claude Haiku 4"
            ]
        
        return available
    
    @classmethod
    def get_model_info(cls, model_name):
        """Get detailed info about a model"""
        model_config = cls.AI_MODELS.get(model_name)
        if model_config:
            return {
                'provider': model_config['provider'],
                'description': model_config.get('description', ''),
                'is_free': model_config['provider'] in ['ollama', 'google'],
                'needs_api_key': model_config['provider'] in ['anthropic', 'openai']
            }
        return None