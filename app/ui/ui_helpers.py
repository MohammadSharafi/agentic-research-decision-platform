from __future__ import annotations

import json
import os
import re
from pathlib import Path

from app.config.settings import PROJECT_DIR, get_settings
from app.models.schemas import WorkflowState

DEMO_TOPICS: dict[str, str] = {
    "Clinical decision support (default)": (
        "Multi-agent AI systems for trustworthy clinical decision support"
    ),
    "Hallucination mitigation": (
        "Analyze how multi-agent AI systems can improve clinical decision support "
        "while reducing hallucination risks."
    ),
    "Framework comparison": (
        "Compare LangGraph, AutoGen, and CrewAI for evidence-grounded research workflows."
    ),
}

TAB_NAMES: list[str] = [
    "Overview",
    "Workflow",
    "Agents",
    "Results",
    "Figures",
    "Downloads",
    "About",
]

WORKFLOW_PIPELINE: list[tuple[str, str, str]] = [
    ("Planner", "📋", "Decompose the topic into subtasks"),
    ("Research", "🔎", "Retrieve ranked evidence sources"),
    ("Analyst", "📊", "Compute metrics, tables, and formulas"),
    ("Critic", "⚖️", "Review evidence and trigger revision if needed"),
    ("Fact-Checker", "✅", "Ground claims with citation markers"),
    ("Visualization", "🖼️", "Generate diagrams and charts"),
    ("Report Writer", "📝", "Produce Markdown, LaTeX, and PDF"),
    ("Evaluator", "📈", "Score artifact quality with rubric"),
    ("Presentation", "🎞️", "Generate slide deck"),
    ("Memory", "💾", "Persist run metadata to SQLite"),
]

WORKFLOW_STAGES: list[tuple[str, str]] = [
    (name, description) for name, _, description in WORKFLOW_PIPELINE
] + [("Finalize Report", "Refresh report with final evaluation scores")]

AGENT_METADATA: dict[str, dict[str, str]] = {
    "planner_agent": {"label": "Planner", "icon": "📋", "role": "Task decomposition and routing"},
    "research_agent": {"label": "Research", "icon": "🔎", "role": "Evidence retrieval"},
    "analyst_agent": {"label": "Analyst", "icon": "📊", "role": "Metrics and structured analysis"},
    "critic_agent": {"label": "Critic", "icon": "⚖️", "role": "Critique and revision routing"},
    "fact_checker_agent": {"label": "Fact-Checker", "icon": "✅", "role": "Claim grounding"},
    "visualization_agent": {"label": "Visualization", "icon": "🖼️", "role": "Diagram and chart generation"},
    "report_writer_agent": {"label": "Report Writer", "icon": "📝", "role": "Academic report synthesis"},
    "evaluator_agent": {"label": "Evaluator", "icon": "📈", "role": "Rubric scoring"},
    "presentation_agent": {"label": "Presentation", "icon": "🎞️", "role": "Slide deck generation"},
    "memory_agent": {"label": "Memory", "icon": "💾", "role": "SQLite persistence"},
}

ROUTING_NOTES: list[str] = [
    "Critic can route back to Research when evidence is insufficient.",
    "Evaluator can route back to Report Writer when quality score Q < τ (78).",
]

EVALUATION_THRESHOLD = 78

UI_ASSET_DIR = PROJECT_DIR / "report" / "assets" / "ui"
RESULT_ASSET_DIR = PROJECT_DIR / "report" / "assets" / "results"
SCREENSHOT_OUTPUT_DIR = PROJECT_DIR / "outputs" / "screenshots"
UI_CAPTURE_METADATA = UI_ASSET_DIR / "capture_metadata.json"

REQUIRED_UI_SCREENSHOTS = [
    "ui_home.png",
    "ui_workflow.png",
    "ui_agent_outputs.png",
    "ui_results.png",
    "ui_figures.png",
    "ui_downloads.png",
]

REQUIRED_RESULT_IMAGES = [
    "demo_evaluation_score.png",
    "demo_agent_workflow_result.png",
    "demo_generated_figures.png",
    "demo_report_output.png",
]

SCREENSHOT_TAB_MAP = {
    "ui_home.png": "Overview",
    "ui_workflow.png": "Workflow",
    "ui_agent_outputs.png": "Agents",
    "ui_results.png": "Results",
    "ui_figures.png": "Figures",
    "ui_downloads.png": "Downloads",
}


