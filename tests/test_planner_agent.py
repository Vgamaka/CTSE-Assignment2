"""Tests for the planner agent."""

from __future__ import annotations

from pathlib import Path

from agents.planner_agent import PlannerAgent
from graph.state import create_initial_state
from tools.brief_normalizer import ProjectBriefNormalizerTool
from tools.requirements_formatter import RequirementsFormatterTool
from tools.task_breakdown import TaskBreakdownGeneratorTool
from utils.logger import JsonlLogger


def test_planner_agent_maps_requirements_to_tasks(tmp_path: Path) -> None:
    """Each functional requirement should be represented in the technical task plan."""
    state = _state_with_requirements(
        "Build a university system that should let students submit projects and lecturers review them."
    )
    agent = PlannerAgent(tool=TaskBreakdownGeneratorTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))

    update = agent(state)
    requirement_ids = {
        item["requirement_id"] for item in state["requirements_spec"]["functional_requirements"]
    }
    mapped_ids = {
        requirement_id
        for task in update["delivery_plan"]["technical_tasks"]
        for requirement_id in task["requirement_ids"]
    }

    assert requirement_ids.issubset(mapped_ids)


def test_planner_agent_creates_roadmap_phases(tmp_path: Path) -> None:
    """Planner output should include phased roadmap data."""
    state = _state_with_requirements(
        "Build a planning assistant that should manage briefs, requirements, tasks, and review reports."
    )
    agent = PlannerAgent(tool=TaskBreakdownGeneratorTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))

    update = agent(state)

    assert update["delivery_plan"]["phased_roadmap"]
    assert update["delivery_plan"]["phased_roadmap"][0]["phase_label"].startswith("Phase")


def test_planner_agent_includes_dependencies_and_priorities(tmp_path: Path) -> None:
    """Task data should expose priorities and dependencies for planning."""
    state = _state_with_requirements(
        "Build a web tool that should let students browse topics, submit work, and track milestones."
    )
    agent = PlannerAgent(tool=TaskBreakdownGeneratorTool(), logger=JsonlLogger(tmp_path / "trace.jsonl"))

    update = agent(state)
    tasks = update["delivery_plan"]["technical_tasks"]

    assert tasks
    assert all("priority" in task and task["priority"] for task in tasks)
    assert all("dependencies" in task for task in tasks)
    assert update["delivery_plan"]["priorities"]
    assert update["delivery_plan"]["dependencies"] is not None


def _state_with_requirements(text: str):
    """Create state with project brief and requirements for planner tests."""
    state = create_initial_state(raw_user_input=text, run_id="planner", max_review_loops=1)
    project_brief = ProjectBriefNormalizerTool().run(text)
    state["project_brief"] = project_brief
    state["requirements_spec"] = RequirementsFormatterTool().run(project_brief)
    return state

