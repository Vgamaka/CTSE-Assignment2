"""Requirements engineer agent implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config.prompts import REQUIREMENTS_PROMPT
from graph.state import AgentTraceEntry, ToolHistoryEntry, WorkflowState
from tools.requirements_formatter import RequirementsFormatterTool
from utils.helpers import safe_summary, summarize_updated_fields, utc_timestamp
from utils.logger import JsonlLogger


@dataclass(slots=True)
class RequirementsAgent:
    """Transform the normalized brief into a structured requirements artifact."""

    # Suggested ownership: student responsible for requirement modeling,
    # requirement IDs, and grouped module structure.
    tool: RequirementsFormatterTool
    logger: JsonlLogger

    @property
    def name(self) -> str:
        """Stable LangGraph node name."""
        return "requirements_agent"

    def __call__(self, state: WorkflowState) -> dict[str, Any]:
        """Read project_brief and generate requirements_spec."""
        requirements_spec = self.tool.run(state["project_brief"])
        update = {
            "requirements_spec": requirements_spec,
            "tool_history": self._append_tool(
                state["tool_history"],
                tool_name="Requirements Formatter Tool",
                details={
                    "prompt_stub": REQUIREMENTS_PROMPT,
                    "functional_count": len(requirements_spec["functional_requirements"]),
                    "non_functional_count": len(requirements_spec["non_functional_requirements"]),
                },
            ),
            "agent_trace": self._append_trace(
                state["agent_trace"],
                message="Converted the normalized brief into structured functional and non-functional requirements.",
            ),
            "status": "requirements_complete",
        }
        self.logger.log_agent_step(
            event_type="agent_step",
            agent=self.name,
            status="completed",
            input_data=state["project_brief"],
            output_data=requirements_spec,
            updated_fields=summarize_updated_fields(update),
            payload={
                "functional_count": len(requirements_spec["functional_requirements"]),
                "non_functional_count": len(requirements_spec["non_functional_requirements"]),
                "prompt_stub": safe_summary(REQUIREMENTS_PROMPT),
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
