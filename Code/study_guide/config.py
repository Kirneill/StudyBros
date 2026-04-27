"""
Configuration management for the Study Guide application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    # Database
    DB_PATH = Path(os.getenv("STUDY_GUIDE_DB_PATH", str(DATA_DIR / "study_guide.db")))

    # Export directory
    EXPORT_DIR = Path(os.getenv("STUDY_GUIDE_EXPORT_DIR", str(DATA_DIR / "exports")))

    # Generation provider settings
    GENERATION_PROVIDER = os.getenv("STUDY_GUIDE_GENERATION_PROVIDER", "openai")

    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    OPENAI_GENERATION_MODEL = os.getenv(
        "STUDY_GUIDE_OPENAI_MODEL",
        os.getenv("STUDY_GUIDE_GENERATION_MODEL", "gpt-4o"),
    )
    ANTHROPIC_GENERATION_MODEL = os.getenv(
        "STUDY_GUIDE_ANTHROPIC_MODEL",
        "claude-3-5-sonnet-latest",
    )
    OPENROUTER_GENERATION_MODEL = os.getenv(
        "STUDY_GUIDE_OPENROUTER_MODEL",
        "openai/gpt-4o-mini",
    )

    # Backward-compatible alias for legacy call sites
    GENERATION_MODEL = OPENAI_GENERATION_MODEL
    TRANSCRIPTION_MODEL = os.getenv("STUDY_GUIDE_TRANSCRIPTION_MODEL", "whisper-1")

    # Generation limits (cost guardrails)
    MAX_CHUNKS_PER_GENERATION = int(os.getenv("STUDY_GUIDE_MAX_CHUNKS_PER_GENERATION", "5"))
    MAX_TOKENS_PER_RESPONSE = int(os.getenv("STUDY_GUIDE_MAX_TOKENS_PER_RESPONSE", "4000"))

    # Audio processing
    AUDIO_CHUNK_SIZE_MB = int(os.getenv("STUDY_GUIDE_AUDIO_CHUNK_SIZE_MB", "20"))

    # Chunking settings
    CHUNK_SIZE = 1500  # characters
    CHUNK_OVERLAP = 200  # characters

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        "document": {".pptx", ".pdf", ".txt", ".md", ".markdown", ".text"},
        "video": {".mp4", ".mov", ".webm", ".avi", ".mkv"},
        "audio": {".mp3", ".wav", ".m4a", ".aac", ".ogg"},
    }

    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        provider = cls.GENERATION_PROVIDER.lower()
        if provider == "anthropic" and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is not set")
        elif provider == "openrouter" and not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is not set")
        elif provider == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        elif provider not in {"openai", "anthropic", "openrouter"}:
            errors.append(
                "STUDY_GUIDE_GENERATION_PROVIDER must be one of: openai, anthropic, openrouter"
            )
        return errors

    @classmethod
    def get_provider_api_key(cls, provider: str) -> str:
        """Return the configured API key for a generation provider."""
        normalized = provider.lower()
        if normalized == "anthropic":
            return cls.ANTHROPIC_API_KEY
        if normalized == "openrouter":
            return cls.OPENROUTER_API_KEY
        return cls.OPENAI_API_KEY

    @classmethod
    def has_provider_api_key(cls, provider: str) -> bool:
        """Whether a provider has a server-configured API key."""
        return bool(cls.get_provider_api_key(provider).strip())

    @classmethod
    def get_generation_model(cls, provider: str) -> str:
        """Return the default generation model for a provider."""
        normalized = provider.lower()
        if normalized == "anthropic":
            return cls.ANTHROPIC_GENERATION_MODEL
        if normalized == "openrouter":
            return cls.OPENROUTER_GENERATION_MODEL
        return cls.OPENAI_GENERATION_MODEL

    @classmethod
    def get_all_supported_extensions(cls) -> set[str]:
        """Get all supported file extensions."""
        all_ext = set()
        for exts in cls.SUPPORTED_EXTENSIONS.values():
            all_ext.update(exts)
        return all_ext


# Create singleton config instance
config = Config()
