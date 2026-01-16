"""
Configuration management using pydantic-settings.
Loads environment variables from .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Hugging Face Configuration
    hf_api_token: str = ""
    hf_text_model: str = "mistralai/Mistral-7B-Instruct-v0.3"  # LLM for text generation
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"  # Image generation
    
    # ChromaDB Configuration
    chroma_db_path: str = "./chroma_db"
    dream_knowledge_zip: str = "dream_knowledge_db.zip"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration (comma-separated origins)
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Rate Limiting Configuration
    rate_limit_requests: int = 5
    rate_limit_window: str = "1 minute"
    
    # Input Validation
    max_dream_length: int = 500
    
    # Cache Configuration (seconds)
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 100
    
    # Supabase Configuration (for Auth & Database)
    supabase_url: str = ""
    supabase_key: str = ""  # anon/public key for client-side auth
    
    # API Security (Static API Key for Client Verification)
    api_secret_key: str = ""  # Required for all requests - blocks unauthorized clients
    
    # Admin Cron Secret (for external cron service fallback on Supabase Free tier)
    cron_secret: str = ""  # Protected admin endpoints for scheduled tasks
    
    # App Configuration
    app_name: str = "Dream Interpretation API"
    app_version: str = "1.0.0"
    
    def get_allowed_origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()
