"""Read text files confined to a workspace directory."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ReadFileTool:
    """Reads UTF-8 (with fallback) text; rejects paths outside workspace."""

    def __init__(self, workspace_path: Path, max_file_size_bytes: int) -> None:
        self._workspace_path = workspace_path.resolve()
        self._max_file_size_bytes = max_file_size_bytes

    @property
    def name(self) -> str:
        ret = "readFile"
        return ret

    def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        raw_path = args.get("path")
        if not isinstance(raw_path, str) or raw_path.strip() == "":
            return {"ok": False, "error": "Missing or invalid 'path'"}
        rel = Path(raw_path)
        if rel.is_absolute():
            return {"ok": False, "error": "Absolute paths are not allowed"}
        if ".." in rel.parts:
            return {"ok": False, "error": "Path must not contain '..'"}

        candidate = (self._workspace_path / rel).resolve()
        try:
            candidate.relative_to(self._workspace_path)
        except ValueError:
            return {"ok": False, "error": "Path escapes workspace"}

        ret: dict[str, Any]
        if not candidate.is_file():
            return {"ok": False, "error": "File not found"}
        try:
            size = candidate.stat().st_size
        except OSError as exc:
            return {"ok": False, "error": f"Cannot stat file: {exc}"}
        if size > self._max_file_size_bytes:
            return {"ok": False, "error": "File too large"}
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
            return {"ok": False, "error": f"Read failed: {exc}"}
        except UnicodeDecodeError:
            try:
                data = candidate.read_bytes()
                text = data.decode("utf-8", errors="replace")
            except OSError as exc:
                return {"ok": False, "error": f"Read failed: {exc}"}
        ret = {"ok": True, "content": text}
        return ret
