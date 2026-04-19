"""Structured outputs expected from the LLM."""

from typing import Any

from pydantic import BaseModel, Field


class ActionResponse(BaseModel):
    """Model chose a tool."""

    thought: str
    action: str
    args: dict[str, Any] = Field(default_factory=dict)


class FinalResponse(BaseModel):
    """Model chose to finish."""

    final_answer: str
