"""End-to-end system flow tests for the local MAS planner."""

from __future__ import annotations

import json
from pathlib import Path

from config.settings import AppSettings
from graph.state import WorkflowState, create_initial_state
from graph.workflow import build_workflow
from utils.file_io import build_output_paths, save_execution_outputs
from utils.logger import JsonlLogger


def test_system_flow_runs_end_to_end_and_persists_outputs(tmp_path: Path) -> None:
    """The full workflow should run, save outputs, and emit structured logs."""
    happy_path_input = (
        "Build a local SDLC planning assistant for a university department. "
        "It should help students and lecturers propose ideas, review milestones, "
        "track submissions, and generate reports. The first release should be web-based, "
        "run locally, and support phased delivery."
    )
    settings = AppSettings(project_root=tmp_path)
    settings.ensure_directories()

    output_paths = build_output_paths(settings=settings, run_id="systemflow")
    logger = JsonlLogger(log_path=output_paths["trace_log"])
    workflow = build_workflow(logger=logger, settings=settings)
    initial_state: WorkflowState = create_initial_state(
        raw_user_input=happy_path_input,
        run_id="systemflow",
        max_review_loops=settings.max_review_loops,
    )

    logger.event(
        "run_started",
        {"run_id": "systemflow"},
        agent="system",
        status="started",
        input_summary="system flow test started",
        output_summary="workflow compiled",
        updated_fields=["run_id"],
    )
    final_state = workflow.invoke(initial_state)
    save_execution_outputs(final_state, output_paths)
    logger.event(
        "run_completed",
        {"run_id": "systemflow"},
        agent="system",
        status=final_state["status"],
        input_summary="system flow completed",
        output_summary="artifacts saved",
        updated_fields=["final_output", "status"],
    )

    assert final_state["status"] == "finalized"
    assert final_state["final_output"]
    assert final_state["tool_history"]
    assert final_state["agent_trace"]
    assert len(final_state["tool_history"]) >= 4
    assert len(final_state["agent_trace"]) >= 4

    assert output_paths["markdown_output"].exists()
    assert output_paths["json_snapshot"].exists()
    assert output_paths["trace_log"].exists()

    saved_state = json.loads(output_paths["json_snapshot"].read_text(encoding="utf-8"))
    assert saved_state["status"] == "finalized"
    assert saved_state["final_output"]

    log_events = _read_jsonl(output_paths["trace_log"])
    assert log_events
    for event in log_events:
        assert "timestamp" in event
        assert "agent" in event
        assert "status" in event
        assert "input_summary" in event
        assert "output_summary" in event
        assert "updated_fields" in event


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    """Load a JSONL file into Python dictionaries."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

