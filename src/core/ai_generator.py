"""
AI Message Generation Module
Handles AI API integration for message improvement and personalization
Supported providers:
  - Google Gemini  (free, online)  — gemini-2.0-flash
  - Groq           (free, online)  — llama-3.3-70b / llama-3.1-8b
  - Ollama         (free, offline) — llama3.2 / mistral
  - OpenAI         (paid)          — gpt-4-turbo / gpt-3.5-turbo
Note: Anthropic/Claude removed (not free)
"""

import time
from typing import Optional, Dict
from ..utils.logger import Logger
from ..utils.config import Config

logger = Logger.get_logger(__name__)

class AIMessageGenerator:
    """Generates and improves messages using AI models"""
    
    def __init__(self, model_name: str):
        """
        Initialize AI generator with specified model
        
        Args:
            model_name: Name of the AI model to use
        """
        self.model_name = model_name
        self.model_config = Config.AI_MODELS.get(model_name)
        
        if not self.model_config:
            raise ValueError(f"Unknown model: {model_name}")
        
        self.provider = self.model_config["provider"]
        self.client = None
        self._initialize_client()
        
        logger.info(f"AI Generator initialized with model: {model_name} ({self.provider})")
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider"""
        try:
            if self.provider == "openai":
                if not Config.OPENAI_API_KEY:
                    raise ValueError(
                        "OpenAI API key not found.\n"
                        "Please set OPENAI_API_KEY in .env file\n"
                        "Get your key at: https://platform.openai.com/"
                    )
                
                import openai
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            
            elif self.provider == "groq":
                if not Config.GROQ_API_KEY:
                    raise ValueError(
                        "Groq API key not found.\n"
                        "Please set GROQ_API_KEY in .env file\n"
                        "Get your FREE key at: https://console.groq.com"
                    )

                from groq import Groq
                self.client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq client initialized")

            elif self.provider == "google":
                if not Config.GOOGLE_API_KEY:
                    raise ValueError(
                        "Google API key not found.\n"
                        "Please set GOOGLE_API_KEY in .env file\n"
                        "Get your FREE key at: https://makersuite.google.com/app/apikey"
                    )
                
                import google.generativeai as genai
                genai.configure(api_key=Config.GOOGLE_API_KEY)
                
                # Use the correct model name
                model_name = self.model_config["model"]
                self.client = genai.GenerativeModel(model_name)
                logger.info(f"Google Gemini client initialized with model: {model_name}")
            
            elif self.provider == "ollama":
                # Verify Ollama is running
                import requests
                try:
                    response = requests.get(f"{Config.OLLAMA_HOST}/api/tags", timeout=5)
                    if response.status_code == 200:
                        logger.info("Ollama server connected successfully")
                        
                        # Check if model is available
                        models_data = response.json()
                        available_models = [m['name'].split(':')[0] for m in models_data.get('models', [])]
                        
                        required_model = self.model_config["model"]
                        if required_model not in available_models:
                            logger.warning(
                                f"Model '{required_model}' not found locally. "
                                f"Available models: {available_models}"
                            )
                            raise ValueError(
                                f"Ollama model '{required_model}' not installed.\n\n"
                                f"To install, run:\n"
                                f"  ollama pull {required_model}\n\n"
                                f"Available models: {', '.join(available_models) if available_models else 'None'}\n"
                                f"Popular options:\n"
                                f"  • ollama pull llama3.2 (2GB, fast)\n"
                                f"  • ollama pull mistral (4GB, better quality)"
                            )
                    else:
                        raise ConnectionError("Ollama server not responding")
                        
                except requests.exceptions.ConnectionError:
                    raise ValueError(
                        "Cannot connect to Ollama server.\n\n"
                        "Setup instructions:\n"
                        "1. Install Ollama from: https://ollama.com/download\n"
                        "2. Start the server: ollama serve\n"
                        f"3. Download model: ollama pull {self.model_config['model']}\n\n"
                        "Then restart this application."
                    )
                
                logger.info(f"Ollama initialized with model: {self.model_config['model']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {str(e)}")
            raise
    
    def generate_message(self, name: str, original_message: Optional[str] = None, 
                        custom_prompt: Optional[str] = None) -> str:
        """
        Generate or improve a personalized message using AI
        
        Args:
            name: Recipient's name for personalization
            original_message: Original message to improve (if any)
            custom_prompt: Custom user prompt for message generation
            
        Returns:
            Generated/improved message string
        """
        try:
            # Build the prompt
            if original_message and original_message.strip():
                # Improve existing message
                prompt = self._build_improvement_prompt(name, original_message, custom_prompt)
            else:
                # Generate new message
                prompt = self._build_generation_prompt(name, custom_prompt)
            
            # Call appropriate API
            if self.provider == "openai":
                message = self._call_openai(prompt)
            elif self.provider == "groq":
                message = self._call_groq(prompt)
            elif self.provider == "google":
                message = self._call_google(prompt)
            elif self.provider == "ollama":
                message = self._call_ollama(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            logger.debug(f"Generated message for {name}: {message[:50]}...")
            return message
            
        except Exception as e:
            logger.error(f"Message generation failed for {name}: {str(e)}")
            # Return original message or a fallback
            if original_message:
                return original_message
            return f"Hi {name}, this is a personalized message for you."
    
    def _build_improvement_prompt(self, name: str, original_message: str, 
                                 custom_prompt: Optional[str]) -> str:
        """Build prompt for improving an existing message"""
        if custom_prompt:
            base_prompt = custom_prompt.replace("{message}", original_message).replace("{name}", name)
        else:
            base_prompt = Config.DEFAULT_AI_PROMPT.replace("{message}", original_message)
        
        return f"""{base_prompt}

