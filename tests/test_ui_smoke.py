"""Lightweight smoke tests for the demo UI."""

from __future__ import annotations

from pathlib import Path

from graph.state import create_initial_state
from ui.app import create_app
from utils.workflow_runner import WorkflowRunResult


def test_ui_home_page_renders() -> None:
    """The UI home page should render the main demo sections."""
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Run Workflow" in body
    assert "Workflow Connectivity" in body
    assert "Final Output" in body


def test_ui_post_uses_runner_and_shows_results(tmp_path: Path) -> None:
    """Posting a brief should render the workflow summary with saved file paths."""
    state = create_initial_state("Build a local planner.", "ui-test", 1)
    state["project_domain"] = "project planning system"
    state["stakeholders"] = ["Students"]
    state["requested_features"] = ["Track project submissions"]
    state["project_brief"]["summary"] = "Build a local planner."
    state["project_brief"]["project_domain"] = "project planning system"
    state["project_brief"]["stakeholders"] = ["Students"]
    state["project_brief"]["requested_features"] = ["Track project submissions"]
    state["requirements_spec"]["functional_requirements"] = [
        {
            "requirement_id": "FR-001",
            "title": "Functional Requirement 1",
            "description": "Track project submissions",
            "priority": "high",
            "source": "project_brief.requested_features",
        }
    ]
    state["delivery_plan"]["technical_tasks"] = [
        {
            "task_id": "TASK-001",
            "title": "Implement Track Project Submissions",
            "description": "Build submission tracking.",
            "module_id": "MOD-001",
            "requirement_ids": ["FR-001"],
            "priority": "high",
            "dependencies": [],
            "phase": "Phase 1 - Foundation",
        }
    ]
    state["risk_report"]["review_status"] = "approved"
    state["risk_report"]["recommendation"] = "finalize"
    state["final_output"] = "# Demo Output"
    state["status"] = "finalized"

    markdown_path = tmp_path / "plan.md"
    json_path = tmp_path / "state.json"
    trace_path = tmp_path / "trace.jsonl"
    markdown_path.write_text("# Demo Output\n", encoding="utf-8")
    json_path.write_text('{"status": "finalized"}\n', encoding="utf-8")
    trace_path.write_text(
        '{"timestamp":"2026-04-18T00:00:00+00:00","event_type":"agent_step","agent":"intake_agent","status":"completed","input_summary":"brief","output_summary":"project brief","updated_fields":["project_brief"],"payload":{}}\n',
        encoding="utf-8",
    )

    def fake_runner(raw_user_input: str, *, settings=None, input_mode: str = "ui") -> WorkflowRunResult:
        assert raw_user_input == "Build a local planner."
        return WorkflowRunResult(
            final_state=state,
            markdown_output_path=markdown_path,
            json_snapshot_path=json_path,
            trace_log_path=trace_path,
        )

    app = create_app(runner=fake_runner)
    client = app.test_client()

    response = client.post("/", data={"brief_text": "Build a local planner."})

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Demo Output" in body
    assert "Trace / Log Preview" in body
    assert str(markdown_path) in body
