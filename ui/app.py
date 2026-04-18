"""Small Flask-based demo UI for the Local Multi-Agent SDLC Planning Assistant."""

from __future__ import annotations

from html import escape
from typing import Callable

from flask import Flask, Request, render_template_string, request

from config.settings import AppSettings
from ui.helpers import AGENT_METADATA, latest_log_preview, load_ui_context, read_text_file
from utils.workflow_runner import WorkflowRunResult, execute_workflow

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Local Multi-Agent SDLC Planning Assistant</title>
  <style>
    body { font-family: Georgia, "Times New Roman", serif; margin: 0; background: #f4f1eb; color: #1f2933; }
    .page { max-width: 1200px; margin: 0 auto; padding: 24px; }
    .hero { background: linear-gradient(135deg, #13315c, #3e5c76); color: #fff; padding: 24px; border-radius: 18px; }
    .hero p { max-width: 860px; line-height: 1.5; }
    .grid { display: grid; gap: 18px; margin-top: 22px; }
    .two { grid-template-columns: 1.1fr 0.9fr; }
    .card { background: #fffdf8; border: 1px solid #d9d0c3; border-radius: 16px; padding: 18px; box-shadow: 0 8px 24px rgba(19, 49, 92, 0.08); }
    .card h2, .card h3 { margin-top: 0; }
    textarea { width: 100%; min-height: 180px; padding: 12px; font: inherit; border-radius: 12px; border: 1px solid #b8c4d0; box-sizing: border-box; }
    input[type=file] { width: 100%; margin-top: 8px; }
    .button { background: #13315c; color: #fff; border: 0; border-radius: 999px; padding: 12px 18px; font: inherit; cursor: pointer; margin-top: 14px; }
    .button:hover { background: #0f2748; }
    .workflow { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; align-items: start; }
    .agent-card { background: #fff; border: 1px solid #cbd5df; border-radius: 14px; padding: 14px; position: relative; min-height: 240px; }
    .agent-card:not(:last-child)::after { content: "→ Shared State"; position: absolute; right: -72px; top: 50%; transform: translateY(-50%); color: #355070; font-size: 0.95rem; width: 68px; text-align: center; }
    .status { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 0.88rem; background: #dde7f0; color: #13315c; }
    .status.completed, .status.approved, .status.finalized { background: #d8f3dc; color: #1b5e20; }
    .status.needs_clarification { background: #fff3cd; color: #7a4b00; }
    .status.pending { background: #eceff1; color: #455a64; }
    .muted { color: #52606d; }
    .label { font-weight: bold; color: #13315c; display: block; margin-top: 10px; }
    pre { white-space: pre-wrap; word-break: break-word; background: #f8fafc; border: 1px solid #d9e2ec; border-radius: 12px; padding: 14px; overflow-x: auto; }
    ul { padding-left: 20px; }
    .file-list li { margin-bottom: 8px; }
    .error { background: #fdecea; color: #7f1d1d; border: 1px solid #f5c2c7; padding: 12px; border-radius: 12px; margin-top: 12px; }
    @media (max-width: 1080px) {
      .two { grid-template-columns: 1fr; }
      .workflow { grid-template-columns: 1fr; }
      .agent-card:not(:last-child)::after { content: "↓ Shared State"; position: static; display: block; margin-top: 14px; transform: none; width: auto; text-align: left; }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>Local Multi-Agent SDLC Planning Assistant</h1>
      <p>This thin local UI sits on top of the existing backend workflow. It shows project input, how the shared state moves through four agents and their tools, the final output, and the trace log generated during the latest run.</p>
    </section>

    <div class="grid two">
      <section class="card">
        <h2>Project Input</h2>
        <p class="muted">Use either the textarea or upload a plain text file. The backend workflow stays unchanged.</p>
        <form method="post" enctype="multipart/form-data">
          <label class="label" for="brief_text">Project Brief</label>
          <textarea id="brief_text" name="brief_text" placeholder="Paste a project idea here...">{{ brief_text }}</textarea>
          <label class="label" for="brief_file">Optional Input File</label>
          <input id="brief_file" type="file" name="brief_file" accept=".txt">
          <button class="button" type="submit">Run Workflow</button>
        </form>
        {% if error_message %}
          <div class="error">{{ error_message }}</div>
        {% endif %}
      </section>

      <section class="card">
        <h2>Workflow Connectivity</h2>
        <p class="muted">All four agents read and update the same shared workflow state. Each agent uses one tool and contributes a distinct planning artifact.</p>
        <div class="workflow">
          {% for agent in workflow_agents %}
            <div class="agent-card">
              <h3>{{ agent.name }}</h3>
              <span class="status {{ agent.status|lower|replace(' ', '_') }}">{{ agent.status }}</span>
              <span class="label">Role</span>
              <div>{{ agent.role }}</div>
              <span class="label">Tool</span>
              <div>{{ agent.tool }}</div>
              <span class="label">Output / State Summary</span>
              <div class="muted">{{ agent.summary }}</div>
            </div>
          {% endfor %}
        </div>
      </section>
    </div>

    <div class="grid two">
      <section class="card">
        <h2>Final Output</h2>
        {% if final_output %}
          <pre>{{ final_output }}</pre>
        {% else %}
          <p class="muted">Run the workflow to view the generated Markdown output.</p>
        {% endif %}
      </section>

      <section class="card">
        <h2>Trace / Log Preview</h2>
        {% if trace_preview %}
          <pre>{{ trace_preview }}</pre>
        {% else %}
          <p class="muted">The latest run will show recent JSONL log events here.</p>
        {% endif %}
      </section>
    </div>

    <div class="grid two">
      <section class="card">
        <h2>Saved Files</h2>
        {% if saved_files %}
          <ul class="file-list">
            <li><strong>Markdown Output:</strong> {{ saved_files.markdown }}</li>
            <li><strong>JSON Snapshot:</strong> {{ saved_files.json_snapshot }}</li>
            <li><strong>Trace Log:</strong> {{ saved_files.trace_log }}</li>
          </ul>
        {% else %}
          <p class="muted">Saved file paths will appear after a run.</p>
        {% endif %}
      </section>

      <section class="card">
        <h2>Latest State Snapshot</h2>
        {% if state_snapshot %}
          <pre>{{ state_snapshot }}</pre>
        {% else %}
          <p class="muted">The most recent shared-state summary will appear here after execution.</p>
        {% endif %}
      </section>
    </div>
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
        final_output = ""
        trace_preview = ""
        saved_files: dict[str, str] | None = None
        state_snapshot = ""
        workflow_agents = [
            {**agent, "status": "pending", "summary": "No run yet. Shared state has not been updated."}
            for agent in AGENT_METADATA
        ]

        if request.method == "POST":
            brief_text, error_message = _extract_input_text(request)
            if not error_message:
                try:
                    result = workflow_runner(brief_text, settings=runtime_settings, input_mode="ui")
                    context = load_ui_context(result)
                    workflow_agents = context["agent_panels"]
                    final_output = read_text_file(result.markdown_output_path)
                    trace_preview = _format_trace_preview(context["trace_events"])
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
            final_output=escape(final_output),
            trace_preview=trace_preview,
            saved_files=saved_files,
            state_snapshot=state_snapshot,
            workflow_agents=workflow_agents,
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


def _format_trace_preview(trace_events: list[dict[str, object]]) -> str:
    """Render the most recent trace events as a readable text preview."""
    preview_lines: list[str] = []
    for event in latest_log_preview(trace_events):
        preview_lines.append(
            f"[{event.get('timestamp')}] {event.get('agent')} | "
            f"{event.get('status')} | {event.get('event_type')} | "
            f"updated={event.get('updated_fields')}"
        )
        preview_lines.append(f"  input: {event.get('input_summary')}")
        preview_lines.append(f"  output: {event.get('output_summary')}")
    return escape("\n".join(preview_lines))


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
