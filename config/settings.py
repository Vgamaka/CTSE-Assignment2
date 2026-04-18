"""Central settings for the local workflow scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4


@dataclass(slots=True)
class AppSettings:
    """Application settings used by the terminal runner and workflow."""

    # Suggested ownership: one student can manage runtime configuration,
    # local paths, and future Ollama integration defaults here.
    # TODO: add validated live Ollama client configuration once stronger
    # local reasoning is introduced in a later phase.
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    enable_live_model: bool = True
    llm_temperature: float = 0.1
    llm_request_timeout_seconds: int = 60
    fallback_to_rules: bool = True
    max_review_loops: int = 1
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])

    def ensure_directories(self) -> None:
        """Create required runtime directories automatically."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.sample_inputs_dir.mkdir(parents=True, exist_ok=True)

    def new_run_id(self) -> str:
        """Return a short deterministic-looking run identifier."""
        return uuid4().hex[:10]

    @property
    def logs_dir(self) -> Path:
        """Directory used for JSONL execution traces."""
        return self.project_root / "logs"

    @property
    def outputs_dir(self) -> Path:
        """Directory used for Markdown and JSON outputs."""
        return self.project_root / "outputs"

    @property
    def sample_inputs_dir(self) -> Path:
        """Directory for example local input files."""
        return self.project_root / "sample_inputs"
