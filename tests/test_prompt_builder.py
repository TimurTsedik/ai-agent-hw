"""Tests for PromptBuilder presets."""

import unittest

from app.config.settings import SystemPromptPreset
from app.services.prompt_builder import PromptBuilder


class TestPromptBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self._tool_specs: list[tuple[str, dict[str, str]]] = [
            ("calculator", {"expression": "string"}),
        ]

    def test_default_includes_tool_name(self) -> None:
        builder = PromptBuilder(self._tool_specs, preset=SystemPromptPreset.DEFAULT)
        text = builder.build("task", [])
        self.assertIn("Available tools:", text)
        self.assertIn("calculator", text)
        self.assertIn("Current user task:", text)
        self.assertIn("task", text)

    def test_autonomous_replaces_placeholder(self) -> None:
        builder = PromptBuilder(self._tool_specs, preset=SystemPromptPreset.AUTONOMOUS)
        text = builder.build("task", [])
        self.assertNotIn("{{TOOLS_DESCRIPTION}}", text)
        self.assertIn("You are an autonomous AI agent.", text)
        self.assertIn("calculator", text)
        self.assertIn("Current user task:", text)


if __name__ == "__main__":
    unittest.main()
