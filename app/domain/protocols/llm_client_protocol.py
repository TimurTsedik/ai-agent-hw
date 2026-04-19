"""LLM client abstraction."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LlmClientProtocol(Protocol):
    """Anything that can turn a prompt string into model text."""

    def generate(self, prompt: str) -> str:
        """Return raw assistant text (expected to be JSON per prompt rules)."""
        ...
