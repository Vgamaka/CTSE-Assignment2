"""Tests for the requirements engineer agent."""

from __future__ import annotations

from pathlib import Path

from agents.requirements_agent import RequirementsAgent
from graph.state import create_initial_state
from tools.brief_normalizer import ProjectBriefNormalizerTool
from tools.requirements_formatter import RequirementsFormatterTool
from utils.logger import JsonlLogger


def test_requirements_agent_creates_fr_and_nfr_sections(tmp_path: Path) -> None:
    """Functional and non-functional requirement sections should always exist."""
    state = _state_with_brief(
        "Build a university planning system where students can submit projects and lecturers can review milestones."
    )
    agent = RequirementsAgent(tool=RequirementsFormatterTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))

    update = agent(state)

    assert update["requirements_spec"]["functional_requirements"]
    assert update["requirements_spec"]["non_functional_requirements"]


def test_requirements_agent_generates_deterministic_ids(tmp_path: Path) -> None:
    """Requirement IDs should use deterministic FR and NFR prefixes."""
    state = _state_with_brief(
        "Build a web-based university system that should let students browse topics and lecturers review submissions."
    )
    agent = RequirementsAgent(tool=RequirementsFormatterTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))

    update = agent(state)
    functional_ids = [item["requirement_id"] for item in update["requirements_spec"]["functional_requirements"]]
    non_functional_ids = [item["requirement_id"] for item in update["requirements_spec"]["non_functional_requirements"]]

    assert functional_ids[0] == "FR-001"
    assert all(item.startswith("FR-") for item in functional_ids)
    assert non_functional_ids[0] == "NFR-001"
    assert all(item.startswith("NFR-") for item in non_functional_ids)


def test_requirements_agent_keeps_assumptions_separate(tmp_path: Path) -> None:
    """Assumptions should not be mixed into confirmed requirements."""
    state = _state_with_brief("Need a planning platform for a department.")
    agent = RequirementsAgent(tool=RequirementsFormatterTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))

    update = agent(state)
    assumptions = update["requirements_spec"]["assumptions"]
    requirement_descriptions = [
        item["description"] for item in update["requirements_spec"]["functional_requirements"]
    ] + [
        item["description"] for item in update["requirements_spec"]["non_functional_requirements"]
    ]

    assert assumptions
    assert not any(assumption in requirement_descriptions for assumption in assumptions)


def _state_with_brief(text: str):
    """Create state with a normalized project brief for downstream agent tests."""
    state = create_initial_state(raw_user_input=text, run_id="req", max_review_loops=1)
    state["project_brief"] = ProjectBriefNormalizerTool().run(text)
    return state

