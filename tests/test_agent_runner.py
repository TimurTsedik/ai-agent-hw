"""Tests for AgentRunner with a stub LLM."""

import json
import logging
import unittest

from app.config.settings import SystemPromptPreset
from app.domain.protocols.llm_client_protocol import LlmClientProtocol
from app.infrastructure.tools.calculator_tool import CalculatorTool
from app.services.agent_runner import AgentRunner
from app.services.prompt_builder import PromptBuilder
from app.services.response_parser import ResponseParser
from app.services.tool_registry import ToolRegistry


class StubLlm:
    """Returns queued raw strings (implements LlmClientProtocol)."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self._index = 0

    def generate(self, prompt: str) -> str:
        if self._index >= len(self._responses):
            msg = "StubLlm: no more scripted responses"
            raise RuntimeError(msg)
        ret = self._responses[self._index]
        self._index += 1
        return ret


class TestAgentRunner(unittest.TestCase):
    def setUp(self) -> None:
        logging.getLogger("app.services.agent_runner").setLevel(logging.CRITICAL)

    def _minimal_registry(self) -> ToolRegistry:
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        return registry

    def _builder(self) -> PromptBuilder:
        specs: list[tuple[str, dict[str, str]]] = [
            ("calculator", {"expression": "string"}),
        ]
        return PromptBuilder(specs, preset=SystemPromptPreset.DEFAULT)

    def test_finishes_on_final_answer(self) -> None:
        llm: LlmClientProtocol = StubLlm([json.dumps({"final_answer": "ok"})])
        runner = AgentRunner(
            llm=llm,
            tools=self._minimal_registry(),
            parser=ResponseParser(),
            prompt_builder=self._builder(),
            max_steps=4,
        )
        result = runner.run("task")
        self.assertTrue(result.success)
        self.assertEqual(result.final_answer, "ok")

    def test_multi_step_action_then_final(self) -> None:
        llm: LlmClientProtocol = StubLlm(
            [
                json.dumps(
                    {
                        "thought": "calc",
                        "action": "calculator",
                        "args": {"expression": "2+2"},
                    }
                ),
                json.dumps({"final_answer": "four"}),
            ]
        )
        runner = AgentRunner(
            llm=llm,
            tools=self._minimal_registry(),
            parser=ResponseParser(),
            prompt_builder=self._builder(),
            max_steps=8,
        )
        result = runner.run("task")
        self.assertTrue(result.success)
        self.assertEqual(result.final_answer, "four")
        self.assertEqual(len(result.steps), 2)

    def test_stops_on_max_steps(self) -> None:
        repeat = json.dumps(
            {"thought": "again", "action": "calculator", "args": {"expression": "1+1"}}
        )
        llm: LlmClientProtocol = StubLlm([repeat] * 10)
        runner = AgentRunner(
            llm=llm,
            tools=self._minimal_registry(),
            parser=ResponseParser(),
            prompt_builder=self._builder(),
            max_steps=3,
        )
        result = runner.run("never ending")
        self.assertFalse(result.success)
        self.assertIn("maximum number of steps", result.error_message or "")

    def test_unknown_tool_error(self) -> None:
        llm: LlmClientProtocol = StubLlm(
            [
                json.dumps(
                    {
                        "thought": "nope",
                        "action": "unknownTool",
                        "args": {},
                    }
                ),
            ]
        )
        runner = AgentRunner(
            llm=llm,
            tools=self._minimal_registry(),
            parser=ResponseParser(),
            prompt_builder=self._builder(),
            max_steps=5,
        )
        result = runner.run("task")
        self.assertFalse(result.success)
        self.assertIn("Unknown tool", result.error_message or "")


if __name__ == "__main__":
    unittest.main()
