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


def main() -> None:
    query = " ".join(sys.argv[1:]) or "Multi-agent AI systems for trustworthy clinical decision support"
    state = run_workflow(query, use_mock_llm=True)
    print(state.presentation_path)


if __name__ == "__main__":
    main()
