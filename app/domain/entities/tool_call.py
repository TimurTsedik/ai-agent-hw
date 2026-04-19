"""Tool invocation value object."""

from typing import Any

from pydantic import BaseModel


class ToolCall(BaseModel):
    """Resolved tool name and arguments."""

    name: str
    args: dict[str, Any]
