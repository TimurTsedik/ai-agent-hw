"""CLI entry: interactive or single-run task string."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from app.config.settings import Settings
from app.infrastructure.llm.ollama_client import OllamaClient
from app.infrastructure.tools.calculator_tool import CalculatorTool
from app.infrastructure.tools.http_get_tool import HttpGetTool
from app.infrastructure.tools.read_file_tool import ReadFileTool
from app.services.agent_runner import AgentRunResult, AgentRunner
from app.services.prompt_builder import PromptBuilder
from app.services.response_parser import ResponseParser
from app.services.tool_registry import ToolRegistry


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def build_agent(settings: Settings) -> AgentRunner:
    workspace = settings.workspace_path
    workspace.mkdir(parents=True, exist_ok=True)

    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(
        ReadFileTool(
            workspace_path=workspace,
            max_file_size_bytes=settings.max_file_size_bytes,
        )
    )
    registry.register(
        HttpGetTool(
            timeout_seconds=settings.http_timeout_seconds,
            max_response_chars=settings.max_http_response_chars,
        )
    )

    tool_specs: list[tuple[str, dict[str, str]]] = [
        ("calculator", {"expression": "string"}),
        ("readFile", {"path": "string"}),
        ("httpGet", {"url": "string"}),
    ]
    prompt_builder = PromptBuilder(tool_specs)
    parser = ResponseParser()
    llm = OllamaClient(
        base_url=str(settings.ollama_base_url),
        model=settings.ollama_model,
        timeout_seconds=600.0,
    )
    ret = AgentRunner(
        llm=llm,
        tools=registry,
        parser=parser,
        prompt_builder=prompt_builder,
        max_steps=settings.max_steps,
    )
    return ret


def print_trace(user_task: str, result: AgentRunResult) -> None:
    print(f"User task: {user_task}")
    for step in result.steps:
        print(f"\nStep {step.step_index}")
        if step.thought is not None:
            print(f"Thought: {step.thought}")
        if step.action is not None:
            print(f"Action: {step.action}")
        if step.args is not None:
            print(f"Args: {json.dumps(step.args, ensure_ascii=False)}")
        if step.observation is not None:
            print(f"Observation: {json.dumps(step.observation, ensure_ascii=False)}")
        if step.final_answer is not None:
            print(f"Final answer: {step.final_answer}")
    if result.success and result.final_answer is not None:
        print(f"\nDone. Result: {result.final_answer}")
    if not result.success and result.error_message is not None:
        print(f"\nError: {result.error_message}")


def main() -> None:
    configure_logging()
    arg_parser = argparse.ArgumentParser(description="Local Ollama tool agent")
    arg_parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help='Task string (omit for interactive "Enter task")',
    )
    args_ns = arg_parser.parse_args()

    settings = Settings()
    agent = build_agent(settings)

    if args_ns.task is not None:
        user_task = args_ns.task
        if user_task.strip() == "":
            print("No task provided.")
            sys.exit(1)
        result = agent.run(user_task)
        print_trace(user_task, result)
        sys.exit(0 if result.success else 2)

    print("Интерактивный режим: введите задачу и Enter; пустая строка — выход.")
    exit_code = 0
    while True:
        print("\nEnter task:")
        line = sys.stdin.readline()
        if not line:
            break
        user_task = line.rstrip("\n")
        if user_task.strip() == "":
            break
        result = agent.run(user_task)
        print_trace(user_task, result)
        if not result.success:
            exit_code = 2
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
