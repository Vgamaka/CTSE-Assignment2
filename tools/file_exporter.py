"""
File Exporter Tool

Allows agents to persist outputs locally with validation and structured responses.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict


class FileExportResult(TypedDict):
    success: bool
    path: str
    message: str


@dataclass(slots=True)
class FileExporterTool:
    """Save outputs to local files with validation and structured result."""

    output_dir: Path = Path("exports")

    def run(self, filename: str, content: str) -> FileExportResult:
        """
        Save content to a file.

        Args:
            filename: Name of the file (must be non-empty and valid)
            content: Data to write

        Returns:
            FileExportResult with success status and file path
        """
        try:
            # 🔒 Validate filename
            if not filename or not filename.strip():
                raise ValueError("Filename cannot be empty")

            if any(char in filename for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
                raise ValueError("Filename contains invalid characters")

            # 📁 Ensure directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)

            file_path = self.output_dir / filename

            # 📝 Write file
            file_path.write_text(content, encoding="utf-8")

            return FileExportResult(
                success=True,
                path=str(file_path),
                message=f"File saved successfully: {file_path}",
            )

        except Exception as e:
            return FileExportResult(
                success=False,
                path="",
                message=f"Error saving file: {str(e)}",
            )