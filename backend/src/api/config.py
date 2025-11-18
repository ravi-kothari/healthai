"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="local", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Redis Configuration
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # FHIR Server Configuration
    FHIR_SERVER_URL: str = Field(default="http://fhir-server:8080/fhir", env="FHIR_SERVER_URL")

    # Azure Services Configuration
    USE_MOCK_OPENAI: bool = Field(default=True, env="USE_MOCK_OPENAI")
    USE_MOCK_SPEECH: bool = Field(default=True, env="USE_MOCK_SPEECH")
    USE_MOCK_AUTH: bool = Field(default=True, env="USE_MOCK_AUTH")
    AZURE_OPENAI_ENDPOINT: str = Field(default="", env="AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY: str = Field(default="", env="AZURE_OPENAI_API_KEY")
    AZURE_SPEECH_KEY: str = Field(default="", env="AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION: str = Field(default="local", env="AZURE_SPEECH_REGION")

    # Authentication Configuration
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Azure Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = Field(default="", env="AZURE_STORAGE_CONNECTION_STRING")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:8000"]
    )

    # Allowed Hosts for production
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )

    # Feature Flags
    ENABLE_PREVISIT: bool = Field(default=True, env="ENABLE_PREVISIT")
    ENABLE_APPOINT_READY: bool = Field(default=True, env="ENABLE_APPOINT_READY")
    ENABLE_TRANSCRIPTION: bool = Field(default=True, env="ENABLE_TRANSCRIPTION")
    ENABLE_FHIR: bool = Field(default=True, env="ENABLE_FHIR")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )


# Create settings instance
settings = Settings()
