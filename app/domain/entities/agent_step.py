"""One step in the agent trace."""

from typing import Any

from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    """Recorded step for history and logging."""

    step_index: int = Field(ge=1)
    thought: str | None = None
    action: str | None = None
    args: dict[str, Any] | None = None
    observation: dict[str, Any] | None = None
    final_answer: str | None = None
