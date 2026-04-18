"""Shared workflow runner used by the CLI and the lightweight demo UI."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from config.settings import AppSettings
from graph.state import WorkflowState, create_initial_state
from utils.file_io import build_output_paths, save_execution_outputs
from utils.helpers import safe_summary
from utils.logger import JsonlLogger


@dataclass(slots=True)
class WorkflowRunResult:
    """Final result object returned after one workflow execution."""

    final_state: WorkflowState
    markdown_output_path: Path
    json_snapshot_path: Path
    trace_log_path: Path


def execute_workflow(
    raw_user_input: str,
    *,
    settings: AppSettings | None = None,
    input_mode: str = "text",
) -> WorkflowRunResult:
    """Run the backend workflow once and persist all generated artifacts."""
    settings = settings or AppSettings()
    settings.ensure_directories()

    run_id = settings.new_run_id()
    output_paths = build_output_paths(settings=settings, run_id=run_id)
    logger = JsonlLogger(log_path=output_paths["trace_log"])

    initial_state: WorkflowState = create_initial_state(
        raw_user_input=raw_user_input,
        run_id=run_id,
        max_review_loops=settings.max_review_loops,
    )

    logger.event(
        "run_started",
        {"run_id": run_id, "input_mode": input_mode},
        agent="system",
        status="started",
        input_summary=safe_summary(raw_user_input),
        output_summary="Workflow initialized.",
        updated_fields=["run_id", "raw_user_input"],
    )

    try:
        # Import here so callers get a clean dependency error if LangGraph
        # is not installed in the local environment yet.
        from graph.workflow import build_workflow

        workflow = build_workflow(logger=logger, settings=settings)
        final_state = workflow.invoke(initial_state)
        save_execution_outputs(final_state, output_paths)
        logger.event(
            "run_completed",
            {
                "run_id": run_id,
                "status": final_state["status"],
                "markdown_output": str(output_paths["markdown_output"]),
                "json_snapshot": str(output_paths["json_snapshot"]),
            },
            agent="system",
            status=final_state["status"],
            input_summary=safe_summary({"run_id": run_id, "input_mode": input_mode}),
            output_summary=safe_summary(
                {
                    "markdown_output": str(output_paths["markdown_output"]),
                    "json_snapshot": str(output_paths["json_snapshot"]),
                    "trace_log": str(output_paths["trace_log"]),
                }
            ),
            updated_fields=["final_output", "risk_report", "status"],
        )
    except Exception as exc:
        logger.event(
            "run_failed",
            {"run_id": run_id, "error": str(exc)},
            agent="system",
            status="failed",
            input_summary=safe_summary(raw_user_input),
            output_summary=safe_summary(str(exc)),
            updated_fields=["errors", "status"],
        )
        raise

    return WorkflowRunResult(
        final_state=final_state,
        markdown_output_path=output_paths["markdown_output"],
        json_snapshot_path=output_paths["json_snapshot"],
        trace_log_path=output_paths["trace_log"],
    )


def read_trace_events(trace_log_path: Path) -> list[dict[str, object]]:
    """Load JSONL trace events for UI rendering and debugging."""
    return [
        json.loads(line)
        for line in trace_log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
