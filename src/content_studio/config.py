"""Configuration settings for AI Content Studio."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    """Application settings with environment variable fallbacks."""

    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    api_key: str = Field(default_factory=lambda: os.getenv("API_KEY", "content_studio_secret_key"))

    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///data/content_studio.db")
    )

    # AI / LLM
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY") or None)
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))

    @property
    def sqlite_path(self) -> Path:
        """Extract Path from sqlite:/// URI or direct path."""
        uri = self.database_url
        if uri.startswith("sqlite:///"):
            uri = uri[len("sqlite:///"):]
        p = Path(uri)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached instance of application settings."""
    return Settings()
