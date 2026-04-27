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

    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GENERATION_MODEL = os.getenv("STUDY_GUIDE_GENERATION_MODEL", "gpt-4o")
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
        "document": {".pptx", ".pdf", ".txt", ".md"},
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
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        return errors

    @classmethod
    def get_all_supported_extensions(cls) -> set[str]:
        """Get all supported file extensions."""
        all_ext = set()
        for exts in cls.SUPPORTED_EXTENSIONS.values():
            all_ext.update(exts)
        return all_ext


# Create singleton config instance
config = Config()
