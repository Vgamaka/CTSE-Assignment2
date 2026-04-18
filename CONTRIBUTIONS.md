# Team Ownership Guide

This document turns the repository into a clear 4-student handoff structure for implementation, testing, demo preparation, and report writing.

## Ownership Summary

Each student should own:

- one agent
- one tool
- one testing responsibility

The goal is not strict isolation. The goal is clear accountability so each teammate can confidently explain one major part of the system during the demo and viva.

## Student 1

Focus:

- foundation
- Intake Agent
- Project Brief Normalizer Tool
- workflow and logging

Owned files:

- [main.py](/Users/ira/Documents/Playground/main.py)
- [graph/workflow.py](/Users/ira/Documents/Playground/graph/workflow.py)
- [graph/routing.py](/Users/ira/Documents/Playground/graph/routing.py)
- [graph/state.py](/Users/ira/Documents/Playground/graph/state.py)
- [utils/logger.py](/Users/ira/Documents/Playground/utils/logger.py)
- [utils/file_io.py](/Users/ira/Documents/Playground/utils/file_io.py)
- [agents/intake_agent.py](/Users/ira/Documents/Playground/agents/intake_agent.py)
- [tools/brief_normalizer.py](/Users/ira/Documents/Playground/tools/brief_normalizer.py)
- [tests/test_intake_agent.py](/Users/ira/Documents/Playground/tests/test_intake_agent.py)
- [tests/test_system_flow.py](/Users/ira/Documents/Playground/tests/test_system_flow.py)

Responsibilities:

- explain the shared state lifecycle
- explain how raw user input enters the system
- explain how JSONL logs are written
- explain conditional routing from review back to intake
- maintain CLI stability and output persistence

Suggested branch name:

- `student1-foundation-intake`

Suggested milestone tasks:

- keep startup and file output flow reliable
- improve intake extraction heuristics safely
- maintain logging readability and trace quality
- validate that end-to-end system flow stays stable

Student 1 should be able to explain:

- why LangGraph is used
- how the workflow starts and ends
- what intake adds to the shared state
- how observability supports debugging and demo confidence

## Student 2

Focus:

- Requirements Agent
- Requirements Formatter Tool

Owned files:

- [agents/requirements_agent.py](/Users/ira/Documents/Playground/agents/requirements_agent.py)
- [tools/requirements_formatter.py](/Users/ira/Documents/Playground/tools/requirements_formatter.py)
- [config/prompts.py](/Users/ira/Documents/Playground/config/prompts.py)
- [tests/test_requirements_agent.py](/Users/ira/Documents/Playground/tests/test_requirements_agent.py)

Responsibilities:

- maintain deterministic FR and NFR generation
- keep assumptions separate from confirmed requirements
- improve grouped module quality carefully
- preserve readable requirement output for report use

Suggested branch name:

- `student2-requirements`

Suggested milestone tasks:

- refine requirement phrasing
- improve separation between functional needs and constraints
- keep IDs stable and test-friendly
- improve requirement grouping for better plans

Student 2 should be able to explain:

- how FR and NFR IDs are generated
- how assumptions are separated from requirements
- how modules are derived from the normalized brief
- why deterministic formatting is useful for testing

## Student 3

Focus:

- Task Planner Agent
- Task Breakdown Generator Tool

Owned files:

- [agents/planner_agent.py](/Users/ira/Documents/Playground/agents/planner_agent.py)
- [tools/task_breakdown.py](/Users/ira/Documents/Playground/tools/task_breakdown.py)
- [tests/test_planner_agent.py](/Users/ira/Documents/Playground/tests/test_planner_agent.py)

Responsibilities:

- map requirements into user stories and tasks
- keep priorities and dependencies readable
- keep roadmap phases simple and explainable
- improve planning specificity without breaking determinism

Suggested branch name:

- `student3-planner`

Suggested milestone tasks:

- improve task titles and dependency rules
- improve stakeholder-to-user-story role mapping
- keep roadmap phases clean for presentation
- validate requirement-to-task coverage

Student 3 should be able to explain:

- how requirements are converted into implementation tasks
- how priorities and dependencies are assigned
- how roadmap phases are built
- why user stories help connect planning output to stakeholders

## Student 4

Focus:

- Review Agent
- Consistency & Risk Checker Tool
- review-focused testing

Owned files:

- [agents/review_agent.py](/Users/ira/Documents/Playground/agents/review_agent.py)
- [tools/consistency_checker.py](/Users/ira/Documents/Playground/tools/consistency_checker.py)
- [utils/helpers.py](/Users/ira/Documents/Playground/utils/helpers.py)
- [tests/test_review_agent.py](/Users/ira/Documents/Playground/tests/test_review_agent.py)

Responsibilities:

- maintain review quality and final report quality
- detect missing mappings and ambiguity consistently
- improve validation notes and risk reporting
- keep final Markdown sections submission-friendly

Suggested branch name:

- `student4-review-risk`

Suggested milestone tasks:

- improve risk explanations without making them generic
- refine validation notes for demo/report use
- keep review outputs professional and readable
- maintain final Markdown structure and consistency

Student 4 should be able to explain:

- how the review stage decides whether the plan is ready
- how missing mappings and ambiguity are detected
- how final Markdown is assembled
- what unresolved risks still mean for a project plan

## Shared Team Expectations

- run `.venv/bin/pytest -q` before handing work to another teammate
- do not change output structure casually because tests and demo flow depend on it
- keep changes deterministic and readable
- prefer small safe improvements over ambitious rewrites
- update README, DEMO, and sample outputs when presentation-facing behavior changes

## Demo and Report Preparation

Before the final submission, each student should prepare:

- one short code walkthrough of their owned files
- one explanation of a design decision in their area
- one example of how their area is tested
- one example of how their area contributes to the final generated plan
