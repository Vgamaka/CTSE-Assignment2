# Demo Plan

## Recommended Demo Scenario

Use the smart campus portal scenario:

- [sample_inputs/smart_campus_portal.txt](/Users/ira/Documents/Playground/sample_inputs/smart_campus_portal.txt)

Why this scenario is best:

- it is easy for lecturers to understand immediately
- it naturally involves multiple stakeholders
- it produces a strong mix of requirements, tasks, modules, and review notes
- it is stable and does not depend on any network access

## Exact Commands

Setup if needed:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the workflow:

```bash
.venv/bin/python main.py --input-file sample_inputs/smart_campus_portal.txt
```

Run the tests:

```bash
.venv/bin/pytest -q
```

## What Should Happen

After running the workflow:

1. The terminal should print that workflow execution finished.
2. A status line should show `finalized`.
3. The terminal should print the saved paths for:
   - Markdown output
   - JSON snapshot
   - JSONL trace log

## Which Generated Files to Show

Show the generated Markdown plan first:

- newest file in `outputs/plan_*.md`

Point out these sections:

- `Project Overview`
- `Stakeholders and Users`
- `Functional Requirements`
- `Suggested Modules`
- `Task Breakdown`
- `Risks and Validation Notes`
- `Recommended Development Phases`

Then show the JSON state snapshot:

- newest file in `outputs/state_*.json`

Explain that it is the full machine-readable shared state used across the workflow.

## What to Show From Logs

Open the newest trace file in `logs/trace_*.jsonl`.

Explain that each step records:

- `timestamp`
- `agent`
- `status`
- `input_summary`
- `output_summary`
- `updated_fields`

This helps demonstrate observability and makes the multi-agent pipeline easier to debug.

## What to Show From Tests

Run:

```bash
.venv/bin/pytest -q
```

Explain that the test suite covers:

- full system flow
- intake handling
- requirements generation
- task planning
- review/risk checking

## Suggested 4-5 Minute Talk Track

Opening:

- “This project is a fully local multi-agent SDLC planning assistant built for a university assignment.”

Architecture:

- “The system uses four LangGraph agents. Intake structures the raw idea, Requirements builds FRs and NFRs, Planner creates user stories and tasks, and Review checks consistency before finalizing.”

State:

- “All agents share one typed workflow state, which makes the pipeline easy to trace and test.”

Observability:

- “Each step writes structured JSONL logs, so we can explain exactly what each agent changed.”

Output:

- “The final result is both human-readable Markdown for a report/demo and structured JSON for later testing.”

Team roles:

- “Each student owns one agent, one tool, and one testing area, so responsibilities are clear for the report and viva.”

Close:

- “The project is intentionally deterministic and local-first, so it stays stable during demonstration and does not depend on paid APIs.”
