"""Deterministic formatter for requirement structures."""

from __future__ import annotations

from dataclasses import dataclass

from graph.state import ModuleItem, ProjectBrief, RequirementItem, RequirementsSpec
from utils.helpers import dedupe_strings


@dataclass(slots=True)
class RequirementsFormatterTool:
    """Convert a normalized project brief into structured requirements."""

    # Suggested ownership: student responsible for deterministic requirement
    # generation and separation of assumptions from confirmed requirements.
    enable_llm_hook: bool = False

    def run(self, project_brief: ProjectBrief) -> RequirementsSpec:
        """Generate deterministic FR and NFR records plus grouped modules."""
        # TODO: enrich requirement phrasing with local model assistance once
        # stable structured prompting has been validated.
        functional_features, derived_constraints = self._split_feature_candidates(project_brief["requested_features"])
        stakeholders = project_brief["stakeholders"]
        constraints = dedupe_strings([*project_brief["constraints"], *derived_constraints])

        functional_requirements = self._build_functional_requirements(functional_features)
        non_functional_requirements = self._build_non_functional_requirements(constraints, project_brief["project_domain"])
        assumptions = self._build_assumptions(project_brief)
        grouped_modules = self._build_modules(functional_requirements)

        return RequirementsSpec(
            summary="Requirements specification derived from the normalized project brief.",
            stakeholders=stakeholders,
            functional_requirements=functional_requirements,
            non_functional_requirements=non_functional_requirements,
            assumptions=assumptions,
            missing_information=project_brief["ambiguities"] + project_brief["clarification_questions"],
            grouped_modules=grouped_modules,
        )

    def _split_feature_candidates(self, features: list[str]) -> tuple[list[str], list[str]]:
        """Separate workflow features from implementation or scope constraints."""
        functional_features: list[str] = []
        derived_constraints: list[str] = []
        constraint_markers = (
            "web-based",
            "web based",
            "run locally",
            "local demo",
            "phased",
            "scope",
            "privacy",
            "security",
            "usability",
            "reliability",
            "manageable scope",
        )
        for feature in features:
            lowered = feature.lower()
            if any(marker in lowered for marker in constraint_markers):
                derived_constraints.append(feature)
            else:
                functional_features.append(feature)

        if not functional_features and features:
            functional_features.append(features[0])
            derived_constraints.extend(features[1:])

        return functional_features, dedupe_strings(derived_constraints)

    def _build_functional_requirements(self, features: list[str]) -> list[RequirementItem]:
        """Build deterministic functional requirement items."""
        items: list[RequirementItem] = []
        base_features = features or ["Support the core workflow described in the project brief."]
        for index, feature in enumerate(base_features, start=1):
            items.append(
                RequirementItem(
                    requirement_id=f"FR-{index:03d}",
                    title=f"Functional Requirement {index}",
                    description=feature,
                    priority="high" if index <= 2 else "medium",
                    source="project_brief.requested_features",
                )
            )
        return items

    def _build_non_functional_requirements(self, constraints: list[str], project_domain: str) -> list[RequirementItem]:
        """Build deterministic non-functional requirement items."""
        base_items = [
            "The system should produce readable structured outputs for project planning.",
            "The system should keep execution local and assignment-demo friendly.",
            "The system should preserve traceability through structured logging.",
        ]
        if project_domain != "unknown":
            base_items.append(f"The solution should remain appropriate for the {project_domain} domain context.")
        base_items.extend([f"The system should satisfy this explicit constraint: {item}." for item in constraints])
        unique_items = dedupe_strings(base_items)

        output: list[RequirementItem] = []
        for index, description in enumerate(unique_items, start=1):
            output.append(
                RequirementItem(
                    requirement_id=f"NFR-{index:03d}",
                    title=f"Non-Functional Requirement {index}",
                    description=description,
                    priority="high" if index <= 2 else "medium",
                    source="project_brief.constraints" if "explicit constraint" in description else "baseline_quality_rules",
                )
            )
        return output

    def _build_assumptions(self, project_brief: ProjectBrief) -> list[str]:
        """List assumptions separately from confirmed requirements."""
        assumptions = [
            "Current planning behavior is primarily rule-based and deterministic.",
            "Live Ollama prompting can be added later without changing the state contract.",
        ]
        if not project_brief["requested_features"]:
            assumptions.append("Core features will need confirmation from the user.")
        if project_brief["project_domain"] == "unknown":
            assumptions.append("Domain-specific rules cannot be specialized until the domain is clarified.")
        return dedupe_strings(assumptions)

    def _build_modules(self, functional_requirements: list[RequirementItem]) -> list[ModuleItem]:
        """Group requirements into readable modules using stable keyword buckets."""
        buckets = [
            ("Catalog and Submission Management", "Supports browsing, submission, registration, and record update workflows."),
            ("Review and Oversight", "Supports approvals, feedback, monitoring, and reporting responsibilities."),
            ("Administration and Configuration", "Supports roles, schedules, academic periods, and operational setup."),
        ]
        grouped_ids: list[list[str]] = [[], [], []]

        for item in functional_requirements:
            lowered = item["description"].lower()
            if any(keyword in lowered for keyword in ("approve", "review", "feedback", "report", "monitor", "summary")):
                grouped_ids[1].append(item["requirement_id"])
            elif any(keyword in lowered for keyword in ("role", "period", "schedule", "classroom", "group", "term")):
                grouped_ids[2].append(item["requirement_id"])
            else:
                grouped_ids[0].append(item["requirement_id"])

        modules: list[ModuleItem] = []
        for index, ((name, description), requirement_ids) in enumerate(zip(buckets, grouped_ids), start=1):
            if requirement_ids:
                modules.append(
                    ModuleItem(
                        module_id=f"MOD-{index:03d}",
                        name=name,
                        description=description,
                        requirement_ids=requirement_ids,
                    )
                )
        return modules
