"""HTTP client for the local Ollama API."""

from __future__ import annotations

import logging
from typing import Any

import requests

from app.shared.exceptions import OllamaRequestError

logger = logging.getLogger(__name__)


class OllamaClient:
    """Synchronous chat call to Ollama — model name comes from settings."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> str:
        url = f"{self._base_url}/api/chat"
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        ret = ""
        try:
            response = requests.post(url, json=payload, timeout=self._timeout_seconds)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.exception("Ollama request failed")
            msg = f"Ollama request failed: {exc}"
            raise OllamaRequestError(msg) from exc
        message = data.get("message") if isinstance(data, dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                ret = content
        if ret == "":
            msg = "Unexpected Ollama response shape"
            raise OllamaRequestError(msg)
        return ret
