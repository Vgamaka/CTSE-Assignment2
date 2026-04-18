"""Deterministic checker for plan consistency and delivery risks."""

from __future__ import annotations

from dataclasses import dataclass

from graph.state import DeliveryPlan, RequirementsSpec, RiskReport
from utils.helpers import dedupe_strings


@dataclass(slots=True)
class ConsistencyRiskCheckerTool:
    """Check requirement coverage, ambiguity, and unsupported assumptions."""

    # Suggested ownership: student responsible for review rules,
    # validation coverage, and risk-oriented quality checks.
    enable_llm_hook: bool = False

    def run(self, requirements_spec: RequirementsSpec, delivery_plan: DeliveryPlan) -> RiskReport:
        """Return structured review results from deterministic coverage checks."""
        # TODO: blend these rule checks with local Ollama critique once a
        # stable review prompt has been tested against sample briefs.
        missing_mappings = self._find_missing_requirement_mappings(requirements_spec, delivery_plan)
        ambiguous_items = self._find_ambiguous_items(requirements_spec)
        unsupported_assumptions = self._find_unsupported_assumptions(requirements_spec, delivery_plan)
        incomplete_module_coverage = self._find_incomplete_module_coverage(requirements_spec, delivery_plan)
        missing_user_story_coverage = self._find_missing_user_story_coverage(requirements_spec, delivery_plan)
        validation_notes = self._build_validation_notes(
            missing_mappings=missing_mappings,
            ambiguous_items=ambiguous_items,
            technical_task_count=len(delivery_plan["technical_tasks"]),
        )

        gaps = dedupe_strings(
            missing_mappings
            + incomplete_module_coverage
            + missing_user_story_coverage
        )
        risks = [
            "Unmapped requirements can lead to incomplete implementation planning." if missing_mappings else "",
            "Ambiguous items may cause rework during later SDLC phases." if ambiguous_items else "",
            "Unsupported assumptions may reduce plan reliability." if unsupported_assumptions else "",
        ]
        risks = [item for item in risks if item]

        severe_ambiguity = bool(ambiguous_items or missing_mappings)
        review_status = "needs_clarification" if severe_ambiguity else "approved"

        return RiskReport(
            gaps=gaps,
            risks=risks,
            validation_notes=validation_notes,
            missing_mappings=missing_mappings,
            ambiguous_items=ambiguous_items,
            unsupported_assumptions=unsupported_assumptions,
            incomplete_module_coverage=incomplete_module_coverage,
            missing_user_story_coverage=missing_user_story_coverage,
            review_status=review_status,
            recommendation="loop_to_intake" if severe_ambiguity else "finalize",
            severe_ambiguity=severe_ambiguity,
        )
        
    def _find_missing_requirement_mappings(self, requirements_spec: RequirementsSpec, delivery_plan: DeliveryPlan) -> list[str]:
        """Check whether every functional requirement is covered by a task."""
        mapped_ids = {
            requirement_id
            for task in delivery_plan["technical_tasks"]
            for requirement_id in task["requirement_ids"]
        }
        issues: list[str] = []
        for requirement in requirements_spec["functional_requirements"]:
            if requirement["requirement_id"] not in mapped_ids:
                issues.append(f"Requirement {requirement['requirement_id']} is not mapped to any technical task.")
        return issues

    def _find_ambiguous_items(self, requirements_spec: RequirementsSpec) -> list[str]:
        """Flag vague items from the missing-information section."""
        vague_markers = ("unclear", "unknown", "not clearly", "not explicitly", "need confirmation", "missing")
        items: list[str] = []
        for item in requirements_spec["missing_information"]:
            lowered = item.lower()
            if any(marker in lowered for marker in vague_markers):
                items.append(item)
        return dedupe_strings(items)

    def _find_unsupported_assumptions(self, requirements_spec: RequirementsSpec, delivery_plan: DeliveryPlan) -> list[str]:
        """Mark assumptions that do not seem reflected in modules or tasks."""
        coverage_text = " ".join(
            [module["name"] + " " + module["description"] for module in delivery_plan["modules"]]
            + [task["title"] + " " + task["description"] for task in delivery_plan["technical_tasks"]]
        ).lower()
        issues: list[str] = []
        baseline_assumption_markers = (
            "rule-based and deterministic",
            "live ollama prompting can be added later",
        )
        for assumption in requirements_spec["assumptions"]:
            if any(marker in assumption.lower() for marker in baseline_assumption_markers):
                continue
            keywords = [word.lower() for word in assumption.split() if len(word) > 5]
            if keywords and not any(keyword in coverage_text for keyword in keywords):
                issues.append(f"Assumption may need explicit planning support: {assumption}")
        return dedupe_strings(issues)

    def _find_incomplete_module_coverage(self, requirements_spec: RequirementsSpec, delivery_plan: DeliveryPlan) -> list[str]:
        """Check whether grouped modules actually cover assigned requirement IDs."""
        module_map = {module["module_id"]: module for module in delivery_plan["modules"]}
        issues: list[str] = []
        for requirement in requirements_spec["functional_requirements"]:
            expected = [
                module["module_id"]
                for module in requirements_spec["grouped_modules"]
                if requirement["requirement_id"] in module["requirement_ids"]
            ]
            if expected and not all(module_id in module_map for module_id in expected):
                issues.append(f"Module coverage is incomplete for requirement {requirement['requirement_id']}.")
        return dedupe_strings(issues)

    def _find_missing_user_story_coverage(self, requirements_spec: RequirementsSpec, delivery_plan: DeliveryPlan) -> list[str]:
        """Check whether functional requirements have linked user stories."""
        mapped_ids = {
            requirement_id
            for story in delivery_plan["user_stories"]
            for requirement_id in story["linked_requirement_ids"]
        }
        issues: list[str] = []
        for requirement in requirements_spec["functional_requirements"]:
            if requirement["requirement_id"] not in mapped_ids:
                issues.append(f"Requirement {requirement['requirement_id']} is missing user story coverage.")
        return issues

    def _build_validation_notes(
        self,
        *,
        missing_mappings: list[str],
        ambiguous_items: list[str],
        technical_task_count: int,
    ) -> list[str]:
        """Create deterministic validation guidance for the final report."""
        notes = [
            f"Demonstrate at least one end-to-end walkthrough using the {technical_task_count}-task delivery plan.",
            "Review the generated plan with a lecturer or teammate before treating it as final implementation scope.",
        ]
        if missing_mappings:
            notes.append("Check requirement-to-task mapping before implementation begins.")
        if ambiguous_items:
            notes.append("Resolve ambiguous items before detailed implementation or estimation.")
        return dedupe_strings(notes)
