"""Structured JSONL logging for workflow execution traces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.helpers import ensure_directory, safe_json_value, safe_summary, utc_timestamp


class JsonlLogger:
    """Append-only logger that records structured execution events."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        ensure_directory(log_path.parent)

    def event(
        self,
        event_type: str,
        payload: dict[str, Any] | None = None,
        *,
        agent: str = "system",
        status: str = "info",
        input_summary: str = "",
        output_summary: str = "",
        updated_fields: list[str] | None = None,
    ) -> None:
        """Write one JSON object per line to the trace file."""
        normalized_payload = safe_json_value(payload or {})
        record = {
            "timestamp": utc_timestamp(),
            "event_type": event_type,
            "agent": agent,
            "status": status,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "updated_fields": updated_fields or [],
            "payload": normalized_payload,
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True, sort_keys=True))
            handle.write("\n")

    def log_agent_step(
        self,
        *,
        event_type: str,
        agent: str,
        status: str,
        input_data: Any,
        output_data: Any,
        updated_fields: list[str],
        payload: dict[str, Any] | None = None,
    ) -> None:
        """Convenience wrapper for consistent agent-step logging."""
        self.event(
            event_type,
            payload=payload or {},
            agent=agent,
            status=status,
            input_summary=safe_summary(input_data),
            output_summary=safe_summary(output_data),
            updated_fields=updated_fields,
        )
