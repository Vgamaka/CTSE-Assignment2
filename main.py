"""Terminal entrypoint for the local MAS workflow."""

from __future__ import annotations

import argparse

from utils.file_io import read_user_input
from utils.workflow_runner import execute_workflow


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for direct text or file-based input."""
    parser = argparse.ArgumentParser(description="Local Multi-Agent SDLC Planning Assistant")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Direct project idea text to analyze.")
    group.add_argument("--input-file", type=str, help="Path to a sample input text file.")
    return parser


def main() -> int:
    """Run the workflow and persist Markdown, JSON snapshot, and JSONL trace outputs."""
    parser = build_parser()
    args = parser.parse_args()

    raw_user_input = read_user_input(text=args.text, input_file=args.input_file)

    try:
        result = execute_workflow(
            raw_user_input,
            input_mode="text" if args.text else "file",
        )
    except ModuleNotFoundError as exc:
        print("Error: missing dependency. Install requirements with `pip install -r requirements.txt`.")
        return 1
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        print(f"Error: {exc}")
        return 1

    print("Workflow execution finished.")
    print(f"Status: {result.final_state['status']}")
    print(f"Markdown output: {result.markdown_output_path}")
    print(f"JSON snapshot: {result.json_snapshot_path}")
    print(f"Trace log: {result.trace_log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
