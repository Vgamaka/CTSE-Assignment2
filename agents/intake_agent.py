"""Intake and clarification agent implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config.prompts import INTAKE_PROMPT
from graph.state import AgentTraceEntry, ToolHistoryEntry, WorkflowState
from tools.brief_normalizer import ProjectBriefNormalizerTool
from utils.helpers import safe_summary, summarize_updated_fields, utc_timestamp
from utils.logger import JsonlLogger


@dataclass(slots=True)
class IntakeAgent:
    """Read raw user input and normalize it into a shared project brief."""

    # Suggested ownership: student responsible for input understanding,
    # ambiguity handling, and brief normalization logic.
    tool: ProjectBriefNormalizerTool
    logger: JsonlLogger

    @property
    def name(self) -> str:
        """Stable LangGraph node name."""
        return "intake_agent"

    def __call__(self, state: WorkflowState) -> dict[str, Any]:
        """Process raw input and write project brief fields back to shared state."""
        project_brief = self.tool.run(state["raw_user_input"])
        update = {
            "project_domain": project_brief["project_domain"],
            "stakeholders": project_brief["stakeholders"],
            "requested_features": project_brief["requested_features"],
            "constraints": project_brief["constraints"],
            "clarification_questions": project_brief["clarification_questions"],
            "project_brief": project_brief,
            "tool_history": self._append_tool(
                state["tool_history"],
                tool_name="Project Brief Normalizer Tool",
                details={
                    "prompt_stub": INTAKE_PROMPT,
                    "stakeholder_count": len(project_brief["stakeholders"]),
                    "feature_count": len(project_brief["requested_features"]),
                },
            ),
            "agent_trace": self._append_trace(
                state["agent_trace"],
                message="Normalized the raw brief into domain, stakeholders, features, and ambiguities.",
            ),
            "status": "intake_complete",
        }
        self.logger.log_agent_step(
            event_type="agent_step",
            agent=self.name,
            status="completed",
            input_data={"raw_user_input": state["raw_user_input"]},
            output_data=project_brief,
            updated_fields=summarize_updated_fields(update),
            payload={
                "project_domain": project_brief["project_domain"],
                "clarification_count": len(project_brief["clarification_questions"]),
                "prompt_stub": safe_summary(INTAKE_PROMPT),
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
