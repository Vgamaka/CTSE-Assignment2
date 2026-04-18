"""Tests for the intake and clarification agent."""

from __future__ import annotations

import json
from pathlib import Path

from agents.intake_agent import IntakeAgent
from graph.state import create_initial_state
from tools.brief_normalizer import ProjectBriefNormalizerTool
from utils.logger import JsonlLogger


def test_intake_agent_handles_empty_input_safely(tmp_path: Path) -> None:
    """Empty input should not crash and should produce clarification guidance."""
    agent = IntakeAgent(tool=ProjectBriefNormalizerTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))
    state = create_initial_state(raw_user_input="", run_id="empty", max_review_loops=1)

    update = agent(state)

    assert update["project_brief"]["project_domain"] == "unknown"
    assert update["project_brief"]["ambiguities"]
    assert update["project_brief"]["clarification_questions"]
    assert update["status"] == "intake_complete"


def test_intake_agent_vague_input_produces_ambiguity(tmp_path: Path) -> None:
    """Vague input should surface ambiguity and missing information."""
    agent = IntakeAgent(tool=ProjectBriefNormalizerTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))
    state = create_initial_state(raw_user_input="Need a system for planning.", run_id="vague", max_review_loops=1)

    update = agent(state)

    assert update["project_brief"]["ambiguities"]
    assert update["clarification_questions"]
    assert update["project_brief"]["confidence"] in {"low", "medium"}


def test_intake_agent_structured_input_extracts_core_fields(tmp_path: Path) -> None:
    """Structured input should extract stakeholders, features, and constraints."""
    text = (
        "Build a university portal where students and lecturers can submit project ideas, "
        "review milestones, and generate reports. It should be web-based, run locally, and "
        "support phased delivery."
    )
    log_path = tmp_path / "trace.jsonl"
    agent = IntakeAgent(tool=ProjectBriefNormalizerTool(), logger=JsonlLogger(log_path))
    state = create_initial_state(raw_user_input=text, run_id="structured", max_review_loops=1)

    update = agent(state)

    assert "Students" in update["stakeholders"]
    assert "Lecturers" in update["stakeholders"]
    assert update["requested_features"]
    assert update["constraints"]
    events = _read_jsonl(log_path)
    assert events[0]["agent"] == "intake_agent"
    assert "updated_fields" in events[0]


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    """Load JSONL trace events from disk."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

