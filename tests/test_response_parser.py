"""Tests for ResponseParser."""

import unittest

from app.domain.entities.llm_response import ActionResponse, FinalResponse
from app.services.response_parser import ResponseParser
from app.shared.exceptions import InvalidJsonResponseError


class TestResponseParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ResponseParser()

    def test_action_json(self) -> None:
        raw = """
        {"thought": "calc", "action": "calculator", "args": {"expression": "1+1"}}
        """
        out = self.parser.parse(raw)
        self.assertIsInstance(out, ActionResponse)
        self.assertEqual(out.action, "calculator")
        self.assertEqual(out.args["expression"], "1+1")

    def test_final_json(self) -> None:
        raw = '{"final_answer": "done"}'
        out = self.parser.parse(raw)
        self.assertIsInstance(out, FinalResponse)
        self.assertEqual(out.final_answer, "done")

    def test_invalid_json(self) -> None:
        raw = "not json"
        with self.assertRaises(InvalidJsonResponseError):
            self.parser.parse(raw)

    def test_missing_fields(self) -> None:
        raw = '{"thought": "x"}'
        with self.assertRaises(InvalidJsonResponseError):
            self.parser.parse(raw)

    def test_mixed_final_and_action_prefers_final(self) -> None:
        """Models often emit redundant keys; a string final_answer ends the turn."""
        raw = '{"thought": "done", "action": "calculator", "final_answer": "Страница открыта."}'
        out = self.parser.parse(raw)
        self.assertIsInstance(out, FinalResponse)
        self.assertEqual(out.final_answer, "Страница открыта.")

    def test_final_answer_with_extra_keys(self) -> None:
        raw = '{"thought": "ok", "final_answer": "result"}'
        out = self.parser.parse(raw)
        self.assertIsInstance(out, FinalResponse)
        self.assertEqual(out.final_answer, "result")

    def test_null_final_answer_falls_through_to_action(self) -> None:
        raw = (
            '{"thought": "t", "action": "calculator", "args": {"expression": "1+1"}, '
            '"final_answer": null}'
        )
        out = self.parser.parse(raw)
        self.assertIsInstance(out, ActionResponse)
        self.assertEqual(out.action, "calculator")


if __name__ == "__main__":
    unittest.main()
