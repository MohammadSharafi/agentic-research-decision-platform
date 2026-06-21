from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_DIR / "app"

# Load local secrets from .env when running Streamlit, FastAPI, tests, or CLI scripts.
# Environment variables already exported in the shell still take priority.
load_dotenv(PROJECT_DIR / ".env", override=False)


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "local")
    use_mock_llm: bool = _bool_env("USE_MOCK_LLM", True)
    model_provider: str = os.getenv("MODEL_PROVIDER", "mock")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    database_path: Path = PROJECT_DIR / os.getenv("DATABASE_PATH", "app/storage/agentic_platform.db")
    output_dir: Path = PROJECT_DIR / os.getenv("OUTPUT_DIR", "outputs")
    evaluation_threshold: int = int(os.getenv("EVALUATION_THRESHOLD", "78"))
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    serpapi_api_key: str = os.getenv("SERPAPI_API_KEY", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def get_settings() -> Settings:
    settings = Settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
