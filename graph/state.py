"""Shared state schema for the full multi-agent planning workflow."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from utils.helpers import utc_timestamp

WorkflowStatus = Literal[
    "initialized",
    "intake_complete",
    "requirements_complete",
    "planning_complete",
    "needs_clarification",
    "review_complete",
    "finalized",
    "failed",
]


class ToolHistoryEntry(TypedDict):
    """Simple record of a tool action for later tracing."""

    agent: str
    tool_name: str
    timestamp: str
    details: dict[str, Any]


class AgentTraceEntry(TypedDict):
    """Trace entry that explains each node decision in a readable format."""

    agent: str
    timestamp: str
    status: str
    message: str


class ProjectBrief(TypedDict):
    """Structured output from the intake and clarification stage."""

    summary: str
    project_domain: str
    stakeholders: list[str]
    requested_features: list[str]
    constraints: list[str]
    ambiguities: list[str]
    clarification_questions: list[str]
    confidence: str


class RequirementItem(TypedDict):
    """One deterministic requirement record."""

    requirement_id: str
    title: str
    description: str
    priority: str
    source: str


class ModuleItem(TypedDict):
    """One grouped module in the requirements or planning view."""

    module_id: str
    name: str
    description: str
    requirement_ids: list[str]


class RequirementsSpec(TypedDict):
    """Structured requirements artifact."""

    summary: str
    stakeholders: list[str]
    functional_requirements: list[RequirementItem]
    non_functional_requirements: list[RequirementItem]
    assumptions: list[str]
    missing_information: list[str]
    grouped_modules: list[ModuleItem]


class UserStoryItem(TypedDict):
    """A simple user story linked back to requirements."""

    story_id: str
    role: str
    goal: str
    benefit: str
    linked_requirement_ids: list[str]


class TaskItem(TypedDict):
    """A technical task produced by the planner."""

    task_id: str
    title: str
    description: str
    module_id: str
    requirement_ids: list[str]
    priority: str
    dependencies: list[str]
    phase: str


class RoadmapPhase(TypedDict):
    """One phase of the delivery roadmap."""

    phase_label: str
    goals: list[str]
    task_ids: list[str]


class DeliveryPlan(TypedDict):
    """Planning artifact that maps requirements to implementation work."""

    user_stories: list[UserStoryItem]
    modules: list[ModuleItem]
    technical_tasks: list[TaskItem]
    priorities: dict[str, str]
    dependencies: dict[str, list[str]]
    phased_roadmap: list[RoadmapPhase]


class RiskReport(TypedDict):
    """Structured review artifact produced by the review agent."""

    gaps: list[str]
    risks: list[str]
    validation_notes: list[str]
    missing_mappings: list[str]
    ambiguous_items: list[str]
    unsupported_assumptions: list[str]
    incomplete_module_coverage: list[str]
    missing_user_story_coverage: list[str]
    review_status: str
    recommendation: str
    severe_ambiguity: bool


class WorkflowState(TypedDict):
    """Shared graph state passed between all LangGraph nodes."""

    run_id: str
    created_at: str
    raw_user_input: str
    project_domain: str
    stakeholders: list[str]
    requested_features: list[str]
    constraints: list[str]
    clarification_questions: list[str]
    project_brief: ProjectBrief
    requirements_spec: RequirementsSpec
    delivery_plan: DeliveryPlan
    risk_report: RiskReport
    final_output: str
    tool_history: list[ToolHistoryEntry]
    agent_trace: list[AgentTraceEntry]
    errors: list[str]
    status: WorkflowStatus
    severe_ambiguity: bool
    review_cycles: int
    max_review_loops: int


def create_initial_state(raw_user_input: str, run_id: str, max_review_loops: int) -> WorkflowState:
    """Create a fully populated initial state so node logic stays simple."""
    return WorkflowState(
        run_id=run_id,
        created_at=utc_timestamp(),
        raw_user_input=raw_user_input.strip(),
        project_domain="unknown",
        stakeholders=[],
        requested_features=[],
        constraints=[],
        clarification_questions=[],
        project_brief=ProjectBrief(
            summary="",
            project_domain="unknown",
            stakeholders=[],
            requested_features=[],
            constraints=[],
            ambiguities=[],
            clarification_questions=[],
            confidence="low",
        ),
        requirements_spec=RequirementsSpec(
            summary="",
            stakeholders=[],
            functional_requirements=[],
            non_functional_requirements=[],
            assumptions=[],
            missing_information=[],
            grouped_modules=[],
        ),
        delivery_plan=DeliveryPlan(
            user_stories=[],
            modules=[],
            technical_tasks=[],
            priorities={},
            dependencies={},
            phased_roadmap=[],
        ),
        risk_report=RiskReport(
            gaps=[],
            risks=[],
            validation_notes=[],
            missing_mappings=[],
            ambiguous_items=[],
            unsupported_assumptions=[],
            incomplete_module_coverage=[],
            missing_user_story_coverage=[],
            review_status="pending",
            recommendation="review_pending",
            severe_ambiguity=False,
        ),
        final_output="",
        tool_history=[],
        agent_trace=[],
        errors=[],
        status="initialized",
        severe_ambiguity=False,
        review_cycles=0,
        max_review_loops=max_review_loops,
    )
