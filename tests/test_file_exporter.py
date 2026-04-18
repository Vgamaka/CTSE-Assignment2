"""
Tests for FileExporterTool (Assignment Requirement)

Validates:
- File creation
- Content correctness
- Error handling
"""

from pathlib import Path

from tools.file_exporter import FileExporterTool


def test_file_is_created(tmp_path: Path):
    """Ensure file is created successfully."""
    tool = FileExporterTool(output_dir=tmp_path)

    result = tool.run("test.txt", "Hello World")

    file_path = tmp_path / "test.txt"

    assert file_path.exists()
    assert result["success"] is True
    assert "saved successfully" in result["message"].lower()


def test_file_content_is_correct(tmp_path: Path):
    """Ensure written content matches expected."""
    tool = FileExporterTool(output_dir=tmp_path)

    tool.run("data.txt", "Sample Content")

    file_path = tmp_path / "data.txt"

    content = file_path.read_text()

    assert content == "Sample Content"


def test_invalid_filename_handled(tmp_path: Path):
    """Ensure tool handles invalid filenames gracefully."""
    tool = FileExporterTool(output_dir=tmp_path)

    result = tool.run("", "data")

    assert result["success"] is False
    assert "error" in result["message"].lower()


def test_overwrite_existing_file(tmp_path: Path):
    """Ensure existing files can be overwritten."""
    tool = FileExporterTool(output_dir=tmp_path)

    tool.run("overwrite.txt", "Old Content")
    tool.run("overwrite.txt", "New Content")

    file_path = tmp_path / "overwrite.txt"

    content = file_path.read_text()

    assert content == "New Content"