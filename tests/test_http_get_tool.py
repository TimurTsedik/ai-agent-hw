"""Tests for HttpGetTool."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from app.infrastructure.tools.http_get_tool import HttpGetTool


class TestHttpGetTool(unittest.TestCase):
    def test_successful_get(self) -> None:
        tool = HttpGetTool(timeout_seconds=5.0, max_response_chars=1000)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "hello"
        with patch("app.infrastructure.tools.http_get_tool.requests.get", return_value=mock_resp):
            out = tool.execute({"url": "https://example.com"})
        self.assertTrue(out["ok"])
        self.assertEqual(out["statusCode"], 200)
        self.assertEqual(out["text"], "hello")

    def test_timeout(self) -> None:
        tool = HttpGetTool(timeout_seconds=0.01, max_response_chars=1000)
        with patch("app.infrastructure.tools.http_get_tool.requests.get", side_effect=requests.Timeout("timeout")):
            out = tool.execute({"url": "https://example.com"})
        self.assertFalse(out["ok"])

    def test_invalid_url_string(self) -> None:
        tool = HttpGetTool(timeout_seconds=5.0, max_response_chars=1000)
        out = tool.execute({"url": ""})
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
