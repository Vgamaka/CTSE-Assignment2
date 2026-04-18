"""LangGraph workflow assembly for the four-agent planning pipeline."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents import IntakeAgent, PlannerAgent, RequirementsAgent, ReviewAgent
from config.settings import AppSettings
from graph.routing import decide_review_route
from graph.state import WorkflowState
from tools import (
    ConsistencyRiskCheckerTool,
    ProjectBriefNormalizerTool,
    RequirementsFormatterTool,
    TaskBreakdownGeneratorTool,
)
from utils.logger import JsonlLogger


def build_workflow(logger: JsonlLogger, settings: AppSettings | None = None):
    """Construct the workflow with four agent classes and review routing."""
    settings = settings or AppSettings()
    workflow = StateGraph(WorkflowState)
    # Suggested ownership: one student can maintain graph orchestration and
    # routing behavior while other teammates focus on individual agents/tools.
    # The agents are classes so live LLM hooks can be injected later without
    # changing the graph topology used in the assignment demo.
    workflow.add_node(
        "intake_agent",
        IntakeAgent(
            tool=ProjectBriefNormalizerTool(enable_llm_hook=settings.enable_live_model),
            logger=logger,
        ),
    )
    workflow.add_node(
        "requirements_agent",
        RequirementsAgent(
            tool=RequirementsFormatterTool(enable_llm_hook=settings.enable_live_model),
            logger=logger,
        ),
    )
    workflow.add_node(
        "planner_agent",
        PlannerAgent(
            tool=TaskBreakdownGeneratorTool(enable_llm_hook=settings.enable_live_model),
            logger=logger,
        ),
    )
    workflow.add_node(
        "review_agent",
        ReviewAgent(
            tool=ConsistencyRiskCheckerTool(enable_llm_hook=settings.enable_live_model),
            logger=logger,
        ),
    )

    workflow.add_edge(START, "intake_agent")
    workflow.add_edge("intake_agent", "requirements_agent")
    workflow.add_edge("requirements_agent", "planner_agent")
    workflow.add_edge("planner_agent", "review_agent")
    workflow.add_conditional_edges(
        "review_agent",
        decide_review_route,
        {
            "intake_agent": "intake_agent",
            "finalize": END,
        },
    )
    return workflow.compile()
