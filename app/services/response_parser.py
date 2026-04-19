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
        # LLMs often add extra keys; a string final_answer ends the turn (even with action/thought).
        if "final_answer" in data:
            fa = data["final_answer"]
            if isinstance(fa, str):
                ret = FinalResponse(final_answer=fa)
                return ret
            if fa is not None:
                msg = "final_answer must be a string or null"
                raise InvalidJsonResponseError(msg)
        if "action" in data:
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
