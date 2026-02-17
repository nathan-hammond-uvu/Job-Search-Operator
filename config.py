"""Configuration management."""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration."""
    
    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    MOCK_LLM: bool = os.getenv("MOCK_LLM", "false").lower() == "true"
    
    # Job discovery
    JOB_SOURCES: list[str] = os.getenv("JOB_SOURCES", "").split(",") if os.getenv("JOB_SOURCES") else []
    
    # Email scanning (disabled by default)
    EMAIL_SCANNING_ENABLED: bool = os.getenv("EMAIL_SCANNING_ENABLED", "false").lower() == "true"
    IMAP_SERVER: Optional[str] = os.getenv("IMAP_SERVER")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))
    EMAIL_ADDRESS: Optional[str] = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # Cleanup
    RECYCLE_BIN_DAYS: int = int(os.getenv("RECYCLE_BIN_DAYS", "7"))
    
    # Paths
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
    DOCUMENTS_DIR: Path = DATA_DIR / "documents"