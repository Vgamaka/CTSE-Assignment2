"""Small helper utilities used across the planning scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    """Return an ISO 8601 UTC timestamp for traces and saved state."""
    return datetime.now(timezone.utc).isoformat()


def ensure_directory(path: Path) -> Path:
    """Create a directory if needed and return the same path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_json_value(value: Any) -> Any:
    """Convert values into JSON-safe structures for logs and snapshots."""
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {str(key): safe_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [safe_json_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def safe_json_dumps(value: Any) -> str:
    """Serialize any supported value into indented JSON text."""
    return json.dumps(safe_json_value(value), indent=2, ensure_ascii=True)


def safe_summary(value: Any, max_length: int = 240) -> str:
    """Create a short one-line summary for logs without flooding JSONL output."""
    normalized = safe_json_value(value)
    if isinstance(normalized, dict):
        text = ", ".join(f"{key}={type(item).__name__}" for key, item in normalized.items())
    elif isinstance(normalized, list):
        preview = ", ".join(str(item) for item in normalized[:4])
        suffix = f" ... (+{len(normalized) - 4} more)" if len(normalized) > 4 else ""
        text = f"[{preview}]{suffix}"
    else:
        text = str(normalized)

    compact = " ".join(text.split())
    return compact[:max_length].rstrip() + ("..." if len(compact) > max_length else "")


def summarize_updated_fields(update: dict[str, Any]) -> list[str]:
    """Return a sorted list of state fields updated by an agent."""
    return sorted(update.keys())


def dedupe_strings(items: list[str]) -> list[str]:
    """Preserve order while removing repeated text values."""
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        cleaned = item.strip()
        lowered = cleaned.lower()
        if cleaned and lowered not in seen:
            seen.add(lowered)
            output.append(cleaned)
    return output


def detect_project_domain(raw_user_input: str) -> str:
    """Infer a rough project domain from the input using deterministic keywords."""
    lowered = raw_user_input.lower()
    if "insurance" in lowered or "claim" in lowered or "policy" in lowered or "archive" in lowered:
        return "insurance records management"
    if "event" in lowered or "registration" in lowered or "volunteer" in lowered or "club" in lowered:
        return "event management"
    if "nursery" in lowered or "preschool" in lowered or "parent" in lowered or "attendance" in lowered:
        return "childcare management"
    if "university" in lowered or "student" in lowered or "campus" in lowered:
        return "education technology"
    if "hospital" in lowered or "clinic" in lowered or "patient" in lowered:
        return "healthcare software"
    if "shop" in lowered or "e-commerce" in lowered or "store" in lowered:
        return "commerce platform"
    if "project" in lowered or "planning" in lowered or "task" in lowered:
        return "project planning system"
    return "unknown"


def detect_stakeholders(raw_user_input: str) -> list[str]:
    """Extract common stakeholder labels from the input text."""
    lowered = raw_user_input.lower()
    candidates = {
        "students": "Students",
        "student": "Students",
        "lecturers": "Lecturers",
        "lecturer": "Lecturers",
        "admins": "Administrators",
        "admin": "Administrators",
        "teachers": "Teachers",
        "staff": "Staff",
        "records staff": "Records Staff",
        "supervisors": "Supervisors",
        "parents": "Parents",
        "parent": "Parents",
        "children": "Children",
        "club admins": "Club Administrators",
        "members": "Members",
        "organizers": "Organizers",
        "volunteers": "Volunteers",
        "users": "End Users",
    }
    matches = [label for key, label in candidates.items() if key in lowered]
    deduped = dedupe_strings(matches)

    if (
        "student team" in lowered
        and "students should" not in lowered
        and "students can" not in lowered
        and "for students" not in lowered
    ):
        deduped = [item for item in deduped if item != "Students"]

    if "Records Staff" in deduped and "Staff" in deduped:
        deduped = [item for item in deduped if item != "Staff"]
    if "Club Administrators" in deduped and "Administrators" in deduped:
        deduped = [item for item in deduped if item != "Administrators"]

    return deduped


def detect_constraints(raw_user_input: str) -> list[str]:
    """Extract obvious planning constraints from the input text."""
    lowered = raw_user_input.lower()
    constraints: list[str] = []
    if "local" in lowered:
        constraints.append("Must run locally")
    if "terminal" in lowered or "cli" in lowered:
        constraints.append("Should demonstrate clean terminal execution")
    if "web" in lowered:
        constraints.append("Target a web-first experience")
    if "secure" in lowered or "security" in lowered:
        constraints.append("Address security considerations early")
    if "phase" in lowered:
        constraints.append("Implementation should support phased delivery")
    return dedupe_strings(constraints)


def build_markdown_output(
    project_brief: dict[str, Any],
    requirements_spec: dict[str, Any],
    delivery_plan: dict[str, Any],
    risk_report: dict[str, Any],
) -> str:
    """Render an assignment-friendly Markdown report from the workflow state."""
    lines = [
        "# Local Multi-Agent SDLC Planning Assistant",
        "",
        "## Project Overview",
        f"- Summary: {project_brief.get('summary', 'Not available')}",
        f"- Domain: {project_brief.get('project_domain', 'unknown')}",
        f"- Confidence: {project_brief.get('confidence', 'unknown')}",
        "",
        "## Stakeholders and Users",
        *_bullet_lines(project_brief.get("stakeholders", [])),
        "",
        "## Functional Requirements",
        *_requirement_section(None, requirements_spec.get("functional_requirements", [])),
        "## Non-Functional Requirements",
        *_requirement_section(None, requirements_spec.get("non_functional_requirements", [])),
        "## Assumptions and Missing Details",
        "### Assumptions",
        *_bullet_lines(requirements_spec.get("assumptions", [])),
        "",
        "### Missing Details",
        *_bullet_lines(requirements_spec.get("missing_information", [])),
        "",
        "### Constraints",
        *_bullet_lines(project_brief.get("constraints", [])),
        "",
        "### Ambiguities",
        *_bullet_lines(project_brief.get("ambiguities", [])),
        "",
        "### Clarification Questions",
        *_bullet_lines(project_brief.get("clarification_questions", [])),
        "",
        "## Suggested Modules",
    ]

    for module in requirements_spec.get("grouped_modules", []):
        lines.append(
            f"- {module.get('module_id', 'MOD-?')} {module.get('name', 'Unnamed Module')}: "
            f"{module.get('description', '')}"
        )

    lines.extend(
        [
            "",
            "## User Stories",
        ]
    )

    for story in delivery_plan.get("user_stories", []):
        lines.append(
            f"- {story.get('story_id', 'US-?')}: As {story.get('role', 'a user')}, I want {story.get('goal', '')} "
            f"so that {story.get('benefit', '')}."
        )

    lines.extend(
        [
            "",
            "## Task Breakdown",
        ]
    )
    for task in delivery_plan.get("technical_tasks", []):
        lines.append(
            f"- {task.get('task_id', 'TASK-?')} [{task.get('priority', 'medium')}] {task.get('title', '')} "
            f"(Phase: {task.get('phase', 'Unassigned')}, Depends on: "
            f"{', '.join(task.get('dependencies', [])) or 'none'})"
        )

    lines.extend(
        [
            "",
            "## Risks and Validation Notes",
            f"- Severe Ambiguity: {risk_report.get('severe_ambiguity', False)}",
            f"- Review Status: {risk_report.get('review_status', 'unknown')}",
            f"- Recommendation: {risk_report.get('recommendation', 'finalize')}",
            "",
            "### Risks",
            *_bullet_lines(risk_report.get("risks", [])),
            "",
            "### Validation Notes",
            *_bullet_lines(risk_report.get("validation_notes", [])),
            "",
            "### Missing Requirement Mappings",
            *_bullet_lines(risk_report.get("missing_mappings", [])),
            "",
            "### Ambiguous Items",
            *_bullet_lines(risk_report.get("ambiguous_items", [])),
            "",
            "### Unsupported Assumptions",
            *_bullet_lines(risk_report.get("unsupported_assumptions", [])),
            "",
            "### Incomplete Module Coverage",
            *_bullet_lines(risk_report.get("incomplete_module_coverage", [])),
            "",
            "### Missing User Story Coverage",
            *_bullet_lines(risk_report.get("missing_user_story_coverage", [])),
            "",
            "## Recommended Development Phases",
        ]
    )

    for phase in delivery_plan.get("phased_roadmap", []):
        lines.append(
            f"- {phase.get('phase_label', 'Unnamed Phase')}: "
            f"{', '.join(phase.get('goals', []))} "
            f"[Tasks: {', '.join(phase.get('task_ids', [])) or 'none'}]"
        )

    return "\n".join(lines)


def _bullet_lines(items: list[str]) -> list[str]:
    """Render a list as Markdown bullets with a fallback line."""
    if not items:
        return ["- None identified"]
    return [f"- {item}" for item in items]


def _section_with_bullets(title: str, items: list[str]) -> list[str]:
    """Render a titled Markdown subsection."""
    return [f"### {title}", *_bullet_lines(items), ""]


def _requirement_section(title: str | None, items: list[dict[str, Any]]) -> list[str]:
    """Render structured requirement items with IDs."""
    lines = [f"### {title}"] if title else []
    if not items:
        return [*lines, "- None identified", ""]
    for item in items:
        lines.append(
            f"- {item.get('requirement_id', 'REQ-?')} [{item.get('priority', 'medium')}] "
            f"{item.get('description', '')}"
        )
    lines.append("")
    return lines
