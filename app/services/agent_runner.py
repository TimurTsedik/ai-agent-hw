"""Orchestrates the thought → action → observation loop."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.domain.entities.agent_step import AgentStep
from app.domain.entities.llm_response import ActionResponse, FinalResponse
from app.domain.protocols.llm_client_protocol import LlmClientProtocol
from app.services.prompt_builder import PromptBuilder
from app.services.response_parser import ResponseParser
from app.services.tool_registry import ToolRegistry
from app.shared.exceptions import AgentError, InvalidJsonResponseError

logger = logging.getLogger(__name__)


@dataclass
class AgentRunResult:
    """Outcome of a single agent session."""

    success: bool
    final_answer: str | None = None
    error_message: str | None = None
    steps: list[AgentStep] = field(default_factory=list)


class AgentRunner:
    """Runs the loop until final_answer, failure, or max steps."""

    def __init__(
        self,
        llm: LlmClientProtocol,
        tools: ToolRegistry,
        parser: ResponseParser,
        prompt_builder: PromptBuilder,
        max_steps: int,
    ) -> None:
        self._llm = llm
        self._tools = tools
        self._parser = parser
        self._prompt_builder = prompt_builder
        self._max_steps = max_steps

    def run(self, user_task: str) -> AgentRunResult:
        history: list[AgentStep] = []
        ret: AgentRunResult
        final_answer: str | None = None
        error_message: str | None = None
        success = False
        for step_index in range(1, self._max_steps + 1):
            prompt = self._prompt_builder.build(user_task, history)
            try:
                raw = self._llm.generate(prompt)
            except AgentError as exc:
                error_message = str(exc)
                logger.warning("LLM error: %s", error_message)
                ret = AgentRunResult(
                    success=False,
                    error_message=error_message,
                    steps=list(history),
                )
                return ret
            try:
                parsed = self._parser.parse(raw)
            except InvalidJsonResponseError as exc:
                error_message = str(exc)
                logger.warning("Parse error: %s", error_message)
                ret = AgentRunResult(
                    success=False,
                    error_message=error_message,
                    steps=list(history),
                )
                return ret
            if isinstance(parsed, FinalResponse):
                history.append(
                    AgentStep(
                        step_index=step_index,
                        thought=None,
                        action=None,
                        args=None,
                        observation=None,
                        final_answer=parsed.final_answer,
                    )
                )
                final_answer = parsed.final_answer
                success = True
                break
            if isinstance(parsed, ActionResponse):
                if not self._tools.has(parsed.action):
                    error_message = f"Unknown tool: {parsed.action}"
                    logger.warning("%s", error_message)
                    ret = AgentRunResult(
                        success=False,
                        error_message=error_message,
                        steps=list(history),
                    )
                    return ret
                observation = self._tools.execute(parsed.action, parsed.args)
                history.append(
                    AgentStep(
                        step_index=step_index,
                        thought=parsed.thought,
                        action=parsed.action,
                        args=parsed.args,
                        observation=observation,
                        final_answer=None,
                    )
                )
                continue
        else:
            error_message = "Agent stopped: maximum number of steps exceeded"
            logger.warning("%s", error_message)
            ret = AgentRunResult(
                success=False,
                error_message=error_message,
                steps=list(history),
            )
            return ret
        ret = AgentRunResult(
            success=success,
            final_answer=final_answer,
            error_message=error_message,
            steps=list(history),
        )
        return ret
