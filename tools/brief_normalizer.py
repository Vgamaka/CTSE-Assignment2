"""Rule-based tool for normalizing rough project briefs."""

from __future__ import annotations

import re
from dataclasses import dataclass

from config.prompts import INTAKE_PROMPT
from graph.state import ProjectBrief
from utils.helpers import dedupe_strings, detect_constraints, detect_project_domain, detect_stakeholders
from utils.ollama_client import OllamaClient


@dataclass(slots=True)
class ProjectBriefNormalizerTool:
    """Extract a stable project brief from raw user input."""

    # Suggested ownership: student working on early parsing heuristics
    # and future local LLM-backed brief extraction.
    enable_llm_hook: bool = False

    def run(self, raw_input: str) -> ProjectBrief:
        """Return a structured project brief even when the input is vague."""
        # TODO: optionally replace parts of this rule-based extractor with
        # stronger local Ollama reasoning while keeping the same return shape.
        text = raw_input.strip()
        if not text:
            return ProjectBrief(
                summary="No project description was provided.",
                project_domain="unknown",
                stakeholders=["Stakeholders not specified"],
                requested_features=[],
                constraints=[],
                ambiguities=["Project description is empty."],
                clarification_questions=[
                    "What problem should the system solve?",
                    "Who are the intended users?",
                    "What are the most important features?",
                ],
                confidence="low",
            )

        project_domain = detect_project_domain(text)
        stakeholders = detect_stakeholders(text)
        requested_features = self._extract_features(text)
        llm_summary = self._generate_llm_summary(text)
        constraints = detect_constraints(text) + self._extract_constraints(text)
        ambiguities = self._extract_ambiguities(text, project_domain, stakeholders, requested_features)
        clarification_questions = self._build_clarification_questions(
            project_domain=project_domain,
            stakeholders=stakeholders,
            requested_features=requested_features,
            constraints=constraints,
            ambiguities=ambiguities,
        )
        confidence = "high" if project_domain != "unknown" and requested_features else "medium"
        if ambiguities and len(ambiguities) >= 3:
            confidence = "low"

        return ProjectBrief(
            summary=llm_summary or self._summarize_text(text),
            project_domain=project_domain,
            stakeholders=stakeholders or ["Stakeholders not clearly stated"],
            requested_features=requested_features,
            constraints=dedupe_strings(constraints),
            ambiguities=ambiguities,
            clarification_questions=clarification_questions,
            confidence=confidence,
        )

    def _generate_llm_summary(self, text: str) -> str:
        """Optionally enrich the brief summary with a local Ollama model."""
        if not self.enable_llm_hook:
            return ""
        prompt = (
            f"{INTAKE_PROMPT}\n\n"
            "Return only a concise 2-3 sentence summary of the user's project brief. "
            "Do not invent requirements. Keep it plain text.\n\n"
            f"User brief:\n{text}"
        )
        client = OllamaClient(
            base_url="http://localhost:11434",
            model="llama3.1:8b",
            temperature=0.1,
            timeout_seconds=60,
        )
        return self._summarize_text(client.generate(prompt))

    def _extract_features(self, text: str) -> list[str]:
        """Pull out feature-like statements from common requirement verbs."""
        feature_clauses: list[str] = []
        normalized = re.sub(r"[\n\r]+", " ", text)
        parts = [part.strip(" .") for part in re.split(r"[.;]", normalized) if part.strip()]
        markers = ("should", "must", "can", "allow", "enable", "help", "let")
        for part in parts:
            lowered = part.lower()
            if any(marker in lowered for marker in markers):
                feature_clauses.append(part[0].upper() + part[1:])
        if not feature_clauses and len(text.split()) > 6:
            feature_clauses.append(f"Support the core workflow described by the user brief: {self._summarize_text(text)}")
        return dedupe_strings(feature_clauses)

    def _extract_constraints(self, text: str) -> list[str]:
        """Detect explicit constraint-like statements."""
        clauses: list[str] = []
        parts = [part.strip(" .") for part in re.split(r"[.;]", text) if part.strip()]
        markers = (
            "important",
            "required",
            "constraint",
            "local",
            "deadline",
            "phase",
            "phased",
            "secure",
            "security",
            "reliable",
            "reliability",
            "usable",
            "usability",
            "privacy",
            "web-based",
            "web based",
            "terminal",
            "cli",
        )
        feature_patterns = (
            "should let",
            "should allow",
            "should help",
            "should enable",
            "should be able to",
            "should manage",
            "should record",
            "should create",
            "should browse",
            "should review",
            "should submit",
            "should upload",
            "should generate",
            "should receive",
            "can ",
            "allow ",
            "enable ",
            "help ",
        )
        for part in parts:
            lowered = part.lower()
            if any(marker in lowered for marker in markers) and not any(pattern in lowered for pattern in feature_patterns):
                clauses.append(part[0].upper() + part[1:])
        return dedupe_strings(clauses)

    def _extract_ambiguities(
        self,
        text: str,
        project_domain: str,
        stakeholders: list[str],
        requested_features: list[str],
    ) -> list[str]:
        """List missing information that will affect planning quality."""
        ambiguities: list[str] = []
        lowered = text.lower()
        if project_domain == "unknown":
            ambiguities.append("Project domain is not clearly identifiable from the brief.")
        if not stakeholders:
            ambiguities.append("Primary stakeholders or end users are not clearly named.")
        if not requested_features:
            ambiguities.append("Requested features are too vague for confident planning.")
        if "web" not in lowered and "mobile" not in lowered and "desktop" not in lowered and "cli" not in lowered:
            ambiguities.append("Target platform is not explicitly defined.")
        if "deadline" not in lowered and "semester" not in lowered and "phase" not in lowered:
            ambiguities.append("Delivery timeline or milestone expectations are not stated.")
        return dedupe_strings(ambiguities)

    def _build_clarification_questions(
        self,
        project_domain: str,
        stakeholders: list[str],
        requested_features: list[str],
        constraints: list[str],
        ambiguities: list[str],
    ) -> list[str]:
        """Turn ambiguity into assignment-friendly follow-up questions."""
        questions: list[str] = []
        if project_domain == "unknown":
            questions.append("What kind of software system is this and which domain does it serve?")
        if not stakeholders:
            questions.append("Who are the main users, stakeholders, or reviewers for this system?")
        if not requested_features:
            questions.append("What are the top features the system must support in its first release?")
        if not constraints:
            questions.append("Are there technical, timeline, or deployment constraints the plan must respect?")
        if not any("web" in item.lower() or "mobile" in item.lower() or "desktop" in item.lower() or "cli" in item.lower() for item in constraints):
            questions.append("What platform should the first release target?")
        if any("timeline" in item.lower() or "milestone" in item.lower() for item in ambiguities):
            questions.append("What delivery timeline or milestone should guide the roadmap?")
        return dedupe_strings(questions)

    def _summarize_text(self, text: str) -> str:
        """Create a short summary line from raw input text."""
        compact = " ".join(text.split())
        return compact[:220].rstrip() + ("..." if len(compact) > 220 else "")
