"""LLM abstraction layer."""
import logging
from abc import ABC, abstractmethod
from typing import Optional

import requests

from config import Config

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """Abstract LLM interface."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text from prompt."""
        pass


class OllamaLLM(LLMInterface):
    """Ollama local LLM client."""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate text using Ollama API."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}", exc_info=True)
            raise


class MockLLM(LLMInterface):
    """Mock LLM for testing."""
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Return mock response."""
        if "summary" in prompt.lower():
            return "This is a mock job summary. The role involves Python development and requires 3+ years of experience."
        elif "fit score" in prompt.lower():
            return "0.85"
        elif "resume" in prompt.lower():
            return "<h1>John Doe</h1><p>Experienced Python Developer</p><h2>Experience</h2><ul><li>5 years Python</li></ul>"
        elif "cover letter" in prompt.lower():
            return "<p>Dear Hiring Manager,</p><p>I am excited to apply for this position...</p>"
        else:
            return "Mock LLM response"


def get_llm() -> LLMInterface:
    """Get configured LLM instance."""
    if Config.MOCK_LLM:
        logger.info("Using Mock LLM")
        return MockLLM()
    
    if Config.LLM_PROVIDER == "ollama":
        logger.info(f"Using Ollama LLM: {Config.OLLAMA_MODEL}")
        return OllamaLLM(Config.OLLAMA_BASE_URL, Config.OLLAMA_MODEL)
    
    raise ValueError(f"Unknown LLM provider: {Config.LLM_PROVIDER}")