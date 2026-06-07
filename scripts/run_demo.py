from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("USE_MOCK_LLM", "true")
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / "outputs" / "logs" / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(PROJECT_DIR / "outputs" / "logs" / "cache"))

from app.graph.workflow import run_workflow


DEMO_TOPIC = "Multi-agent AI systems for trustworthy clinical decision support"


def main() -> None:
    state = run_workflow(DEMO_TOPIC, use_mock_llm=True)
    print(f"Run ID: {state.run_id}")
    print(f"Status: {state.status}")
    print(f"Report: {state.report_path}")
    print(f"Report PDF: {state.report_pdf_path}")
    print(f"Presentation: {state.presentation_path}")
    print(f"Evaluation: {state.evaluation.total}/100")
    print(f"Figures: {len(state.figures)}")


if __name__ == "__main__":
    main()
