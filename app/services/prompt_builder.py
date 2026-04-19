"""Builds prompts that constrain the model to JSON-only tool use."""

from __future__ import annotations

import json

from app.config.settings import SystemPromptPreset
from app.domain.entities.agent_step import AgentStep
from app.services.system_prompt_templates import (
    AUTONOMOUS_PROMPT_TEMPLATE,
    DEFAULT_PROMPT_TEMPLATE,
    TOOLS_DESCRIPTION_PLACEHOLDER,
)


class PromptBuilder:
    """Assembles system rules, tool specs, history, and the user task."""

    def __init__(
        self,
        tool_descriptions: list[tuple[str, dict[str, str]]],
        preset: SystemPromptPreset = SystemPromptPreset.DEFAULT,
    ) -> None:
        self._tool_descriptions = tool_descriptions
        self._preset = preset

    def build(self, user_task: str, previous_steps: list[AgentStep]) -> str:
        if self._preset == SystemPromptPreset.AUTONOMOUS:
            ret = self._build_autonomous()
        else:
            ret = self._build_default()
        ret = self._append_history_and_task(ret, user_task, previous_steps)
        return ret

    def _build_tools_description(self) -> str:
        lines: list[str] = []
        idx = 1
        for name, arg_schema in self._tool_descriptions:
            lines.append(f"{idx}. {name}")
            lines.append("Args (JSON shape):")
            lines.append(json.dumps(arg_schema, ensure_ascii=False, indent=2))
            idx += 1
            lines.append("")
        ret = "\n".join(lines).rstrip()
        return ret

    def _apply_tools_placeholder(self, template: str) -> str:
        tools_block = self._build_tools_description()
        ret = template.replace(TOOLS_DESCRIPTION_PLACEHOLDER, tools_block)
        return ret

    def _build_default(self) -> str:
        ret = self._apply_tools_placeholder(DEFAULT_PROMPT_TEMPLATE)
        return ret

    def _build_autonomous(self) -> str:
        ret = self._apply_tools_placeholder(AUTONOMOUS_PROMPT_TEMPLATE)
        return ret

    def _append_history_and_task(
        self,
        prefix: str,
        user_task: str,
        previous_steps: list[AgentStep],
    ) -> str:
        sections: list[str] = [prefix, "", "Previous steps:"]
        if not previous_steps:
            sections.append("(none)")
        else:
            for step in previous_steps:
                sections.append(f"Step {step.step_index}:")
                if step.thought is not None:
                    sections.append(f"Thought: {step.thought}")
                if step.action is not None:
                    sections.append(f"Action: {step.action}")
                if step.args is not None:
                    sections.append(f"Args: {json.dumps(step.args, ensure_ascii=False)}")
                if step.observation is not None:
                    sections.append(f"Observation: {json.dumps(step.observation, ensure_ascii=False)}")
                if step.final_answer is not None:
                    sections.append(f"Final answer: {step.final_answer}")
                sections.append("")
        sections.append("Current user task:")
        sections.append(user_task)
        ret = "\n".join(sections)
        return ret
