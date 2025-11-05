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

    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o")
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
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY must be configured. "
                "Please set OPENAI_API_KEY in your .env file. "
                "Get your API key from: https://platform.openai.com/api-keys"
            )

        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
