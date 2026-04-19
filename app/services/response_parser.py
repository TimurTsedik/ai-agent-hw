"""Maps raw model text to ActionResponse or FinalResponse."""

from __future__ import annotations

from typing import Any

from app.domain.entities.llm_response import ActionResponse, FinalResponse
from app.shared.exceptions import InvalidJsonResponseError
from app.shared.json_utils import parse_json_loose


class ResponseParser:
    """Validates JSON structure for the agent contract."""

    def parse(self, raw_text: str) -> ActionResponse | FinalResponse:
        ret: ActionResponse | FinalResponse
        try:
            data = parse_json_loose(raw_text)
        except (ValueError, TypeError) as exc:
            msg = f"Invalid JSON: {exc}"
            raise InvalidJsonResponseError(msg) from exc
        if not isinstance(data, dict):
            msg = "Model output JSON must be an object"
            raise InvalidJsonResponseError(msg)
        ret = self._parse_dict(data)
        return ret

    def _parse_dict(self, data: dict[str, Any]) -> ActionResponse | FinalResponse:
        has_final = "final_answer" in data
        has_action = "action" in data
        if has_final and has_action:
            msg = "Model output must not mix final_answer and action"
            raise InvalidJsonResponseError(msg)
        if has_final:
            fa = data["final_answer"]
            if not isinstance(fa, str):
                msg = "final_answer must be a string"
                raise InvalidJsonResponseError(msg)
            if len(data) != 1:
                msg = "final_answer object must only contain final_answer"
                raise InvalidJsonResponseError(msg)
            ret = FinalResponse(final_answer=fa)
            return ret
        if has_action:
            thought = data.get("thought")
            action = data.get("action")
            args = data.get("args")
            if not isinstance(thought, str):
                msg = "thought must be a string"
                raise InvalidJsonResponseError(msg)
            if not isinstance(action, str):
                msg = "action must be a string"
                raise InvalidJsonResponseError(msg)
            if args is None:
                args = {}
            if not isinstance(args, dict):
                msg = "args must be an object"
                raise InvalidJsonResponseError(msg)
            ret = ActionResponse(thought=thought, action=action, args=args)
            return ret
        msg = "Model output must include either final_answer or action"
        raise InvalidJsonResponseError(msg)
