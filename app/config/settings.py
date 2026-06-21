from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_DIR / "app"
ENV_FILE = PROJECT_DIR / ".env"


def reload_env() -> None:
    """Reload .env so Streamlit reruns can pick up newly edited API keys."""
    load_dotenv(ENV_FILE, override=True)


# Initial load for CLI, tests, FastAPI, and Streamlit startup.
reload_env()


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str
    use_mock_llm: bool
    model_provider: str
    openai_api_key: str
    database_path: Path
    output_dir: Path
    evaluation_threshold: int
    tavily_api_key: str
    serpapi_api_key: str
    log_level: str


def get_settings() -> Settings:
    reload_env()
    settings = Settings(
        app_env=os.getenv("APP_ENV", "local"),
        use_mock_llm=_bool_env("USE_MOCK_LLM", True),
        model_provider=os.getenv("MODEL_PROVIDER", "mock"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        database_path=PROJECT_DIR / os.getenv("DATABASE_PATH", "app/storage/agentic_platform.db"),
        output_dir=PROJECT_DIR / os.getenv("OUTPUT_DIR", "outputs"),
        evaluation_threshold=int(os.getenv("EVALUATION_THRESHOLD", "78")),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        serpapi_api_key=os.getenv("SERPAPI_API_KEY", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
