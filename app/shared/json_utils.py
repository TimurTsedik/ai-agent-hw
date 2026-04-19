"""Helpers to recover JSON from possibly noisy LLM text."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json_payload(text: str) -> str:
    """Return a substring that should parse as JSON (object)."""
    stripped = text.strip()
    ret = _try_strip_markdown_fence(stripped)
    return ret


def _try_strip_markdown_fence(text: str) -> str:
    match = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```\s*$", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def parse_json_loose(text: str) -> Any:
    """Parse JSON; if direct parse fails, take the first top-level `{...}` block."""
    ret: Any
    payload = extract_json_payload(text)
    try:
        ret = json.loads(payload)
        return ret
    except json.JSONDecodeError:
        pass
    fragment = _first_brace_object(payload)
    ret = json.loads(fragment)
    return ret


def _first_brace_object(text: str) -> str:
    start = text.find("{")
    if start < 0:
        msg = "No JSON object found in model output"
        raise ValueError(msg)
    depth = 0
    idx = start
    in_string: str | None = None
    escape = False
    while idx < len(text):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            idx += 1
            continue
        if ch in ("'", '"'):
            in_string = ch
            idx += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
        idx += 1
    msg = "Unbalanced braces in model output"
    raise ValueError(msg)
