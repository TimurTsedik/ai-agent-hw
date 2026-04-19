"""Domain-specific errors for the agent."""


class AgentError(Exception):
    """Base class for controlled agent failures."""


class InvalidJsonResponseError(AgentError):
    """LLM output is not valid JSON or does not match the expected schema."""


class UnknownToolError(AgentError):
    """Model requested a tool that is not registered."""


class MaxStepsExceededError(AgentError):
    """Agent used all allowed steps without a final answer."""


class ToolExecutionError(AgentError):
    """Tool failed in an unexpected way (optional wrapper)."""


class OllamaRequestError(AgentError):
    """HTTP or API error when talking to Ollama."""
