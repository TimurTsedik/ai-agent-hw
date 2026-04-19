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

    def test_mixed_final_and_action(self) -> None:
        raw = '{"final_answer": "a", "action": "calculator"}'
        with self.assertRaises(InvalidJsonResponseError):
            self.parser.parse(raw)


if __name__ == "__main__":
    unittest.main()
