"""Conditional routing helpers for the review stage."""

from __future__ import annotations

from typing import Literal

from graph.state import WorkflowState

ReviewRoute = Literal["finalize", "intake_agent"]


def decide_review_route(state: WorkflowState) -> ReviewRoute:
    """Route back to intake once when ambiguity is still severe."""
    if state["severe_ambiguity"] and state["review_cycles"] <= state["max_review_loops"]:
        return "intake_agent"
    return "finalize"

