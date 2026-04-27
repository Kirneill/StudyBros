"""
Video/Audio extractor - extracts audio and transcribes using OpenAI Whisper.
"""

import tempfile
from pathlib import Path

from openai import OpenAI

from study_guide.config import config
from study_guide.ingestion.extractors.base import BaseExtractor, ExtractionResult
from study_guide.utils.audio import AudioProcessor


class VideoExtractor(BaseExtractor):
    """Extract transcription from video and audio files using OpenAI Whisper."""

    def __init__(self):
        self.client: OpenAI | None = None
        self.audio_processor = AudioProcessor()

    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self.client is None:
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set")
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        return self.client

    def supported_extensions(self) -> set[str]:
        return {".mp4", ".mov", ".webm", ".avi", ".mkv", ".mp3", ".wav", ".m4a", ".aac", ".ogg"}

    def extract(self, filepath: Path | str) -> ExtractionResult:
        """
        Extract transcription from a video/audio file.

        Steps:
        1. Extract audio from video (if video)
        2. Convert to suitable format
        3. Split into chunks if too large
        4. Transcribe each chunk using Whisper
        5. Combine transcriptions
        """
        try:
            filepath = self._validate_file(filepath)
            client = self._get_client()

            is_audio = filepath.suffix.lower() in {".mp3", ".wav", ".m4a", ".aac", ".ogg"}

            # Use temp directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Step 1 & 2: Extract/convert audio
                if is_audio:
                    audio_path = self.audio_processor.convert_audio(
                        filepath, temp_path / "audio.mp3"
                    )
                else:
                    audio_path = self.audio_processor.extract_audio(
                        filepath, temp_path / "audio.mp3"
                    )

                if not audio_path or not audio_path.exists():
                    return ExtractionResult(
                        text="",
                        success=False,
                        error="Failed to extract/convert audio",
                    )

                # Step 3: Check file size and split if needed
                audio_size_mb = audio_path.stat().st_size / (1024 * 1024)
                max_size_mb = config.AUDIO_CHUNK_SIZE_MB

                if audio_size_mb > max_size_mb:
                    # Split into chunks
                    audio_chunks = self.audio_processor.split_audio(
                        audio_path, temp_path, max_size_mb
                    )
                else:
                    audio_chunks = [audio_path]

                # Step 4: Transcribe each chunk
                transcriptions: list[str] = []

                for i, chunk_path in enumerate(audio_chunks):
                    transcript = self._transcribe_chunk(client, chunk_path)
                    if transcript:
                        transcriptions.append(transcript)

                # Step 5: Combine
                combined_text = "\n\n".join(transcriptions)

                # Get duration if possible
                try:
                    duration = self.audio_processor.get_duration(audio_path)
                except Exception:
                    duration = 0

                return ExtractionResult(
                    text=combined_text,
                    title=filepath.stem,
                    metadata={
                        "file_type": "video" if not is_audio else "audio",
                        "duration_seconds": duration,
                        "chunk_count": len(audio_chunks),
                    },
                    success=True,
                )

        except Exception as e:
            return ExtractionResult(
                text="",
                success=False,
                error=str(e),
            )

    def _transcribe_chunk(self, client: OpenAI, audio_path: Path) -> str:
        """Transcribe a single audio chunk using Whisper."""
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=config.TRANSCRIPTION_MODEL,
                file=audio_file,
                response_format="text",
            )
        return response if isinstance(response, str) else str(response)
