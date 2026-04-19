"""Loaded from environment / .env — OLLAMA_MODEL is the source of truth for the model name."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:4b"
    max_steps: int = 8
    http_timeout_seconds: float = 10.0
    max_http_response_chars: int = 5000
    max_file_size_bytes: int = 1048576
    workspace_path: Path = Path("./workspace")

    @field_validator("workspace_path", mode="before")
    @classmethod
    def coerce_workspace_path(cls, value: str | Path) -> Path:
        ret = Path(value).expanduser()
        return ret
