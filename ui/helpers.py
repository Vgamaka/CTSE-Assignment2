"""Presentation helpers for the lightweight local demo UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from graph.state import WorkflowState
from utils.helpers import safe_summary
from utils.workflow_runner import WorkflowRunResult, read_trace_events

AGENT_METADATA = [
    {
        "key": "intake_agent",
        "name": "Intake Agent",
        "role": "Normalizes the rough project idea into a shared brief.",
        "tool": "Project Brief Normalizer Tool",
    },
    {
        "key": "requirements_agent",
        "name": "Requirements Agent",
        "role": "Creates structured functional and non-functional requirements.",
        "tool": "Requirements Formatter Tool",
    },
    {
        "key": "planner_agent",
        "name": "Task Planner Agent",
        "role": "Builds user stories, tasks, dependencies, and phases.",
        "tool": "Task Breakdown Generator Tool",
    },
    {
        "key": "review_agent",
        "name": "Risk & Review Agent",
        "role": "Checks consistency, flags risks, and finalizes output.",
        "tool": "Consistency & Risk Checker Tool",
    },
]


def build_agent_panels(state: WorkflowState, trace_events: list[dict[str, object]]) -> list[dict[str, str]]:
    """Build UI-friendly agent cards from the final workflow state and trace log."""
    status_by_agent = {
        str(event.get("agent")): str(event.get("status"))
        for event in trace_events
        if event.get("event_type") == "agent_step"
    }
    summaries = {
        "intake_agent": _intake_summary(state),
        "requirements_agent": _requirements_summary(state),
        "planner_agent": _planner_summary(state),
        "review_agent": _review_summary(state),
    }

    panels: list[dict[str, str]] = []
    for item in AGENT_METADATA:
        panels.append(
            {
                "name": item["name"],
                "role": item["role"],
                "tool": item["tool"],
                "status": status_by_agent.get(item["key"], "pending"),
                "summary": summaries[item["key"]],
            }
        )
    return panels


def load_ui_context(result: WorkflowRunResult) -> dict[str, Any]:
    """Build a single UI context object from one workflow execution."""
    trace_events = read_trace_events(result.trace_log_path)
    return {
        "result": result,
        "trace_events": trace_events,
        "agent_panels": build_agent_panels(result.final_state, trace_events),
        "saved_files": {
            "markdown": str(result.markdown_output_path),
            "json_snapshot": str(result.json_snapshot_path),
            "trace_log": str(result.trace_log_path),
        },
    }


def latest_log_preview(trace_events: list[dict[str, object]], limit: int = 12) -> list[dict[str, object]]:
    """Return the most recent trace events for a compact UI preview."""
    return trace_events[-limit:]


def read_text_file(path: Path) -> str:
    """Read a UTF-8 file for UI display."""
    return path.read_text(encoding="utf-8")


def _intake_summary(state: WorkflowState) -> str:
    return safe_summary(
        {
            "domain": state["project_domain"],
            "stakeholders": state["stakeholders"],
            "features": state["requested_features"],
            "clarification_questions": state["clarification_questions"],
        }
    )


def _requirements_summary(state: WorkflowState) -> str:
    requirements = state["requirements_spec"]
    return safe_summary(
        {
            "functional_requirements": len(requirements["functional_requirements"]),
            "non_functional_requirements": len(requirements["non_functional_requirements"]),
            "modules": len(requirements["grouped_modules"]),
        }
    )


def _planner_summary(state: WorkflowState) -> str:
    delivery_plan = state["delivery_plan"]
    return safe_summary(
        {
            "user_stories": len(delivery_plan["user_stories"]),
            "technical_tasks": len(delivery_plan["technical_tasks"]),
            "phases": len(delivery_plan["phased_roadmap"]),
        }
    )


def _review_summary(state: WorkflowState) -> str:
    risk_report = state["risk_report"]
    return safe_summary(
        {
            "review_status": risk_report["review_status"],
            "recommendation": risk_report["recommendation"],
            "risks": risk_report["risks"],
            "ambiguities": risk_report["ambiguous_items"],
        }
    )

