"""
File scanner - discovers supported files in a directory.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from study_guide.config import config


@dataclass
class ScannedFile:
    """Represents a discovered file."""
    path: Path
    filename: str
    extension: str
    file_type: str  # document, video, audio
    size: int
    hash: str = field(default="")

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the file."""
        if self.hash:
            return self.hash

        sha256 = hashlib.sha256()
        with open(self.path, "rb") as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        self.hash = sha256.hexdigest()
        return self.hash


class FileScanner:
    """Scans directories for supported files."""

    def __init__(self, extensions: dict[str, set[str]] | None = None):
        self.extensions = extensions or config.SUPPORTED_EXTENSIONS

    def scan_directory(self, directory: Path | str) -> list[ScannedFile]:
        """
        Scan a directory for supported files.

        Args:
            directory: Path to the directory to scan

        Returns:
            List of ScannedFile objects
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        files: list[ScannedFile] = []

        for path in directory.rglob("*"):
            if path.is_file():
                scanned = self._scan_file(path)
                if scanned:
                    files.append(scanned)

        # Sort by filename for consistent ordering
        files.sort(key=lambda f: f.filename.lower())
        return files

    def scan_file(self, filepath: Path | str) -> ScannedFile | None:
        """
        Scan a single file.

        Args:
            filepath: Path to the file

        Returns:
            ScannedFile object or None if not supported
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if not filepath.is_file():
            raise ValueError(f"Path is not a file: {filepath}")

        return self._scan_file(filepath)

    def _scan_file(self, path: Path) -> ScannedFile | None:
        """Internal method to scan a single file."""
        extension = path.suffix.lower()

        # Determine file type
        file_type = self._get_file_type(extension)
        if not file_type:
            return None

        return ScannedFile(
            path=path.resolve(),
            filename=path.name,
            extension=extension,
            file_type=file_type,
            size=path.stat().st_size,
        )

    def _get_file_type(self, extension: str) -> str | None:
        """Determine the file type from extension."""
        for file_type, exts in self.extensions.items():
            if extension in exts:
                return file_type
        return None

    def get_supported_extensions(self) -> set[str]:
        """Get all supported extensions."""
        all_ext = set()
        for exts in self.extensions.values():
            all_ext.update(exts)
        return all_ext
