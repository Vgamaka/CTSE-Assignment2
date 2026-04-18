"""Deterministic generator for user stories and technical tasks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
from graph.state import DeliveryPlan, ModuleItem, RequirementsSpec, RoadmapPhase, TaskItem, UserStoryItem


@dataclass(slots=True)
class TaskBreakdownGeneratorTool:
    """Map requirements into implementation-oriented planning structures."""

    # Suggested ownership: student responsible for task planning logic,
    # dependency modeling, and phased roadmap generation.
    enable_llm_hook: bool = False

    def run(self, requirements_spec: RequirementsSpec) -> DeliveryPlan:
        """Produce a stable delivery plan from the requirements specification."""
        # TODO: upgrade task decomposition with stronger local reasoning while
        # preserving deterministic IDs and testable structure.
        modules = requirements_spec["grouped_modules"]
        functional_requirements = requirements_spec["functional_requirements"]
        stakeholders = requirements_spec["stakeholders"] or ["User"]

        user_stories = self._build_user_stories(functional_requirements, stakeholders)
        technical_tasks = self._build_tasks(functional_requirements, modules)
        priorities = {task["task_id"]: task["priority"] for task in technical_tasks}
        dependencies = {task["task_id"]: task["dependencies"] for task in technical_tasks}
        phased_roadmap = self._build_roadmap(technical_tasks)

        return DeliveryPlan(
            user_stories=user_stories,
            modules=modules,
            technical_tasks=technical_tasks,
            priorities=priorities,
            dependencies=dependencies,
            phased_roadmap=phased_roadmap,
        )

    def _build_user_stories(
        self,
        functional_requirements: list[dict[str, str]],
        stakeholders: list[str],
    ) -> list[UserStoryItem]:
        """Create simple user stories linked to requirement IDs."""
        stories: list[UserStoryItem] = []
        for index, requirement in enumerate(functional_requirements, start=1):
            stories.append(
                UserStoryItem(
                    story_id=f"US-{index:03d}",
                    role=self._role_for_requirement(requirement["description"], stakeholders),
                    goal=self._goal_for_requirement(requirement["description"]),
                    benefit="the project plan addresses a concrete user need",
                    linked_requirement_ids=[requirement["requirement_id"]],
                )
            )
        return stories

    def _build_tasks(
        self,
        functional_requirements: list[dict[str, str]],
        modules: list[ModuleItem],
    ) -> list[TaskItem]:
        """Create deterministic technical tasks with dependencies and phase labels."""
        tasks: list[TaskItem] = []
        phase_labels = ["Phase 1 - Foundation", "Phase 2 - Core Build", "Phase 3 - Review and Refinement"]

        for index, requirement in enumerate(functional_requirements, start=1):
            module = self._module_for_requirement(requirement["requirement_id"], modules)
            task_id = f"TASK-{index:03d}"
            tasks.append(
                TaskItem(
                    task_id=task_id,
                    title=self._task_title_for_requirement(requirement["description"]),
                    description=f"Build and validate support for requirement {requirement['requirement_id']}: {requirement['description']}",
                    module_id=module["module_id"] if module else "MOD-UNASSIGNED",
                    requirement_ids=[requirement["requirement_id"]],
                    priority=requirement["priority"],
                    dependencies=[] if index == 1 else [f"TASK-{index - 1:03d}"],
                    phase=phase_labels[min(index - 1, len(phase_labels) - 1)],
                )
            )
        return tasks

    def _build_roadmap(self, technical_tasks: list[TaskItem]) -> list[RoadmapPhase]:
        """Group task IDs by phase label."""
        grouped: dict[str, list[str]] = {}
        for task in technical_tasks:
            grouped.setdefault(task["phase"], []).append(task["task_id"])

        roadmap: list[RoadmapPhase] = []
        for phase_label, task_ids in grouped.items():
            roadmap.append(
                RoadmapPhase(
                    phase_label=phase_label,
                    goals=[f"Complete tasks assigned to {phase_label}."],
                    task_ids=task_ids,
                )
            )
        return roadmap

    def _module_for_requirement(self, requirement_id: str, modules: list[ModuleItem]) -> ModuleItem | None:
        """Find the first module mapped to a given requirement."""
        for module in modules:
            if requirement_id in module["requirement_ids"]:
                return module
        return None

    def _role_for_requirement(self, description: str, stakeholders: list[str]) -> str:
        """Choose the most relevant stakeholder role for a requirement."""
        lowered = description.lower()
        role_hints = [
            ("club admin", "Club Administrators"),
            ("members", "Members"),
            ("member", "Members"),
            ("lecturers", "Lecturers"),
            ("lecturer", "Lecturers"),
            ("students", "Students"),
            ("student", "Students"),
            ("parents", "Parents"),
            ("parent", "Parents"),
            ("teachers", "Teachers"),
            ("teacher", "Teachers"),
            ("records staff", "Records Staff"),
            ("supervisors", "Supervisors"),
            ("admin staff", "Administrators"),
        ]
        for phrase, role in role_hints:
            if lowered.startswith(phrase):
                return role if role in stakeholders or not stakeholders else role
        for stakeholder in stakeholders:
            singular = stakeholder.lower().rstrip("s")
            if stakeholder.lower() in lowered or singular in lowered:
                return stakeholder
        return stakeholders[0] if stakeholders else "User"

    def _goal_for_requirement(self, description: str) -> str:
        """Convert requirement wording into a cleaner user-story goal."""
        lowered = description.lower()
        for prefix in (
            "it should let ",
            "the system should let ",
            "should let ",
            "teachers should be able to ",
            "parents should be able to ",
            "lecturers should be able to ",
            "club admins should be able to ",
            "members should be able to ",
            "supervisors should be able to ",
        ):
            if lowered.startswith(prefix):
                cleaned = description[len(prefix):]
                return self._strip_leading_actor_phrase(cleaned)
        return self._strip_leading_actor_phrase(description)

    def _task_title_for_requirement(self, description: str) -> str:
        """Create a readable task title from a requirement description."""
        cleaned = self._goal_for_requirement(description).strip().rstrip(".")
        title = " ".join(cleaned.split()[:5]).title()
        return f"Implement {title}"

    def _strip_leading_actor_phrase(self, text: str) -> str:
        """Remove repeated actor phrases after the role has already been identified."""
        lowered = text.lower().strip()
        actor_prefixes = (
            "students ",
            "lecturers ",
            "teachers ",
            "parents ",
            "members ",
            "club admins ",
            "supervisors ",
            "records staff ",
            "admin staff ",
        )
        for prefix in actor_prefixes:
            if lowered.startswith(prefix):
                return text[len(prefix):]
        return text
