"""Registers tools and dispatches by name."""

from __future__ import annotations

from typing import Any

from app.domain.protocols.tool_protocol import ToolProtocol
from app.shared.exceptions import UnknownToolError


class ToolRegistry:
    """In-memory registry — extend by registering new ToolProtocol implementations."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolProtocol] = {}

    def register(self, tool: ToolProtocol) -> None:
        name = tool.name
        self._tools[name] = tool

    def has(self, name: str) -> bool:
        ret = name in self._tools
        return ret

    def get(self, name: str) -> ToolProtocol:
        if name not in self._tools:
            msg = f"Unknown tool: {name}"
            raise UnknownToolError(msg)
        ret = self._tools[name]
        return ret

    def execute(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        tool = self.get(name)
        ret = tool.execute(args)
        return ret

    def tool_names(self) -> list[str]:
        ret = sorted(self._tools.keys())
        return ret
