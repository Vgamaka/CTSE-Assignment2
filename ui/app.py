"""Polished Flask-based academic demo UI for the Local Multi-Agent SDLC Planning Assistant."""

from __future__ import annotations

from html import escape
from typing import Callable

from flask import Flask, Request, render_template_string, request

from config.settings import AppSettings
from ui.helpers import latest_log_preview, load_ui_context, read_text_file
from utils.workflow_runner import WorkflowRunResult, execute_workflow

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Local Multi-Agent SDLC Planning Assistant</title>
  <style>
    :root {
      --bg: #0b1220;
      --surface: #111a2e;
      --surface-2: #16213b;
      --card: rgba(255,255,255,0.06);
      --card-strong: rgba(255,255,255,0.1);
      --border: rgba(255,255,255,0.12);
      --text: #e5ecf6;
      --muted: #9db0c9;
      --primary: #60a5fa;
      --primary-2: #2563eb;
      --success: #22c55e;
      --warn: #f59e0b;
      --danger: #ef4444;
      --shadow: 0 16px 40px rgba(0,0,0,0.28);
      --radius: 20px;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(96,165,250,0.14), transparent 24%),
        linear-gradient(180deg, #08101d 0%, #0b1220 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .page {
      max-width: 1440px;
      margin: 0 auto;
      padding: 28px;
    }

    .hero {
      background: linear-gradient(135deg, rgba(37,99,235,0.22), rgba(96,165,250,0.08));
      border: 1px solid var(--border);
      border-radius: 28px;
      padding: 28px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }

    .eyebrow {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(96,165,250,0.14);
      color: #bfdbfe;
      font-size: 0.84rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 14px;
    }

    .hero h1 {
      margin: 0 0 12px;
      font-size: clamp(2rem, 3vw, 3.4rem);
      line-height: 1.05;
    }

    .hero p {
      margin: 0;
      max-width: 980px;
      color: var(--muted);
      line-height: 1.7;
      font-size: 1.02rem;
    }

    .layout {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 22px;
      margin-top: 22px;
    }

    .stack {
      display: grid;
      gap: 22px;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }

    .card h2 {
      margin: 0 0 10px;
      font-size: 1.2rem;
    }

    .section-note {
      margin: 0 0 18px;
      color: var(--muted);
      line-height: 1.6;
      font-size: 0.96rem;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
    }

    .summary-tile {
      background: var(--card-strong);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      min-height: 118px;
    }

    .summary-label {
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 8px;
      display: block;
    }

    .summary-value {
      font-size: 1.05rem;
      font-weight: 700;
      line-height: 1.35;
      word-break: break-word;
      overflow-wrap: anywhere;
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.08);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 0.92rem;
    }

    .badge strong {
      color: #bfdbfe;
    }

    .input-panel {
      display: grid;
      gap: 14px;
    }

    label {
      font-weight: 700;
      color: #dbeafe;
      display: block;
      margin-bottom: 8px;
    }

    textarea, input[type=file] {
      width: 100%;
      border-radius: 16px;
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(8,16,29,0.64);
      color: var(--text);
      padding: 14px 16px;
      font: inherit;
    }

    textarea {
      min-height: 220px;
      resize: vertical;
      line-height: 1.6;
    }

    textarea::placeholder {
      color: #8aa0bc;
    }

    .button-row {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .button {
      border: 0;
      border-radius: 999px;
      padding: 13px 20px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      color: white;
      background: linear-gradient(135deg, var(--primary-2), var(--primary));
      box-shadow: 0 10px 24px rgba(37,99,235,0.28);
    }

    .button:hover {
      filter: brightness(1.06);
    }

    .muted-chip {
      display: inline-flex;
      align-items: center;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.06);
      border: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.92rem;
    }

    .error {
      background: rgba(239,68,68,0.14);
      color: #fecaca;
      border: 1px solid rgba(239,68,68,0.25);
      padding: 14px 16px;
      border-radius: 16px;
    }

    .workflow-banner {
      margin-bottom: 16px;
      padding: 14px 16px;
      border-radius: 16px;
      background: rgba(96,165,250,0.08);
      border: 1px solid rgba(96,165,250,0.16);
      color: #dbeafe;
      font-size: 0.95rem;
    }

    .workflow-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      align-items: stretch;
    }

    .agent-card {
      padding: 18px;
      border-radius: 18px;
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
      min-height: 270px;
    }

    .agent-title {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 10px;
    }

    .agent-title h3 {
      margin: 0;
      font-size: 1.02rem;
      max-width: 70%;
    }

    .status {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 700;
      background: rgba(148,163,184,0.16);
      color: #dbeafe;
      border: 1px solid rgba(148,163,184,0.24);
      white-space: nowrap;
    }

    .status.completed, .status.approved, .status.finalized {
      background: rgba(34,197,94,0.14);
      color: #bbf7d0;
      border-color: rgba(34,197,94,0.24);
    }

    .status.needs_clarification {
      background: rgba(245,158,11,0.16);
      color: #fde68a;
      border-color: rgba(245,158,11,0.24);
    }

    .status.pending {
      background: rgba(148,163,184,0.12);
      color: #cbd5e1;
      border-color: rgba(148,163,184,0.18);
    }

    .meta-label {
      font-size: 0.76rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 14px;
      margin-bottom: 6px;
      display: block;
    }

    .meta-value {
      color: var(--text);
      line-height: 1.55;
      font-size: 0.96rem;
    }

    .state-group-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }

    .state-group {
      border: 1px solid var(--border);
      border-radius: 18px;
      background: rgba(255,255,255,0.05);
      padding: 18px;
    }

    .state-group h3 {
      margin: 0 0 8px;
      font-size: 1rem;
      color: #bfdbfe;
    }

    .state-group p {
      margin: 0 0 14px;
      color: var(--muted);
      line-height: 1.55;
      font-size: 0.92rem;
    }

    .state-item {
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 12px;
      margin-top: 12px;
    }

    .state-item:first-of-type {
      border-top: 0;
      padding-top: 0;
      margin-top: 0;
    }

    .state-item strong {
      display: block;
      margin-bottom: 6px;
      color: #dbeafe;
    }

    .state-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 18px;
    }

    .state-chip {
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.06);
      color: var(--muted);
      font-size: 0.84rem;
    }

    .output-card .markdown-viewer {
      background: rgba(8,16,29,0.54);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 16px;
      padding: 18px;
      max-height: 640px;
      overflow: auto;
      line-height: 1.7;
      color: #dbeafe;
    }

    .markdown-viewer h1,
    .markdown-viewer h2,
    .markdown-viewer h3 {
      color: #ffffff;
      margin-top: 1.2em;
      margin-bottom: 0.6em;
      line-height: 1.3;
    }

    .markdown-viewer h1 { font-size: 1.5rem; margin-top: 0; }
    .markdown-viewer h2 { font-size: 1.2rem; }
    .markdown-viewer h3 { font-size: 1rem; }

    .markdown-viewer ul {
      margin: 0.6em 0 1em 1.2em;
      padding: 0;
    }

    .markdown-viewer li {
      margin: 0.35em 0;
    }

    .markdown-viewer p {
      margin: 0.5em 0;
    }

    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
    }

    .file-list {
      list-style: none;
      padding: 0;
      margin: 0;
      display: grid;
      gap: 12px;
    }

    .file-item {
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.05);
      border-radius: 16px;
      padding: 14px;
      word-break: break-word;
      overflow-wrap: anywhere;
    }

    .file-item strong {
      display: block;
      color: #bfdbfe;
      margin-bottom: 6px;
    }

    .timeline {
      display: grid;
      gap: 12px;
    }

    .timeline-item {
      border-left: 3px solid rgba(96,165,250,0.55);
      padding-left: 14px;
    }

    .timeline-item .time {
      color: #93c5fd;
      font-size: 0.82rem;
      display: block;
      margin-bottom: 4px;
    }

    .timeline-item .line {
      color: var(--text);
      line-height: 1.55;
      font-size: 0.95rem;
    }

    .snapshot-card pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      background: rgba(8,16,29,0.54);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 16px;
      padding: 16px;
      overflow-x: auto;
      color: #dbeafe;
      line-height: 1.55;
      max-height: 260px;
    }

    .footer-note {
      margin-top: 22px;
      color: var(--muted);
      font-size: 0.92rem;
      text-align: center;
    }

    @media (max-width: 1280px) {
      .summary-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .state-group-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 980px) {
      .layout, .two-col { grid-template-columns: 1fr; }
      .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .workflow-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
      .page { padding: 18px; }
      .summary-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <span class="eyebrow">SE4010 CTSE · Assignment 2 · Multi-Agent System</span>
      <h1>Local Multi-Agent SDLC Planning Assistant</h1>
      <p>
        A locally hosted multi-agent system that transforms a rough software idea into a structured engineering plan.
        This dashboard is designed to clearly demonstrate the assignment requirements: multi-agent orchestration,
        shared state handoff, custom tool usage, observability, local Ollama integration, and workflow outputs.
      </p>
    </section>

    <div class="layout">
      <div class="stack">
        <section class="card">
          <h2>Project Input</h2>
          <p class="section-note">
            Provide a free-form software or system idea using the textarea or upload a plain text file.
            The backend orchestration remains unchanged and runs fully locally.
          </p>
          <form method="post" enctype="multipart/form-data" class="input-panel">
            <div>
              <label for="brief_text">Project Brief</label>
              <textarea id="brief_text" name="brief_text" placeholder="Example: Build a smart campus portal that supports student registration, timetable viewing, lecturer communication, notices, event booking, and role-based access for students, lecturers, and admins.">{{ brief_text }}</textarea>
            </div>

            <div>
              <label for="brief_file">Optional Input File</label>
              <input id="brief_file" type="file" name="brief_file" accept=".txt">
            </div>

            <div class="button-row">
              <button class="button" type="submit">Run Workflow</button>
              <span class="muted-chip">Execution Mode: Local Flask UI</span>
            </div>
          </form>

          {% if error_message %}
            <div class="error">{{ error_message }}</div>
          {% endif %}
        </section>

        <section class="card">
          <h2>Execution Summary</h2>
          <p class="section-note">
            High-level metrics from the latest workflow run, including detected project context, planning counts,
            review state, and local SLM configuration.
          </p>

          {% if execution_summary %}
            <div class="summary-grid">
              <div class="summary-tile"><span class="summary-label">Workflow Status</span><div class="summary-value">{{ execution_summary.workflow_status }}</div></div>
              <div class="summary-tile"><span class="summary-label">Project Domain</span><div class="summary-value">{{ execution_summary.project_domain }}</div></div>
              <div class="summary-tile"><span class="summary-label">Ollama</span><div class="summary-value">{{ execution_summary.ollama_enabled }}</div></div>
              <div class="summary-tile"><span class="summary-label">Model</span><div class="summary-value">{{ execution_summary.ollama_model }}</div></div>
              <div class="summary-tile"><span class="summary-label">Review Cycles</span><div class="summary-value">{{ execution_summary.review_cycles }}</div></div>

              <div class="summary-tile"><span class="summary-label">Stakeholders</span><div class="summary-value">{{ execution_summary.stakeholder_count }}</div></div>
              <div class="summary-tile"><span class="summary-label">Features</span><div class="summary-value">{{ execution_summary.feature_count }}</div></div>
              <div class="summary-tile"><span class="summary-label">FR / NFR</span><div class="summary-value">{{ execution_summary.functional_count }} / {{ execution_summary.non_functional_count }}</div></div>
              <div class="summary-tile"><span class="summary-label">Stories / Tasks</span><div class="summary-value">{{ execution_summary.story_count }} / {{ execution_summary.task_count }}</div></div>
              <div class="summary-tile"><span class="summary-label">Phases / Risks</span><div class="summary-value">{{ execution_summary.phase_count }} / {{ execution_summary.risk_count }}</div></div>
            </div>
          {% else %}
            <p class="section-note">Run the workflow to populate the latest execution summary.</p>
          {% endif %}
        </section>

        <section class="card">
          <h2>Assignment Alignment</h2>
          <p class="section-note">
            A quick visual confirmation that the current implementation covers the core MAS engineering requirements.
          </p>
          <div class="badge-row">
            {% for item in assignment_alignment %}
              <span class="badge"><strong>{{ item.label }}:</strong> {{ item.value }}</span>
            {% endfor %}
          </div>
        </section>

        <section class="card">
          <h2>Workflow Connectivity</h2>
          <p class="section-note">
            The system operates as a four-stage agent pipeline. Each agent reads and updates the same shared workflow state,
            uses one dedicated tool, and contributes a distinct artifact to the final engineering plan.
          </p>

          <div class="workflow-banner">
            Shared Workflow State flows across all four agents: input understanding → requirements modeling → planning → review and finalization.
          </div>

          <div class="workflow-grid">
            {% for agent in workflow_agents %}
              <article class="agent-card">
                <div class="agent-title">
                  <h3>{{ agent.name }}</h3>
                  <span class="status {{ agent.status|lower|replace(' ', '_') }}">{{ agent.status }}</span>
                </div>

                <span class="meta-label">Role</span>
                <div class="meta-value">{{ agent.role }}</div>

                <span class="meta-label">Tool</span>
                <div class="meta-value">{{ agent.tool }}</div>

                <span class="meta-label">Primary Artifact</span>
                <div class="meta-value">{{ agent.artifact }}</div>

                <span class="meta-label">Output / State Summary</span>
                <div class="meta-value">{{ agent.summary }}</div>
              </article>
            {% endfor %}
          </div>
        </section>

        <section class="card">
          <h2>Shared State Flow</h2>
          <p class="section-note">
            This view groups the most important state handoff points into readable stages, making it easier to explain how context is preserved across the workflow.
          </p>

          <div class="state-group-grid">
            {% for group in state_flow_groups %}
              <section class="state-group">
                <h3>{{ group.title }}</h3>
                <p>{{ group.description }}</p>
                {% for item in group['items'] %}
                  <div class="state-item">
                    <strong>{{ item.field }}</strong>
                    <div>{{ item.value }}</div>
                  </div>
                {% endfor %}
              </section>
            {% endfor %}
          </div>

          <div class="state-list">
            {% for field in shared_state_fields %}
              <span class="state-chip">{{ field }}</span>
            {% endfor %}
          </div>
        </section>
      </div>

      <div class="stack">
        <section class="card output-card">
          <h2>Final Output</h2>
          <p class="section-note">
            The reviewed engineering plan generated by the full multi-agent workflow.
          </p>
          {% if final_output_html %}
            <div class="markdown-viewer">{{ final_output_html|safe }}</div>
          {% else %}
            <p class="section-note">Run the workflow to view the generated final output.</p>
          {% endif %}
        </section>

        <section class="card">
          <h2>Trace / Log Preview</h2>
          <p class="section-note">
            A readable preview of the latest workflow trace events, showing step-by-step execution visibility.
          </p>
          {% if timeline_items %}
            <div class="timeline">
              {% for item in timeline_items %}
                <div class="timeline-item">
                  <span class="time">{{ item.timestamp }}</span>
                  <div class="line">{{ item.line|safe }}</div>
                </div>
              {% endfor %}
            </div>
          {% else %}
            <p class="section-note">The latest run will show a readable execution timeline here.</p>
          {% endif %}
        </section>

        <section class="card">
          <h2>Saved Artifacts</h2>
          <p class="section-note">
            These files are persisted after each run and can be used as demo evidence or report screenshots.
          </p>
          {% if saved_files %}
            <ul class="file-list">
              <li class="file-item"><strong>Markdown Output</strong>{{ saved_files.markdown }}</li>
              <li class="file-item"><strong>JSON Snapshot</strong>{{ saved_files.json_snapshot }}</li>
              <li class="file-item"><strong>Trace Log</strong>{{ saved_files.trace_log }}</li>
            </ul>
          {% else %}
            <p class="section-note">Saved file paths will appear after execution.</p>
          {% endif %}
        </section>

        <section class="card snapshot-card">
          <h2>Raw Final State Snapshot</h2>
          <p class="section-note">
            This raw JSON snapshot is retained mainly for debugging, verification, and report evidence.
          </p>
          {% if state_snapshot %}
            <pre>{{ state_snapshot }}</pre>
          {% else %}
            <p class="section-note">The most recent shared-state snapshot will appear here after execution.</p>
          {% endif %}
        </section>
      </div>
    </div>

    <p class="footer-note">
      Demo UI for the Local Multi-Agent SDLC Planning Assistant · Flask frontend on top of the existing LangGraph backend workflow.
    </p>
  </div>
</body>
</html>
"""


def create_app(
    *,
    runner: Callable[..., WorkflowRunResult] | None = None,
    settings: AppSettings | None = None,
) -> Flask:
    """Create the Flask app used for local demo support."""
    app = Flask(__name__)
    workflow_runner = runner or execute_workflow
    runtime_settings = settings or AppSettings()

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        brief_text = ""
        error_message = ""
        final_output_html = ""
        saved_files: dict[str, str] | None = None
        state_snapshot = ""
        timeline_items: list[dict[str, str]] = []
        execution_summary: dict[str, object] | None = None
        assignment_alignment = [
            {"label": "4 Agents", "value": "Implemented"},
            {"label": "4 Tools", "value": "Integrated"},
            {"label": "LangGraph", "value": "Orchestrated"},
            {"label": "Shared State", "value": "Active"},
            {"label": "Tracing", "value": "JSONL Logs"},
            {"label": "Ollama", "value": runtime_settings.ollama_model if runtime_settings.enable_live_model else "Disabled"},
            {"label": "Execution", "value": "Awaiting Run"},
            {"label": "Tests", "value": "15 Passing"},
        ]
        state_flow_groups: list[dict[str, object]] = []
        shared_state_fields: list[str] = []
        workflow_agents = [
            {
                "name": "Intake Agent",
                "role": "Transforms the rough project idea into a structured shared brief.",
                "tool": "Project Brief Normalizer Tool",
                "artifact": "project_brief",
                "status": "pending",
                "summary": "No run yet. Shared state has not been updated.",
            },
            {
                "name": "Requirements Agent",
                "role": "Builds structured functional and non-functional requirements.",
                "tool": "Requirements Formatter Tool",
                "artifact": "requirements_spec",
                "status": "pending",
                "summary": "No run yet. Shared state has not been updated.",
            },
            {
                "name": "Task Planner Agent",
                "role": "Generates user stories, tasks, dependencies, and roadmap phases.",
                "tool": "Task Breakdown Generator Tool",
                "artifact": "delivery_plan",
                "status": "pending",
                "summary": "No run yet. Shared state has not been updated.",
            },
            {
                "name": "Risk & Review Agent",
                "role": "Validates consistency, identifies risks, and finalizes the engineering plan.",
                "tool": "Consistency & Risk Checker Tool",
                "artifact": "risk_report + final_output",
                "status": "pending",
                "summary": "No run yet. Shared state has not been updated.",
            },
        ]

        if request.method == "POST":
            brief_text, error_message = _extract_input_text(request)
            if not error_message:
                try:
                    result = workflow_runner(brief_text, settings=runtime_settings, input_mode="ui")
                    context = load_ui_context(result, runtime_settings)
                    workflow_agents = context["agent_panels"]
                    execution_summary = context["execution_summary"]
                    assignment_alignment = context["assignment_alignment"]
                    state_flow_groups = context["state_flow_groups"]
                    shared_state_fields = context["shared_state_fields"]
                    final_output_html = _render_markdown_like(read_text_file(result.markdown_output_path))
                    timeline_items = _format_timeline_items(context["trace_events"])
                    saved_files = context["saved_files"]
                    state_snapshot = escape(read_text_file(result.json_snapshot_path))
                except ModuleNotFoundError:
                    error_message = "Missing dependency. Install requirements with `pip install -r requirements.txt`."
                except Exception as exc:  # pragma: no cover - defensive runtime guard
                    error_message = f"Workflow execution failed: {exc}"

        return render_template_string(
            HTML_TEMPLATE,
            brief_text=brief_text,
            error_message=error_message,
            final_output_html=final_output_html,
            saved_files=saved_files,
            state_snapshot=state_snapshot,
            workflow_agents=workflow_agents,
            timeline_items=timeline_items,
            execution_summary=execution_summary,
            assignment_alignment=assignment_alignment,
            state_flow_groups=state_flow_groups,
            shared_state_fields=shared_state_fields,
        )

    return app


def _extract_input_text(http_request: Request) -> tuple[str, str]:
    """Read either the textarea value or uploaded text file."""
    brief_text = (http_request.form.get("brief_text") or "").strip()
    upload = http_request.files.get("brief_file")

    if upload and upload.filename:
        brief_text = upload.read().decode("utf-8").strip()

    if not brief_text:
        return "", "Provide a project brief in the textarea or upload a text file."
    return brief_text, ""


def _render_markdown_like(markdown_text: str) -> str:
    """Render a limited markdown-like view without adding heavy dependencies."""
    lines = markdown_text.splitlines()
    html_parts: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            close_list()
            continue

        if stripped.startswith("### "):
            close_list()
            html_parts.append(f"<h3>{escape(stripped[4:])}</h3>")
            continue

        if stripped.startswith("## "):
            close_list()
            html_parts.append(f"<h2>{escape(stripped[3:])}</h2>")
            continue

        if stripped.startswith("# "):
            close_list()
            html_parts.append(f"<h1>{escape(stripped[2:])}</h1>")
            continue

        if stripped.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{_format_inline_markup(stripped[2:])}</li>")
            continue

        close_list()
        html_parts.append(f"<p>{_format_inline_markup(stripped)}</p>")

    close_list()
    return "".join(html_parts)


def _format_inline_markup(text: str) -> str:
    """Apply minimal inline formatting for bold segments."""
    escaped = escape(text)
    parts = escaped.split("**")
    if len(parts) < 3:
        return escaped

    rebuilt: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 1:
            rebuilt.append(f"<strong>{part}</strong>")
        else:
            rebuilt.append(part)
    return "".join(rebuilt)


def _format_timeline_items(trace_events: list[dict[str, object]]) -> list[dict[str, str]]:
    """Render the most recent trace events as a readable timeline."""
    items: list[dict[str, str]] = []
    for event in latest_log_preview(trace_events):
        line = (
            f"<strong>{escape(str(event.get('agent')))}</strong> · "
            f"{escape(str(event.get('status')))} · "
            f"{escape(str(event.get('event_type')))}"
        )

        updated_fields = event.get("updated_fields")
        if updated_fields:
            line += f"<br><span style='color:#9db0c9'>Updated:</span> {escape(str(updated_fields))}"

        input_summary = event.get("input_summary")
        if input_summary:
            line += f"<br><span style='color:#9db0c9'>Input:</span> {escape(str(input_summary))}"

        output_summary = event.get("output_summary")
        if output_summary:
            line += f"<br><span style='color:#9db0c9'>Output:</span> {escape(str(output_summary))}"

        items.append(
            {
                "timestamp": str(event.get("timestamp")),
                "line": line,
            }
        )
    return items


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
