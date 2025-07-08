"""
AI Backend Configuration for Multi-Agent System
==============================================

Handles intelligent backend selection between:
- Groq (fast cloud API with Llama models) - Primary if internet available
- Ollama (local Llama models) - Fallback for offline/privacy

Auto-detects availability and provides unified interface.
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path

# Ensure logs directory exists
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """AI Backend Configuration"""
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.2-90b-text-preview"  # Fast Groq Llama model
    ollama_model: str = "llama3.2:latest"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30
    prefer_groq: bool = True  # Use Groq if available
    
class AIBackend:
    """
    Unified AI Backend that intelligently selects between Groq and Ollama
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.groq_client = None
        self.ollama_client = None
        self.current_backend = None
        
        # Try to initialize backends
        self._init_groq()
        self._init_ollama()
        
        # Select best available backend
        self._select_backend()
    
    def _init_groq(self):
        """Initialize Groq client if API key is available"""
        try:
            # Check for API key in config or environment
            api_key = self.config.groq_api_key or os.getenv("GROQ_API_KEY")
            
            if api_key:
                from groq import Groq
                self.groq_client = Groq(api_key=api_key)
                
                # Test connection with a simple request
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": "Test"}],
                    model=self.config.groq_model,
                    max_tokens=10,
                    timeout=10
                )
                
                logger.info("✅ Groq backend initialized successfully")
                return True
                
            else:
                logger.info("ℹ️ Groq API key not found (set GROQ_API_KEY env var)")
                return False
                
        except ImportError:
            logger.warning("⚠️ Groq package not installed (pip install groq)")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Groq initialization failed: {e}")
            return False
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        try:
            from langchain_community.llms import Ollama
            
            self.ollama_client = Ollama(
                model=self.config.ollama_model,
                base_url=self.config.ollama_base_url,
                temperature=self.config.temperature
            )
            
            # Test connection
            response = self.ollama_client.invoke("Test", timeout=10)
            logger.info("✅ Ollama backend initialized successfully")
            return True
            
        except ImportError:
            logger.warning("⚠️ LangChain/Ollama not available")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama initialization failed: {e}")
            return False
    
    def _select_backend(self):
        """Select the best available backend"""
        if self.config.prefer_groq and self.groq_client:
            self.current_backend = "groq"
            logger.info("🚀 Using Groq backend (fast cloud API)")
        elif self.ollama_client:
            self.current_backend = "ollama"
            logger.info("🏠 Using Ollama backend (local)")
        else:
            self.current_backend = None
            logger.error("❌ No AI backend available!")
    
    def is_available(self) -> bool:
        """Check if any backend is available"""
        return self.current_backend is not None
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about current backend"""
        return {
            "backend": self.current_backend,
            "groq_available": self.groq_client is not None,
            "ollama_available": self.ollama_client is not None,
            "model": self.config.groq_model if self.current_backend == "groq" else self.config.ollama_model
        }
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the best available backend
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text
        """
        if not self.is_available():
            raise RuntimeError("No AI backend available")
        
        # Merge parameters
        params = {
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        try:
            if self.current_backend == "groq":
                return self._generate_groq(prompt, **params)
            elif self.current_backend == "ollama":
                return self._generate_ollama(prompt, **params)
            else:
                raise RuntimeError("No backend selected")
                
        except Exception as e:
            logger.error(f"Generation failed with {self.current_backend}: {e}")
            
            # Try fallback backend
            if self.current_backend == "groq" and self.ollama_client:
                logger.info("🔄 Falling back to Ollama...")
                self.current_backend = "ollama"
                return self._generate_ollama(prompt, **params)
            elif self.current_backend == "ollama" and self.groq_client:
                logger.info("🔄 Falling back to Groq...")
                self.current_backend = "groq"
                return self._generate_groq(prompt, **params)
            else:
                raise e
    
    def _generate_groq(self, prompt: str, **params) -> str:
        """Generate text using Groq"""
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.config.groq_model,
            temperature=params.get("temperature", 0.7),
            max_tokens=params.get("max_tokens", 4000),
            timeout=self.config.timeout
        )
        return response.choices[0].message.content
    
    def _generate_ollama(self, prompt: str, **params) -> str:
        """Generate text using Ollama"""
        return self.ollama_client.invoke(prompt)
    
    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async version of generate"""
        # Run in executor to avoid blocking
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await asyncio.get_event_loop().run_in_executor(
                executor, self.generate, prompt, **kwargs
            )

# Global AI backend instance
_ai_backend = None

def get_ai_backend() -> AIBackend:
    """Get global AI backend instance"""
    global _ai_backend
    if _ai_backend is None:
        _ai_backend = AIBackend()
    return _ai_backend

def initialize_ai(config: Optional[AIConfig] = None) -> AIBackend:
    """Initialize AI backend with custom config"""
    global _ai_backend
    _ai_backend = AIBackend(config)
    return _ai_backend

# Convenience functions
def generate_text(prompt: str, **kwargs) -> str:
    """Generate text using the best available backend"""
    return get_ai_backend().generate(prompt, **kwargs)

async def generate_text_async(prompt: str, **kwargs) -> str:
    """Async generate text using the best available backend"""
    return await get_ai_backend().generate_async(prompt, **kwargs)

def is_ai_available() -> bool:
    """Check if AI is available"""
    return get_ai_backend().is_available()

def get_ai_info() -> Dict[str, Any]:
    """Get AI backend information"""
    return get_ai_backend().get_backend_info()
