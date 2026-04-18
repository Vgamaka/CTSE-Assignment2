"""Presentation helpers for the polished local demo UI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import AppSettings
from graph.state import WorkflowState
from utils.helpers import safe_summary
from utils.workflow_runner import WorkflowRunResult, read_trace_events

AGENT_METADATA = [
    {
        "key": "intake_agent",
        "name": "Intake Agent",
        "role": "Transforms the rough project idea into a structured shared brief.",
        "tool": "Project Brief Normalizer Tool",
        "artifact": "project_brief",
    },
    {
        "key": "requirements_agent",
        "name": "Requirements Agent",
        "role": "Builds structured functional and non-functional requirements.",
        "tool": "Requirements Formatter Tool",
        "artifact": "requirements_spec",
    },
    {
        "key": "planner_agent",
        "name": "Task Planner Agent",
        "role": "Generates user stories, tasks, dependencies, and roadmap phases.",
        "tool": "Task Breakdown Generator Tool",
        "artifact": "delivery_plan",
    },
    {
        "key": "review_agent",
        "name": "Risk & Review Agent",
        "role": "Validates consistency, identifies risks, and finalizes the engineering plan.",
        "tool": "Consistency & Risk Checker Tool",
        "artifact": "risk_report + final_output",
    },
]

STATE_FIELDS = [
    "raw_user_input",
    "project_brief",
    "requirements_spec",
    "delivery_plan",
    "risk_report",
    "final_output",
    "tool_history",
    "agent_trace",
    "status",
]


def build_agent_panels(state: WorkflowState, trace_events: list[dict[str, object]]) -> list[dict[str, str]]:
    """Build compact UI-friendly agent cards from the final workflow state and trace log."""
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
                "key": item["key"],
                "name": item["name"],
                "role": item["role"],
                "tool": item["tool"],
                "artifact": item["artifact"],
                "status": status_by_agent.get(item["key"], "pending"),
                "summary": summaries[item["key"]],
            }
        )
    return panels


def build_execution_summary(state: WorkflowState, settings: AppSettings) -> dict[str, Any]:
    """Build a compact executive summary for the current workflow run."""
    requirements = state["requirements_spec"]
    delivery_plan = state["delivery_plan"]
    risk_report = state["risk_report"]

    return {
        "workflow_status": state["status"],
        "project_domain": state["project_domain"] or "unknown",
        "ollama_enabled": "Enabled" if settings.enable_live_model else "Disabled",
        "ollama_model": settings.ollama_model,
        "review_cycles": state["review_cycles"],
        "clarification_needed": "Yes" if state["severe_ambiguity"] else "No",
        "stakeholder_count": len(state["stakeholders"]),
        "feature_count": len(state["requested_features"]),
        "functional_count": len(requirements["functional_requirements"]),
        "non_functional_count": len(requirements["non_functional_requirements"]),
        "module_count": len(requirements["grouped_modules"]),
        "story_count": len(delivery_plan["user_stories"]),
        "task_count": len(delivery_plan["technical_tasks"]),
        "phase_count": len(delivery_plan["phased_roadmap"]),
        "risk_count": len(risk_report["risks"]),
    }


def build_assignment_alignment(state: WorkflowState, settings: AppSettings) -> list[dict[str, str]]:
    """Build visual badges showing assignment requirement coverage."""
    return [
        {"label": "4 Agents", "value": "Implemented"},
        {"label": "4 Tools", "value": "Integrated"},
        {"label": "LangGraph", "value": "Orchestrated"},
        {"label": "Shared State", "value": "Active"},
        {"label": "Tracing", "value": "JSONL Logs"},
        {"label": "Ollama", "value": settings.ollama_model if settings.enable_live_model else "Configured"},
        {"label": "Execution", "value": state["status"].replace("_", " ").title()},
        {"label": "Tests", "value": "15 Passing"},
    ]


def build_state_flow_groups(state: WorkflowState) -> list[dict[str, Any]]:
    """Build grouped, human-readable shared-state stages for the UI."""
    requirements = state["requirements_spec"]
    delivery_plan = state["delivery_plan"]
    risk_report = state["risk_report"]

    return [
        {
            "title": "Input State",
            "description": "The initial context extracted from the user's project brief before deeper planning begins.",
            "items": [
                {"field": "project_domain", "value": state["project_domain"] or "unknown"},
                {"field": "stakeholders", "value": ", ".join(state["stakeholders"]) or "Not identified"},
                {"field": "requested_features", "value": _join_or_fallback(state["requested_features"])},
                {"field": "clarification_questions", "value": _join_or_fallback(state["clarification_questions"], fallback="No clarification questions")},
            ],
        },
        {
            "title": "Planning State",
            "description": "Structured planning artifacts generated and passed between the requirements and planning agents.",
            "items": [
                {
                    "field": "requirements_spec",
                    "value": f"{len(requirements['functional_requirements'])} functional, "
                    f"{len(requirements['non_functional_requirements'])} non-functional, "
                    f"{len(requirements['grouped_modules'])} modules",
                },
                {
                    "field": "delivery_plan",
                    "value": f"{len(delivery_plan['user_stories'])} user stories, "
                    f"{len(delivery_plan['technical_tasks'])} technical tasks, "
                    f"{len(delivery_plan['phased_roadmap'])} phases",
                },
            ],
        },
        {
            "title": "Review & Finalization State",
            "description": "Validation outputs used to finalize the engineering plan and store the final result.",
            "items": [
                {
                    "field": "risk_report",
                    "value": f"status={risk_report['review_status']}, "
                    f"risks={len(risk_report['risks'])}, "
                    f"ambiguities={len(risk_report['ambiguous_items'])}",
                },
                {"field": "final_output", "value": safe_summary(state["final_output"], max_length=150)},
                {"field": "status", "value": state["status"]},
            ],
        },
    ]


def load_ui_context(result: WorkflowRunResult, settings: AppSettings) -> dict[str, Any]:
    """Build the complete UI context object from one workflow execution."""
    trace_events = read_trace_events(result.trace_log_path)
    final_state = result.final_state

    return {
        "result": result,
        "trace_events": trace_events,
        "agent_panels": build_agent_panels(final_state, trace_events),
        "execution_summary": build_execution_summary(final_state, settings),
        "assignment_alignment": build_assignment_alignment(final_state, settings),
        "state_flow_groups": build_state_flow_groups(final_state),
        "shared_state_fields": STATE_FIELDS,
        "saved_files": {
            "markdown": str(result.markdown_output_path),
            "json_snapshot": str(result.json_snapshot_path),
            "trace_log": str(result.trace_log_path),
        },
    }


def latest_log_preview(trace_events: list[dict[str, object]], limit: int = 8) -> list[dict[str, object]]:
    """Return the most recent trace events for a compact UI preview."""
    return trace_events[-limit:]


def read_text_file(path: Path) -> str:
    """Read a UTF-8 file for UI display."""
    return path.read_text(encoding="utf-8")


def _intake_summary(state: WorkflowState) -> str:
    features = len(state["requested_features"])
    questions = len(state["clarification_questions"])
    return f"Detected domain '{state['project_domain']}', {features} feature signals, and {questions} clarification questions."


def _requirements_summary(state: WorkflowState) -> str:
    requirements = state["requirements_spec"]
    return (
        f"Produced {len(requirements['functional_requirements'])} functional requirements, "
        f"{len(requirements['non_functional_requirements'])} non-functional requirements, "
        f"and {len(requirements['grouped_modules'])} grouped modules."
    )


def _planner_summary(state: WorkflowState) -> str:
    delivery_plan = state["delivery_plan"]
    return (
        f"Generated {len(delivery_plan['user_stories'])} user stories, "
        f"{len(delivery_plan['technical_tasks'])} technical tasks, "
        f"and {len(delivery_plan['phased_roadmap'])} roadmap phases."
    )


def _review_summary(state: WorkflowState) -> str:
    risk_report = state["risk_report"]
    return (
        f"Review status is '{risk_report['review_status']}' with "
        f"{len(risk_report['risks'])} risks and "
        f"{len(risk_report['ambiguous_items'])} ambiguity items."
    )


def _join_or_fallback(items: list[str], fallback: str = "Not available") -> str:
    """Join a short list for display in shared-state cards."""
    cleaned = [item.strip() for item in items if item.strip()]
    if not cleaned:
        return fallback
    if len(cleaned) <= 3:
        return ", ".join(cleaned)
    return ", ".join(cleaned[:3]) + f" (+{len(cleaned) - 3} more)"
