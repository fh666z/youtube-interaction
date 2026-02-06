"""Application configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Required settings
    google_api_key: str
    
    # Optional settings with defaults
    model_name: str = "gemini-3-pro-preview"
    model_provider: str = "google_genai"
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_api_key(self) -> None:
        """Validate that API key is provided."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.validate_api_key()
    return _settings
