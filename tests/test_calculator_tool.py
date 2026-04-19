"""Tests for CalculatorTool."""

import unittest

from app.infrastructure.tools.calculator_tool import CalculatorTool


class TestCalculatorTool(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = CalculatorTool()

    def test_simple(self) -> None:
        out = self.tool.execute({"expression": "1 + 2"})
        self.assertTrue(out["ok"])
        self.assertEqual(out["result"], 3)

    def test_parens(self) -> None:
        out = self.tool.execute({"expression": "(123 + 456) * 2"})
        self.assertTrue(out["ok"])
        self.assertEqual(out["result"], 1158)

    def test_invalid_expression(self) -> None:
        out = self.tool.execute({"expression": "1 + * 2"})
        self.assertFalse(out["ok"])
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
