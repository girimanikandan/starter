"""
Configuration Management
------------------------
Loads environment variables from .env file
Provides centralized configuration access
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # API Keys
    gemini_api_key: str
    serper_api_key: str
    firecrawl_api_key: str
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017/"
    database_name: str = "startup_validator"
    
    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    
    # API Timeouts (in seconds)
    api_timeout: int = 60
    
    # Search Configuration
    max_search_results: int = 10
    max_scrape_urls: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance
    LRU cache ensures we only create one instance
    """
    return Settings()