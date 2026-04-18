"""File input and output helpers for the terminal workflow."""

from __future__ import annotations

import json
from pathlib import Path

from config.settings import AppSettings
from graph.state import WorkflowState
from utils.helpers import ensure_directory, safe_json_value


def read_user_input(text: str | None, input_file: str | None) -> str:
    """Load direct text or read a project brief from a file path."""
    if text and text.strip():
        return text.strip()
    if input_file:
        return Path(input_file).read_text(encoding="utf-8").strip()
    raise ValueError("Either --text or --input-file must be provided.")


def build_output_paths(settings: AppSettings, run_id: str) -> dict[str, Path]:
    """Prepare file paths for outputs and trace logs."""
    ensure_directory(settings.outputs_dir)
    ensure_directory(settings.logs_dir)
    return {
        "markdown_output": settings.outputs_dir / f"plan_{run_id}.md",
        "json_snapshot": settings.outputs_dir / f"state_{run_id}.json",
        "trace_log": settings.logs_dir / f"trace_{run_id}.jsonl",
    }


def save_markdown_output(markdown_text: str, output_path: Path) -> None:
    """Persist the final Markdown planning report."""
    output_path.write_text(markdown_text.rstrip() + "\n", encoding="utf-8")


def save_state_snapshot(state: WorkflowState, output_path: Path) -> None:
    """Persist the full final workflow state as readable JSON."""
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(safe_json_value(state), handle, indent=2, ensure_ascii=True)
        handle.write("\n")


def save_execution_outputs(state: WorkflowState, output_paths: dict[str, Path]) -> None:
    """Persist all final execution artifacts in a consistent order."""
    save_markdown_output(state["final_output"], output_paths["markdown_output"])
    save_state_snapshot(state, output_paths["json_snapshot"])
