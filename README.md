Here’s your **final README (clean, ready-to-copy, no extra formatting issues)**:

---

```markdown
# Local Multi-Agent SDLC Planning Assistant

## Project Overview

This project is a fully local multi-agent system for software project planning. A rough software idea is passed through four LangGraph agents that progressively transform it into a structured SDLC plan.

The system is designed for:
- university assignment demonstration
- local execution (no cloud dependency)
- deterministic and testable outputs
- future extensibility with local LLMs (Ollama)

---

## What the System Produces

- Normalized project brief  
- Functional and non-functional requirements  
- User stories, modules, tasks, and phases  
- Risk analysis and validation report  
- Final Markdown SDLC report  
- JSON snapshot of full workflow state  
- JSONL execution trace logs  

---

## Architecture Summary

The system uses a 4-agent LangGraph workflow:

1. `intake_agent`  
2. `requirements_agent`  
3. `planner_agent`  
4. `review_agent`  

Workflow:

Input → Intake → Requirements → Planner → Review → Output  
                                             ↑  
                                     (loop if ambiguity)

- Shared global state across all agents  
- Conditional routing handled by Review Agent  
- Fully local execution  

---

## Project Structure

```

.
├── agents/          # Agent implementations
├── tools/           # Custom tools
├── graph/           # Workflow + state management
├── config/          # Prompts + settings
├── utils/           # Helpers + logging
├── ui/              # Flask demo UI
├── tests/           # Evaluation tests
├── sample_inputs/   # Demo inputs
├── outputs/         # Generated outputs
├── logs/            # Execution logs
├── main.py          # CLI entry point

````

---

## Setup Instructions

### Requirements
- Python 3.11+
- Git
- Optional: Ollama (for future LLM integration)

---

### Clone Repository

```bash
git clone https://github.com/Vgamaka/CTSE-Assignment2.git
cd CTSE-Assignment2
````

---

### Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# OR
.venv\Scripts\activate      # Windows
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Optional: Install Ollama

Install from: [https://ollama.com](https://ollama.com)

Run:

```bash
ollama run llama3
```

Note: The system works fully without Ollama.

---

## How to Run

### CLI Mode

```bash
python main.py --text "Build a student management system"
```

OR

```bash
python main.py --input-file sample_inputs/smart_campus_portal.txt
```

---

### UI Mode (Recommended for Demo)

```bash
python -m ui.app
```

Open:

```
http://127.0.0.1:5000
```

---

### Run Tests

```bash
pytest
```

---

## How the System Works

### Agents

**Intake Agent**

* Extracts domain, stakeholders, features
* Identifies ambiguities

**Requirements Agent**

* Generates structured requirements
* Separates functional and non-functional requirements

**Planner Agent**

* Creates user stories and technical tasks
* Defines dependencies and phases

**Review Agent**

* Detects risks and missing mappings
* Decides whether to finalize or loop back

---

## Tools

| Tool                       | Purpose                   |
| -------------------------- | ------------------------- |
| Project Brief Normalizer   | Extract structured input  |
| Requirements Formatter     | Generate requirements     |
| Task Breakdown Generator   | Create planning structure |
| Consistency & Risk Checker | Validate plan             |
| File Exporter              | Save outputs              |

---

## State Management

All agents share a single `WorkflowState`.

Key fields:

* project_brief
* requirements_spec
* delivery_plan
* risk_report
* final_output
* tool_history
* agent_trace
* status

This ensures:

* no context loss
* deterministic workflow
* easy testing

---

## Observability

Logs are stored as JSONL:

```
logs/trace_<run_id>.jsonl
```

Each log contains:

* agent name
* status
* input summary
* output summary
* updated fields

---

## Outputs

Generated automatically:

```
outputs/plan_<run_id>.md
outputs/state_<run_id>.json
logs/trace_<run_id>.jsonl
```

---

## Testing

We use pytest for evaluation.

Validations include:

* requirement generation
* task mapping
* risk detection
* ambiguity handling

Run:

```bash
pytest
```

---

## Common Issues & Fixes

### ModuleNotFoundError

Use:

```bash
python -m ui.app
```

NOT:

```bash
python ui/app.py
```

---

### UI not loading

* Activate virtual environment
* Install dependencies

---

### Ollama issues

Disable in:

```python
enable_live_model = False
```

---

## Future Improvements

* Full Ollama-based reasoning
* Better domain detection
* Output scoring system
* Effort estimation
* Additional export formats

---

## Team Contributions

* Peiris P G V (IT22364388) – Intake Agent, File Exporter Tool, UI, Testing
* Kulathunga K A K M (IT22915740) – Pending
* Dissanayake E G M (IT22342744) – Pending
* Gunarathne M D C H (IT22306104) – Pending

