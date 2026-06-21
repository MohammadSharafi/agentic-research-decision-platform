from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / "outputs" / "logs" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_DIR / "outputs" / "logs" / "cache"))

from app.config.settings import get_settings
from app.graph.workflow import run_workflow


DEFAULT_QUERY = "Compare Iran and Turkey across economy, healthcare, education, technology, and geopolitical risk."


def existing_path(value: str) -> str:
    path = Path(value) if value else None
    if path and path.exists():
        return str(path.resolve())
    return value or "not generated"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the agentic workflow in real, non-mock mode.")
    parser.add_argument("query", nargs="*", help="Research or comparison prompt.")
    parser.add_argument("--show-sources", action="store_true", help="Print retrieved source titles and URLs.")
    args = parser.parse_args()

    query = " ".join(args.query).strip() or DEFAULT_QUERY
    settings = get_settings()
    if not (settings.openai_api_key or settings.tavily_api_key or settings.serpapi_api_key):
        print("Warning: no OpenAI, Tavily, or SerpAPI key is configured; real mode will use dynamic fallbacks.")

    state = run_workflow(query, use_mock_llm=False)
    print(f"Run ID: {state.run_id}")
    print(f"Status: {state.status}")
    print(f"Score: {state.evaluation.total}/100")
    print(f"Sources: {len(state.sources)}")
    print(f"Report Markdown: {existing_path(state.report_path)}")
    print(f"Report PDF: {existing_path(state.report_pdf_path)}")
    print(f"Presentation: {existing_path(state.presentation_path)}")
    print(f"Canonical PDF copy: {(PROJECT_DIR / 'report' / 'final_report.pdf').resolve()}")

    if args.show_sources:
        for index, source in enumerate(state.sources, start=1):
            print(f"{index}. {source.title} ({source.url})")

    return 0 if state.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
