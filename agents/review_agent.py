"""Risk and review agent implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from tools.file_exporter import FileExporterTool
from config.prompts import REVIEW_PROMPT
from graph.state import AgentTraceEntry, ToolHistoryEntry, WorkflowState
from tools.consistency_checker import ConsistencyRiskCheckerTool
from utils.helpers import build_markdown_output, safe_summary, summarize_updated_fields, utc_timestamp
from utils.logger import JsonlLogger


@dataclass(slots=True)
class ReviewAgent:
    """Review requirements and plan coverage, then optionally finalize output."""

    # Suggested ownership: student responsible for consistency checks,
    # risk analysis, and final Markdown assembly readiness.
    tool: ConsistencyRiskCheckerTool
    logger: JsonlLogger

    @property
    def name(self) -> str:
        """Stable LangGraph node name."""
        return "review_agent"

    def __call__(self, state: WorkflowState) -> dict[str, Any]:
        """Review the current plan and produce a final output if quality is acceptable."""
        review_cycles = state["review_cycles"] + 1
        risk_report = self.tool.run(state["requirements_spec"], state["delivery_plan"])
        if risk_report["severe_ambiguity"] and review_cycles <= state["max_review_loops"]:
            recommendation = "loop_to_intake"
        elif risk_report["severe_ambiguity"]:
            recommendation = "finalize_with_open_questions"
        else:
            recommendation = "finalize"

        if recommendation == "loop_to_intake":
            review_status = "needs_clarification"
            final_output = ""
        else:
            review_status = risk_report["review_status"]
            final_output = build_markdown_output(
                project_brief=state["project_brief"],
                requirements_spec=state["requirements_spec"],
                delivery_plan=state["delivery_plan"],
                risk_report={**risk_report, "recommendation": recommendation},
            )

            # Save final output using custom tool
            exporter = FileExporterTool()
            exporter.run("final_output.md", final_output)

        update = {
            "risk_report": {**risk_report, "recommendation": recommendation, "review_status": review_status},
            "final_output": final_output,
            "severe_ambiguity": risk_report["severe_ambiguity"],
            "review_cycles": review_cycles,
            "tool_history": self._append_tool(
                state["tool_history"],
                tool_name="Consistency & Risk Checker Tool",
                details={
                    "prompt_stub": REVIEW_PROMPT,
                    "review_status": review_status,
                    "missing_mapping_count": len(risk_report["missing_mappings"]),
                },
            ),
            "agent_trace": self._append_trace(
                state["agent_trace"],
                message=f"Reviewed the plan and set recommendation to {recommendation}.",
            ),
            "status": "needs_clarification" if recommendation == "loop_to_intake" else "finalized",
        }
        self.logger.log_agent_step(
            event_type="agent_step",
            agent=self.name,
            status=review_status,
            input_data={
                "requirements_spec": state["requirements_spec"],
                "delivery_plan": state["delivery_plan"],
            },
            output_data={"risk_report": update["risk_report"], "final_output": update["final_output"]},
            updated_fields=summarize_updated_fields(update),
            payload={
                "recommendation": recommendation,
                "severe_ambiguity": risk_report["severe_ambiguity"],
                "prompt_stub": safe_summary(REVIEW_PROMPT),
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
