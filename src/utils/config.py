"""Configuration module for WhatsApp AI Automation
Supported free providers: Google Gemini, Groq, Ollama
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ===== PYINSTALLER COMPATIBILITY FIX =====
# Detect if running as .exe or as .py script
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    BASE_DIR = Path(sys.executable).parent
    APPLICATION_PATH = Path(sys.executable).parent
else:
    # Running as Python script
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    APPLICATION_PATH = Path(__file__).resolve().parent.parent.parent

# Load .env file from the correct location
env_path = APPLICATION_PATH / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try looking in parent directory
    parent_env = APPLICATION_PATH.parent / '.env'
    if parent_env.exists():
        load_dotenv(parent_env)
    # If still not found, .env loading will fail silently (user needs to create it)


class Config:
    """Application configuration settings"""
    
    # Application Info
    APP_NAME = "WhatsApp AI Message Automation"
    APP_VERSION = "1.0.0"
    
    # Directory Paths (PyInstaller compatible)
    BASE_DIR = BASE_DIR
    LOGS_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    
    # Create directories if they don't exist
    LOGS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    
    # AI Model Configuration
    # Only free or free-tier models are listed here
    AI_MODELS = {
        # ── FREE ONLINE (API key required but free tier available) ──────────
        "Groq Llama 3.3 70B (Free)": {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 500,
            "description": "Groq — fastest API available, free tier, best quality"
        },
        "Groq Llama 3.1 8B (Free)": {
            "provider": "groq",
            "model": "llama-3.1-8b-instant",
            "max_tokens": 500,
            "description": "Groq — ultra fast, lightweight, free tier"
        },
        "Gemini 2.0 Flash (Free)": {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "max_tokens": 500,
            "description": "Google Gemini — free tier, good quality"
        },

        # ── FREE OFFLINE (No API key, runs on your computer) ────────────────
        "Llama 3.2 (Offline - Free)": {
            "provider": "ollama",
            "model": "llama3.2",
            "max_tokens": 500,
            "description": "Runs locally, no internet needed — ollama pull llama3.2"
        },
        "Mistral (Offline - Free)": {
            "provider": "ollama",
            "model": "mistral",
            "max_tokens": 500,
            "description": "Runs locally, good quality — ollama pull mistral"
        },

        # ── PAID (optional, requires API key) ───────────────────────────────
        "GPT-4 Turbo": {
            "provider": "openai",
            "model": "gpt-4-turbo-preview",
            "max_tokens": 500,
            "description": "OpenAI GPT-4 — paid, best quality"
        },
        "GPT-3.5 Turbo": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "max_tokens": 500,
            "description": "OpenAI GPT-3.5 — paid, fast and affordable"
        },
    }
    
    # API Keys (from environment variables)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")       # Free — https://aistudio.google.com/app/apikey
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")           # Free — https://console.groq.com
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")       # Paid — https://platform.openai.com/
    
    # Ollama Configuration (for offline models)
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
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
    WINDOW_HEIGHT = 900  # Increased for scrollable GUI
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
        has_google = bool(cls.GOOGLE_API_KEY)
        has_groq = bool(cls.GROQ_API_KEY)
        has_openai = bool(cls.OPENAI_API_KEY)
        has_ollama = cls._check_ollama_available()
    
        if not (has_google or has_groq or has_openai or has_ollama):
            issues.append(
                "No AI services available!\n\n"
                "FREE OPTIONS (get API key in minutes):\n"
                "  • Google Gemini: https://aistudio.google.com/app/apikey\n"
                "  • Groq:          https://console.groq.com\n\n"
                "OFFLINE OPTION (no API key needed):\n"
                "  • Install Ollama: https://ollama.com/download\n"
                "    Then run: ollama pull llama3.2\n\n"
                "Add keys to .env file next to the .exe and restart the app."
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
        
        # Free online models
        if cls.GROQ_API_KEY:
            available.extend([
                "Groq Llama 3.3 70B (Free)",
                "Groq Llama 3.1 8B (Free)",
            ])
        
        if cls.GOOGLE_API_KEY:
            available.append("Gemini 2.0 Flash (Free)")

        # Offline models (Ollama)
        if cls._check_ollama_available():
            available.extend([
                "Llama 3.2 (Offline - Free)",
                "Mistral (Offline - Free)",
            ])

        # Paid models
        if cls.OPENAI_API_KEY:
            available.extend([
                "GPT-4 Turbo",
                "GPT-3.5 Turbo",
            ])

        # Fallback — show free options even if keys not set yet
        if not available:
            available = [
                "Gemini 2.0 Flash (Free)",
                "Groq Llama 3.3 70B (Free)",
                "Llama 3.2 (Offline - Free)",
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
                'is_free': model_config['provider'] in ['ollama', 'google', 'groq'],
                'needs_api_key': model_config['provider'] in ['openai']
            }
        return None