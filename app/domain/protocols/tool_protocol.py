"""Tool abstraction."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolProtocol(Protocol):
    """A callable tool registered by name."""

    @property
    def name(self) -> str:
        """Stable tool identifier matching model output."""
        ...

    def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        """Run the tool; must return a JSON-serializable dict."""
        ...