Recipient Name: {name}

Important: Personalize the message by using the recipient's name naturally. Keep it concise (2-3 sentences max). 
Return ONLY the improved message text, no explanations or quotation marks."""
    
    def _build_generation_prompt(self, name: str, custom_prompt: Optional[str]) -> str:
        """Build prompt for generating a new message"""
        if custom_prompt:
            base_prompt = custom_prompt.replace("{name}", name)
        else:
            base_prompt = f"Write a professional, friendly, and personalized greeting message for {name}."
        
        return f"""{base_prompt}

Recipient Name: {name}

Important: Create a warm, professional message that uses the recipient's name. Keep it concise (2-3 sentences max).
Return ONLY the message text, no explanations or quotation marks."""
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI GPT API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_config["model"],
                max_tokens=self.model_config["max_tokens"],
                messages=[
                    {"role": "system", "content": "You are a professional message writer. Generate clear, concise, personalized messages."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract text from response
            message = response.choices[0].message.content.strip()
            
            # Remove quotation marks if present
            message = message.strip('"\'')
            
            return message
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API — extremely fast, free tier available"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_config["model"],
                max_tokens=self.model_config["max_tokens"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional message writer. "
                                   "Generate clear, concise, personalized messages."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            message = response.choices[0].message.content.strip()
            message = message.strip('"\'')
            return message

        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}")
            raise

    def _call_google(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            response = self.client.generate_content(prompt)
            
            # Extract text from response
            message = response.text.strip()
            
            # Remove quotation marks if present
            message = message.strip('"\'')
            
            return message
            
        except Exception as e:
            logger.error(f"Google Gemini API call failed: {str(e)}")
            raise
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API (local/offline)"""
        try:
            import requests
            
            url = f"{Config.OLLAMA_HOST}/api/generate"
            
            payload = {
                "model": self.model_config["model"],
                "prompt": prompt,
                "stream": False,  # Get complete response at once
                "options": {
                    "num_predict": self.model_config["max_tokens"],
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            logger.debug(f"Calling Ollama with model: {self.model_config['model']}")
            
            response = requests.post(url, json=payload, timeout=120)  # 2 min timeout
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('response', '').strip()
                
                # Remove quotation marks if present
                message = message.strip('"\'')
                
                if not message:
                    raise ValueError("Ollama returned empty response")
                
                return message
            else:
                error_detail = response.text
                raise Exception(f"Ollama API error: {response.status_code} - {error_detail}")
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout - model may be too slow for your hardware")
            raise Exception(
                "Ollama timeout. This model may be too large for your computer.\n"
                "Try a smaller model like 'llama3.2' or 'phi3'"
            )
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Lost connection to Ollama.\n"
                "Please ensure 'ollama serve' is still running."
            )
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test AI API connection
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Testing connection for {self.model_name}...")
            test_message = self.generate_message("Test User", "This is a test message.")
            success = bool(test_message) and len(test_message) > 10
            
            if success:
                logger.info(f"Connection test successful for {self.model_name}")
            else:
                logger.warning(f"Connection test returned short response for {self.model_name}")
            
            return success
        except Exception as e:
            logger.error(f"AI connection test failed: {str(e)}")
            return False