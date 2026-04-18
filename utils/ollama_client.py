"""Minimal local Ollama client for assignment-safe structured prompting."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(slots=True)
class OllamaClient:
    """Tiny client for calling a local Ollama generate endpoint."""

    base_url: str
    model: str
    temperature: float = 0.1
    timeout_seconds: int = 60

    def generate(self, prompt: str) -> str:
        """Return plain text from the local Ollama model."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
                return str(body.get("response", "")).strip()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return ""
