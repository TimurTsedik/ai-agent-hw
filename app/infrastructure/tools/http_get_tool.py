"""HTTP GET with timeout and response truncation."""

from __future__ import annotations

from typing import Any

import requests


class HttpGetTool:
    """Fetches URL body as text (no SSRF filtering in MVP)."""

    def __init__(self, timeout_seconds: float, max_response_chars: int) -> None:
        self._timeout_seconds = timeout_seconds
        self._max_response_chars = max_response_chars

    @property
    def name(self) -> str:
        ret = "httpGet"
        return ret

    def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        url = args.get("url")
        if not isinstance(url, str) or not url.strip():
            return {"ok": False, "error": "Missing or invalid 'url'"}
        ret: dict[str, Any]
        try:
            response = requests.get(
                url,
                timeout=self._timeout_seconds,
                headers={"User-Agent": "ai-agent-hw/1.0"},
            )
            text = response.text
            if len(text) > self._max_response_chars:
                text = text[: self._max_response_chars]
            ret = {
                "ok": True,
                "statusCode": response.status_code,
                "text": text,
            }
        except requests.RequestException as exc:
            ret = {"ok": False, "error": str(exc)}
        return ret
