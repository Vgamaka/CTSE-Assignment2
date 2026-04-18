"""
Evaluation tests for Multi-Agent System (Assignment Requirement)

Validates:
- Output structure
- Requirement completeness
- Planning correctness
- Risk identification
"""

from utils.workflow_runner import execute_workflow


def test_output_contains_core_sections():
    """Ensure final output includes all key SDLC sections."""
    result = execute_workflow(
        "Build a simple student portal where users can register, login, and manage courses."
    )

    output = result.final_state["final_output"]

    assert "Project Overview" in output
    assert "Functional Requirements" in output
    assert "Task Breakdown" in output
    assert "Risks" in output


def test_requirements_are_generated():
    """Check if functional requirements are actually created."""
    result = execute_workflow(
        "Build a web system for managing event registrations with admin control."
    )

    requirements = result.final_state["requirements_spec"]["functional_requirements"]

    assert isinstance(requirements, list)
    assert len(requirements) > 0


def test_tasks_are_linked_to_requirements():
    """Ensure planning is logically derived from requirements."""
    result = execute_workflow(
        "Create a task management system where users can create and track tasks."
    )

    tasks = result.final_state["delivery_plan"]["technical_tasks"]

    assert len(tasks) > 0
    assert all("requirement_ids" in task for task in tasks)


def test_risk_detection_present():
    """Ensure system identifies risks or ambiguity."""
    result = execute_workflow("Build something")

    risks = result.final_state["risk_report"]["risks"]

    assert isinstance(risks, list)


def test_low_quality_input_triggers_ambiguity():
    """Weak input should trigger clarification questions."""
    result = execute_workflow("System")

    ambiguities = result.final_state["project_brief"]["ambiguities"]

    assert len(ambiguities) > 0