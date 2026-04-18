"""Task planner agent implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config.prompts import PLANNER_PROMPT
from graph.state import AgentTraceEntry, ToolHistoryEntry, WorkflowState
from tools.task_breakdown import TaskBreakdownGeneratorTool
from utils.helpers import safe_summary, summarize_updated_fields, utc_timestamp
from utils.logger import JsonlLogger


@dataclass(slots=True)
class PlannerAgent:
    """Convert requirements into user stories, modules, tasks, and roadmap phases."""

    # Suggested ownership: student responsible for roadmap design,
    # task sequencing, dependencies, and planning output quality.
    tool: TaskBreakdownGeneratorTool
    logger: JsonlLogger

    @property
    def name(self) -> str:
        """Stable LangGraph node name."""
        return "planner_agent"

    def __call__(self, state: WorkflowState) -> dict[str, Any]:
        """Read requirements_spec and build the delivery plan."""
        delivery_plan = self.tool.run(state["requirements_spec"])
        update = {
            "delivery_plan": delivery_plan,
            "tool_history": self._append_tool(
                state["tool_history"],
                tool_name="Task Breakdown Generator Tool",
                details={
                    "prompt_stub": PLANNER_PROMPT,
                    "task_count": len(delivery_plan["technical_tasks"]),
                    "phase_count": len(delivery_plan["phased_roadmap"]),
                },
            ),
            "agent_trace": self._append_trace(
                state["agent_trace"],
                message="Mapped requirements into user stories, modules, technical tasks, and a phased roadmap.",
            ),
            "status": "planning_complete",
        }
        self.logger.log_agent_step(
            event_type="agent_step",
            agent=self.name,
            status="completed",
            input_data=state["requirements_spec"],
            output_data=delivery_plan,
            updated_fields=summarize_updated_fields(update),
            payload={
                "task_count": len(delivery_plan["technical_tasks"]),
                "phase_count": len(delivery_plan["phased_roadmap"]),
                "prompt_stub": safe_summary(PLANNER_PROMPT),
            },
        )
        return update

    def _append_tool(
        self,
        history: list[ToolHistoryEntry],
        tool_name: str,
        details: dict[str, Any],
    ) -> list[ToolHistoryEntry]:
        entry: ToolHistoryEntry = {
            "agent": self.name,
            "tool_name": tool_name,
            "timestamp": utc_timestamp(),
            "details": details,
        }
        return [*history, entry]

    def _append_trace(self, trace: list[AgentTraceEntry], message: str) -> list[AgentTraceEntry]:
        entry: AgentTraceEntry = {
            "agent": self.name,
            "timestamp": utc_timestamp(),
            "status": "completed",
            "message": message,
        }
        return [*trace, entry]