def screenshot_seed_enabled() -> bool:
    return os.environ.get("STREAMLIT_SCREENSHOT_SEED", "").lower() in {"1", "true", "yes"}


def get_output_dir() -> Path:
    return get_settings().output_dir


def resolve_report_path(state: WorkflowState) -> Path | None:
    path = Path(state.report_path) if state.report_path else None
    return path if path and path.exists() else None


def resolve_report_pdf_path(state: WorkflowState) -> Path | None:
    canonical = PROJECT_DIR / "report" / "final_report.pdf"
    if canonical.exists():
        return canonical
    if state.report_pdf_path:
        path = Path(state.report_pdf_path)
        if path.exists():
            return path
    return None


def resolve_presentation_path(state: WorkflowState) -> Path | None:
    path = Path(state.presentation_path) if state.presentation_path else None
    return path if path and path.exists() else None


def resolve_evaluation_paths(state: WorkflowState) -> tuple[Path | None, Path | None]:
    eval_dir = get_output_dir() / "evaluation"
    json_path = eval_dir / f"{state.run_id}_evaluation.json"
    md_path = eval_dir / f"{state.run_id}_evaluation.md"
    return (
        json_path if json_path.exists() else None,
        md_path if md_path.exists() else None,
    )


def list_figure_paths(state: WorkflowState) -> list[Path]:
    paths: list[Path] = []
    for figure in state.figures:
        path = Path(figure.path)
        if path.exists():
            paths.append(path)
    run_dir = get_output_dir() / "figures" / state.run_id
    if run_dir.exists():
        for path in sorted(run_dir.iterdir()):
            if path.suffix.lower() in {".png", ".svg"} and path not in paths:
                paths.append(path)
    return paths


def list_png_figures(state: WorkflowState) -> list[Path]:
    return [path for path in list_figure_paths(state) if path.suffix.lower() == ".png"]


def figure_caption(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").title()


def evaluation_rows(state: WorkflowState) -> list[tuple[str, float]]:
    evaluation = state.evaluation
    return [
        ("Factuality", evaluation.factuality),
        ("Relevance", evaluation.relevance),
        ("Completeness", evaluation.completeness),
        ("Structure", evaluation.structure),
        ("Citation quality", evaluation.citation_quality),
        ("Clarity", evaluation.clarity),
        ("Visual quality", evaluation.visual_quality),
        ("Reproducibility", evaluation.reproducibility),
        ("Total", evaluation.total),
    ]


def evaluation_criteria_rows(state: WorkflowState) -> list[tuple[str, float]]:
    return [row for row in evaluation_rows(state) if row[0] != "Total"]


def agent_output_cards(state: WorkflowState) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for note in state.notes:
        meta = AGENT_METADATA.get(note.agent, {})
        cards.append(
            {
                "agent": note.agent,
                "label": meta.get("label", note.agent.replace("_", " ").title()),
                "icon": meta.get("icon", "🤖"),
                "role": meta.get("role", "Agent execution note"),
                "content": note.content,
                "status": "Completed",
            }
        )
    return cards


def artifact_status(path: Path | None) -> str:
    return "Ready" if path and path.exists() else "Pending"


def load_evaluation_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_read_text(path: Path, limit: int = 12000) -> str:
    return path.read_text(encoding="utf-8")[:limit]


def write_capture_metadata(capture_type: str, details: str) -> None:
    UI_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"capture_type": capture_type, "details": details}
    UI_CAPTURE_METADATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_capture_metadata() -> dict[str, str]:
    if not UI_CAPTURE_METADATA.exists():
        return {"capture_type": "unknown", "details": "No capture metadata found."}
    return json.loads(UI_CAPTURE_METADATA.read_text(encoding="utf-8"))


def ui_screenshot_caption(filename: str) -> str:
    meta = read_capture_metadata()
    capture_type = meta.get("capture_type", "unknown")
    tab = SCREENSHOT_TAB_MAP.get(filename, "interface")
    if capture_type == "browser":
        return f"Actual Streamlit {tab} tab captured in a headless browser after mock demo run."
    if capture_type == "fallback":
        return f"Fallback documentation render of the {tab} tab (browser capture unavailable)."
    return f"Streamlit {tab} tab screenshot for the demonstration interface."


def contains_hardcoded_user_path(text: str) -> bool:
    for line in text.splitlines():
        if "contains_hardcoded_user_path" in line or 'r"/Users/' in line:
            continue
        if re.search(r'["\']/Users/[A-Za-z0-9._-]+', line):
            return True
    return False
