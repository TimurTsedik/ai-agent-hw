"""Builds prompts that constrain the model to JSON-only tool use."""

from __future__ import annotations

import json

from app.domain.entities.agent_step import AgentStep


class PromptBuilder:
    """Assembles system rules, tool specs, history, and the user task."""

    def __init__(self, tool_descriptions: list[tuple[str, dict[str, str]]]) -> None:
        self._tool_descriptions = tool_descriptions

    def build(self, user_task: str, previous_steps: list[AgentStep]) -> str:
        sections: list[str] = [
            "You are a step-by-step AI agent with tools.",
            "On every step respond with ONLY a single JSON object and NOTHING else.",
            "No markdown fences. No keys except those defined below.",
            "Either choose a tool (thought + action + args) OR finish (final_answer).",
            "Use a tool when you need external data or computation.",
            "When you have enough information, return final_answer.",
            "",
            "JSON format 1 — tool:",
            json.dumps(
                {
                    "thought": "why you take this step",
                    "action": "toolName",
                    "args": {"key": "value"},
                },
                ensure_ascii=False,
            ),
            "",
            "JSON format 2 — finish:",
            json.dumps({"final_answer": "answer text"}, ensure_ascii=False),
            "",
            "Available tools:",
        ]
        idx = 1
        for name, arg_schema in self._tool_descriptions:
            sections.append(f"{idx}. {name}")
            sections.append("Args (JSON shape):")
            sections.append(json.dumps(arg_schema, ensure_ascii=False, indent=2))
            idx += 1
            sections.append("")
        sections.append("Previous steps:")
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
