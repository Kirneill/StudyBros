"""
Audio processing utilities using FFmpeg.
"""

import shutil
import subprocess
from pathlib import Path

import ffmpeg


class AudioProcessor:
    """Audio processing utilities using FFmpeg."""

    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        return shutil.which("ffmpeg") is not None

    def _ensure_ffmpeg(self):
        """Raise error if FFmpeg is not available."""
        if not self.ffmpeg_available:
            raise RuntimeError(
                "FFmpeg is not installed or not in PATH. "
                "Please install FFmpeg to process video/audio files."
            )

    def extract_audio(self, input_path: Path, output_path: Path) -> Path:
        """
        Extract audio from a video file.

        Args:
            input_path: Path to video file
            output_path: Path for output audio file

        Returns:
            Path to extracted audio file
        """
        self._ensure_ffmpeg()

        try:
            # Use ffmpeg-python for extraction
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="libmp3lame",
                ac=1,  # Mono
                ar=16000,  # 16kHz sample rate (good for speech)
                ab="64k",  # 64kbps bitrate
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")

    def convert_audio(self, input_path: Path, output_path: Path) -> Path:
        """
        Convert audio to a suitable format for transcription.

        Args:
            input_path: Path to audio file
            output_path: Path for output audio file

        Returns:
            Path to converted audio file
        """
        self._ensure_ffmpeg()

        try:
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="libmp3lame",
                ac=1,  # Mono
                ar=16000,  # 16kHz
                ab="64k",  # 64kbps
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")

    def split_audio(
        self, input_path: Path, output_dir: Path, max_size_mb: float
    ) -> list[Path]:
        """
        Split audio file into smaller chunks.

        Args:
            input_path: Path to audio file
            output_dir: Directory for output chunks
            max_size_mb: Maximum size per chunk in MB

        Returns:
            List of paths to audio chunks
        """
        self._ensure_ffmpeg()

        # Get duration
        duration = self.get_duration(input_path)
        file_size_mb = input_path.stat().st_size / (1024 * 1024)

        # Calculate chunk duration based on size ratio
        if file_size_mb <= max_size_mb:
            return [input_path]

        # Estimate seconds per MB
        seconds_per_mb = duration / file_size_mb
        chunk_duration = int(max_size_mb * seconds_per_mb * 0.9)  # 10% safety margin

        # Split into chunks
        chunks: list[Path] = []
        current_time = 0

        while current_time < duration:
            chunk_num = len(chunks)
            chunk_path = output_dir / f"chunk_{chunk_num:03d}.mp3"

            try:
                stream = ffmpeg.input(str(input_path), ss=current_time, t=chunk_duration)
                stream = ffmpeg.output(
                    stream,
                    str(chunk_path),
                    acodec="libmp3lame",
                    ac=1,
                    ar=16000,
                    ab="64k",
                )
                ffmpeg.run(stream, overwrite_output=True, quiet=True)

                if chunk_path.exists() and chunk_path.stat().st_size > 0:
                    chunks.append(chunk_path)

            except ffmpeg.Error:
                # Stop if we can't create more chunks
                break

            current_time += chunk_duration

        return chunks

    def get_duration(self, audio_path: Path) -> float:
        """
        Get the duration of an audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        self._ensure_ffmpeg()

        try:
            probe = ffmpeg.probe(str(audio_path))
            duration = float(probe["format"]["duration"])
            return duration
        except (ffmpeg.Error, KeyError) as e:
            # Fallback: try using ffprobe directly
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(audio_path),
                    ],
                    capture_output=True,
                    text=True,
                )
                return float(result.stdout.strip())
            except Exception:
                raise RuntimeError(f"Could not get duration: {e}")
