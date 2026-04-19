"""Tests for ReadFileTool."""

import tempfile
import unittest
from pathlib import Path

from app.infrastructure.tools.read_file_tool import ReadFileTool


class TestReadFileTool(unittest.TestCase):
    def test_successful_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "a.txt"
            target.write_text("line1\nline2\n", encoding="utf-8")
            tool = ReadFileTool(workspace_path=root, max_file_size_bytes=1024)
            out = tool.execute({"path": "a.txt"})
            self.assertTrue(out["ok"])
            self.assertEqual(out["content"], "line1\nline2\n")

    def test_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = ReadFileTool(workspace_path=root, max_file_size_bytes=1024)
            out = tool.execute({"path": "missing.txt"})
            self.assertFalse(out["ok"])

    def test_too_large(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            big = root / "big.txt"
            big.write_bytes(b"x" * 20)
            tool = ReadFileTool(workspace_path=root, max_file_size_bytes=10)
            out = tool.execute({"path": "big.txt"})
            self.assertFalse(out["ok"])
            self.assertIn("large", out["error"].lower())

    def test_escapes_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = ReadFileTool(workspace_path=root, max_file_size_bytes=1024)
            out = tool.execute({"path": "../outside.txt"})
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
