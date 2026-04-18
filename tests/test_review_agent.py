"""Tests for the review agent."""

from __future__ import annotations

from pathlib import Path

from agents.review_agent import ReviewAgent
from graph.state import create_initial_state
from tools.brief_normalizer import ProjectBriefNormalizerTool
from tools.consistency_checker import ConsistencyRiskCheckerTool
from tools.requirements_formatter import RequirementsFormatterTool
from tools.task_breakdown import TaskBreakdownGeneratorTool
from utils.logger import JsonlLogger


def test_review_agent_detects_missing_mappings(tmp_path: Path) -> None:
    """Review should flag requirements that do not map to technical tasks."""
    state = create_initial_state("Build a local system.", "review-missing", 1)
    project_brief = ProjectBriefNormalizerTool().run(
        "Build a local university system that should let students browse projects and lecturers review submissions."
    )
    requirements_spec = RequirementsFormatterTool().run(project_brief)
    delivery_plan = TaskBreakdownGeneratorTool().run(requirements_spec)
    delivery_plan["technical_tasks"] = delivery_plan["technical_tasks"][:-1]

    state["project_brief"] = project_brief
    state["requirements_spec"] = requirements_spec
    state["delivery_plan"] = delivery_plan

    agent = ReviewAgent(tool=ConsistencyRiskCheckerTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))
    update = agent(state)

    assert update["risk_report"]["missing_mappings"]
    assert update["status"] == "needs_clarification"


def test_review_agent_flags_vague_items(tmp_path: Path) -> None:
    """Review should surface vague or unclear missing-information items."""
    state = create_initial_state("Need something for planning.", "review-vague", 1)
    project_brief = ProjectBriefNormalizerTool().run("Need something for planning.")
    requirements_spec = RequirementsFormatterTool().run(project_brief)
    delivery_plan = TaskBreakdownGeneratorTool().run(requirements_spec)

    state["project_brief"] = project_brief
    state["requirements_spec"] = requirements_spec
    state["delivery_plan"] = delivery_plan

    agent = ReviewAgent(tool=ConsistencyRiskCheckerTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))
    update = agent(state)

    assert update["risk_report"]["ambiguous_items"]


def test_review_agent_generates_final_output_for_acceptable_plan(tmp_path: Path) -> None:
    """Acceptable plans should finalize and produce Markdown output."""
    text = (
        "Build a local SDLC planning assistant for a university. It should let students and lecturers "
        "track milestones, review submissions, and generate reports. It should be web-based and run locally."
    )
    state = create_initial_state(text, "review-good", 1)
    project_brief = ProjectBriefNormalizerTool().run(text)
    requirements_spec = RequirementsFormatterTool().run(project_brief)
    delivery_plan = TaskBreakdownGeneratorTool().run(requirements_spec)

    state["project_brief"] = project_brief
    state["requirements_spec"] = requirements_spec
    state["delivery_plan"] = delivery_plan

    agent = ReviewAgent(tool=ConsistencyRiskCheckerTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))
    update = agent(state)

    assert update["status"] == "finalized"
    assert update["final_output"]
    assert "# Local Multi-Agent SDLC Planning Assistant" in update["final_output"]
