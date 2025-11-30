import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""

    # Application settings
    app_name: str = Field("YouTube WebSub Pipeline", description="The name of the application")
    app_version: str = Field("0.0.1", description="The version of the application")
    debug: bool = Field(False, description="Enable or disable debug mode")

    # API configuration
    api_host: str = Field("0.0.0.0", description="API host address")
    api_port: int = Field(8000, description="API port number")
    api_reload: bool = Field(True, description="Enable or disable API auto-reload")

    # Google gemini Configuration
    google_gemini_api_key: str | None = Field(None, description="Google Gemini API key")
    google_gemini_model: str = Field("gemini-2.5-pro", description="Google Gemini model to use")

    # Storage paths
    logs_directory: str = Field("./logs", description="Directory for application logs")

    # MongoDB configuration
    MONGODB_URI: str = Field("mongodb://mongodb:27017", description="MongoDB connection URI") # Use the service name
    MONGODB_DB_NAME: str = Field("youtube_websub", description="MongoDB database name")


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()


def ensure_directories() -> None:
    """Ensure directories exists."""
    settings = get_settings()
    os.makedirs(settings.logs_directory, exist_ok=True)


ensure_directories()
