# Local Multi-Agent SDLC Planning Assistant

## Project Overview

This project is a fully local university assignment system for software project planning. A rough software idea is passed through four LangGraph agents that progressively turn it into a structured engineering plan. The implementation is intentionally assignment-friendly: deterministic where possible, readable for student collaboration, and ready for stronger local Ollama reasoning in later iterations.

The current project produces:

- a normalized project brief
- structured requirements
- a delivery plan with user stories, modules, tasks, and phases
- a review report with risks and coverage gaps
- a final Markdown report
- a machine-readable JSON snapshot of the whole shared state
- a JSONL execution trace

## Architecture Summary

The system uses exactly four agents connected in a LangGraph workflow:

1. `intake_agent`
2. `requirements_agent`
3. `planner_agent`
4. `review_agent`

The workflow is mostly linear, but the review stage can route back to intake once if severe ambiguity is detected. This keeps the orchestration simple enough for a terminal demo while still showing multi-agent coordination and conditional routing.

## File Structure

```text
.
├── README.md
├── requirements.txt
├── main.py
├── agents/
│   ├── intake_agent.py
│   ├── requirements_agent.py
│   ├── planner_agent.py
│   └── review_agent.py
├── config/
│   ├── prompts.py
│   └── settings.py
├── graph/
│   ├── routing.py
│   ├── state.py
│   └── workflow.py
├── logs/
├── outputs/
├── sample_inputs/
│   ├── insurance_archiving.txt
│   ├── nursery_app.txt
│   ├── event_system.txt
│   └── smart_campus_portal.txt
├── tests/
│   ├── conftest.py
│   ├── test_system_flow.py
│   ├── test_intake_agent.py
│   ├── test_requirements_agent.py
│   ├── test_planner_agent.py
│   └── test_review_agent.py
├── tools/
│   ├── brief_normalizer.py
│   ├── requirements_formatter.py
│   ├── task_breakdown.py
│   └── consistency_checker.py
└── utils/
    ├── file_io.py
    ├── helpers.py
    └── logger.py
```

## Setup Instructions

Requirements:

- Python 3.11+
- Optional: Ollama for future local model integration

Recommended setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Instructions

Direct text input:

```bash
python main.py --text "Build a local planning assistant for software project proposals."
```

Sample input file:

```bash
python main.py --input-file sample_inputs/insurance_archiving.txt
```

Other example inputs:

```bash
python main.py --input-file sample_inputs/nursery_app.txt
python main.py --input-file sample_inputs/event_system.txt
python main.py --input-file sample_inputs/smart_campus_portal.txt
```

## Frontend Demo UI

A lightweight local Flask UI is included for demo clarity. It does not replace the backend workflow. It simply calls the existing backend functions and visualizes:

- project input
- the 4 agents and their tools
- shared state flow across the workflow
- final Markdown output
- recent trace/log events
- saved output file paths

Run the UI:

```bash
python ui/app.py
```

Or with the local virtual environment:

```bash
.venv/bin/python ui/app.py
```

Then open:

```text
http://127.0.0.1:5000
```

Generated artifacts are saved automatically to:

- `outputs/plan_<run_id>.md`
- `outputs/state_<run_id>.json`
- `logs/trace_<run_id>.jsonl`

## Test Instructions

Run all tests:

```bash
pytest
```

Run with the local virtual environment:

```bash
.venv/bin/pytest
```

The tests are deterministic and do not require network access or a running Ollama server.

Additional team handoff documents:

- [CONTRIBUTIONS.md](/Users/ira/Documents/Playground/CONTRIBUTIONS.md)
- [DEMO.md](/Users/ira/Documents/Playground/DEMO.md)

## Explanation of Agents

`intake_agent`

- reads raw user input from shared state
- identifies domain, stakeholders, requested features, constraints, and ambiguities
- writes the normalized `project_brief`

`requirements_agent`

- reads `project_brief`
- creates functional requirements, non-functional requirements, assumptions, missing information, and grouped modules
- writes `requirements_spec`

`planner_agent`

- reads `requirements_spec`
- generates user stories, suggested modules, technical tasks, priorities, dependencies, and roadmap phases
- writes `delivery_plan`

`review_agent`

- reads `requirements_spec` and `delivery_plan`
- checks missing mappings, vague items, unsupported assumptions, and incomplete coverage
- writes `risk_report`
- creates final Markdown when the plan is acceptable

## Explanation of Tools

`Project Brief Normalizer Tool`

- converts rough input text into a structured project brief
- handles empty and vague input safely

`Requirements Formatter Tool`

- creates deterministic `FR-*` and `NFR-*` IDs
- separates assumptions from confirmed requirements

`Task Breakdown Generator Tool`

- maps requirements to user stories, tasks, dependencies, and phases
- stays deterministic enough for testing

`Consistency & Risk Checker Tool`

- checks requirement-to-task mapping
- checks vague items and unsupported assumptions
- checks module and user story coverage

## State Management Explanation

The entire workflow shares one `WorkflowState` object defined in `graph/state.py`. This state stores both raw input and every generated planning artifact. The state includes:

- `raw_user_input`
- `project_domain`
- `stakeholders`
- `requested_features`
- `constraints`
- `clarification_questions`
- `project_brief`
- `requirements_spec`
- `delivery_plan`
- `risk_report`
- `final_output`
- `tool_history`
- `agent_trace`
- `errors`
- `status`

This makes the system easy to test because each stage reads from known fields and writes predictable updates back into the same structure.

## Observability and Logging Explanation

Execution traces are written as JSONL files through `utils/logger.py`. Each log event includes:

- `timestamp`
- `agent`
- `status`
- `input_summary`
- `output_summary`
- `updated_fields`

The summaries are intentionally bounded so the logs remain readable in a terminal demo. The logger records system-level events such as run start and completion, along with per-agent step logs.

## Assignment-Friendly Output Structure

The final Markdown output is organized into the following sections:

- `Project Overview`
- `Stakeholders and Users`
- `Functional Requirements`
- `Non-Functional Requirements`
- `Assumptions and Missing Details`
- `Suggested Modules`
- `User Stories`
- `Task Breakdown`
- `Risks and Validation Notes`
- `Recommended Development Phases`

The JSON output is a machine-readable state snapshot that keeps nested structures intact for later testing and validation.

## Limitations and Future Improvements

Current limitations:

- the reasoning is primarily rule-based rather than fully LLM-driven
- domain detection and feature extraction use simple heuristics
- review quality is only as strong as the deterministic coverage checks

Reasonable future improvements:

- integrate stronger local Ollama prompting behind the existing tool interfaces
- improve domain-specific extraction rules for more project types
- add richer validation metrics and output scoring
- expand roadmap generation with effort estimates and milestones
- add optional export formats beyond Markdown and JSON

## Notes on Team Contribution

Several files now include short ownership comments so different students can divide work more clearly across configuration, graph orchestration, agents, and tools. This is meant to make collaboration easier without changing the code structure itself.
