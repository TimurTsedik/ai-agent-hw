"""Safe arithmetic evaluation without arbitrary code execution."""

from __future__ import annotations

import ast
import operator
from typing import Any


class CalculatorTool:
    """Evaluates + - * / and parentheses on numbers."""

    _OPS: dict[type[ast.AST], Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    @property
    def name(self) -> str:
        ret = "calculator"
        return ret

    def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        raw = args.get("expression")
        if not isinstance(raw, str):
            return {"ok": False, "error": "Missing or invalid 'expression' (string required)"}
        ret: dict[str, Any]
        try:
            value = self._eval_expression(raw)
            ret = {"ok": True, "result": value}
        except (ValueError, ZeroDivisionError, TypeError, SyntaxError) as exc:
            ret = {"ok": False, "error": str(exc)}
        return ret

    def _eval_expression(self, source: str) -> int | float:
        tree = ast.parse(source, mode="eval")
        if not isinstance(tree, ast.Expression):
            msg = "Invalid expression"
            raise ValueError(msg)
        ret = self._eval_node(tree.body)
        return ret

    def _eval_node(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                msg = "Boolean not allowed in expression"
                raise ValueError(msg)
            if isinstance(node.value, (int, float)):
                return node.value
            msg = "Only numeric constants are allowed"
            raise ValueError(msg)
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type not in {ast.Add, ast.Sub, ast.Mult, ast.Div}:
                msg = "Operator not allowed"
                raise ValueError(msg)
            func = self._OPS[type(node.op)]
            ret = func(left, right)
            return ret
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type not in {ast.UAdd, ast.USub}:
                msg = "Unary operator not allowed"
                raise ValueError(msg)
            func = self._OPS[type(node.op)]
            ret = func(operand)
            return ret
        msg = "Unsupported syntax in expression"
        raise ValueError(msg)
