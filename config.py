"""Configuration management for ContentBlitz."""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # LLM Configuration
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")

    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # Search Configuration
    SERPAPI_API_KEY: Optional[str] = os.getenv("SERPAPI_API_KEY")

    # Image Generation
    STABILITY_API_KEY: Optional[str] = os.getenv("STABILITY_API_KEY")

    # Vector Database
    CHROMADB_PATH: str = os.getenv("CHROMADB_PATH", "./chroma_db")

    # Brand Settings
    DEFAULT_BRAND_NAME: str = os.getenv("DEFAULT_BRAND_NAME", "Your Brand")
    DEFAULT_BRAND_VOICE: str = os.getenv("DEFAULT_BRAND_VOICE", "professional, informative, friendly")
    DEFAULT_TARGET_AUDIENCE: str = os.getenv("DEFAULT_TARGET_AUDIENCE", "marketers and content creators")

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        has_llm = any([
            cls.ANTHROPIC_API_KEY,
            cls.OPENAI_API_KEY,
            cls.GOOGLE_API_KEY
        ])

        if not has_llm:
            raise ValueError(
                "At least one LLM API key must be configured. "
                "Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY."
            )

        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
