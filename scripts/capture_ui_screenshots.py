#!/usr/bin/env python3
"""Capture real Streamlit UI screenshots and professional demo result images."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault("USE_MOCK_LLM", "true")
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_DIR / "outputs" / "logs" / "matplotlib"))

from app.graph.workflow import run_workflow
from app.tools.file_tools import ensure_dir
from app.ui.ui_helpers import (
    REQUIRED_RESULT_IMAGES,
    REQUIRED_UI_SCREENSHOTS,
    RESULT_ASSET_DIR,
    SCREENSHOT_OUTPUT_DIR,
    SCREENSHOT_TAB_MAP,
    UI_ASSET_DIR,
    WORKFLOW_PIPELINE,
    evaluation_criteria_rows,
    list_png_figures,
    write_capture_metadata,
)

PLAYWRIGHT_INSTALL = """Playwright is not installed. For real browser screenshots run:
  pip install playwright
  python -m playwright install chromium
Then rerun:
  python scripts/capture_ui_screenshots.py
"""


def _matplotlib_available() -> bool:
    try:
        import matplotlib  # noqa: F401

        return True
    except Exception:
        return False


def _copy_asset(path: Path) -> None:
    ensure_dir(SCREENSHOT_OUTPUT_DIR)
    (SCREENSHOT_OUTPUT_DIR / path.name).write_bytes(path.read_bytes())


def _strip_inline_markdown(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return " ".join(text.split())


def _report_preview_text(state, report_md: Path, wrap_width: int = 76) -> str:
    topic = _strip_inline_markdown(state.query or "Research topic")
    lines = [
        "Agentic Research & Decision Intelligence Platform",
        "Final Course Project Report",
        "",
        f"Topic: {topic}",
        f"Run ID: {state.run_id}",
        f"Quality score: {state.evaluation.total}/100",
        f"Sources: {len(state.sources)}  |  Figures: {len(state.figures)}",
        "",
        "Abstract",
        "-" * wrap_width,
    ]

    abstract = ""
    section_titles: list[str] = []
    if report_md.exists():
        md_text = report_md.read_text(encoding="utf-8")
        if "## Abstract" in md_text:
            abstract = md_text.split("## Abstract", 1)[1].split("\n##", 1)[0].strip()
            abstract = _strip_inline_markdown(abstract)
        for raw in md_text.splitlines():
            if raw.startswith("## "):
                title = _strip_inline_markdown(raw[3:].strip())
                if title.lower() != "abstract":
                    section_titles.append(title)

    if not abstract:
        abstract = (
            "Multi-agent evidence-grounded research report with critique loops, "
            "claim checks, figures, LaTeX/PDF output, and presentation artifacts."
        )
    lines.append(textwrap.fill(abstract, width=wrap_width))
    lines.extend(["", "Included sections", "-" * wrap_width])
    for title in section_titles[:8]:
        lines.append(f"  {title}")
    if len(section_titles) > 8:
        lines.append(f"  … and {len(section_titles) - 8} more sections")
    return "\n".join(lines)


def generate_result_images(state) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import image as mpimg

    ensure_dir(RESULT_ASSET_DIR)
    ensure_dir(SCREENSHOT_OUTPUT_DIR / "results")
    created: list[Path] = []
    palette = "#2f6f73"

    rows = evaluation_criteria_rows(state)
    labels = [row[0] for row in rows]
    values = [row[1] for row in rows]
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(labels, values, color=palette, height=0.62)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score", fontsize=12)
    ax.set_title(f"Demo Evaluation Scores — Total {state.evaluation.total}/100", fontsize=16, weight="bold")
    ax.axvline(78, color="#c44e52", linestyle="--", linewidth=1.5, label="Threshold τ = 78")
    for bar, value in zip(bars, values):
        ax.text(value + 1, bar.get_y() + bar.get_height() / 2, f"{value}", va="center", fontsize=11)
    ax.legend(loc="lower right")
    fig.tight_layout()
    eval_path = RESULT_ASSET_DIR / "demo_evaluation_score.png"
    fig.savefig(eval_path, dpi=180, facecolor="white")
    plt.close(fig)
    created.append(eval_path)
    _copy_asset(eval_path)
    (SCREENSHOT_OUTPUT_DIR / "results" / eval_path.name).write_bytes(eval_path.read_bytes())

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.axis("off")
    ax.set_title("Demo Agent Workflow Result", fontsize=18, weight="bold", pad=16)
    lines = [
        f"Run ID: {state.run_id}",
        f"Status: {state.status}",
        f"Sources retrieved: {len(state.sources)}",
        f"Figures generated: {len(state.figures)}",
        f"Evaluation score: {state.evaluation.total}/100",
        "",
        "Workflow pipeline:",
    ]
    lines.extend(f"  {idx + 1}. {agent} — {desc}" for idx, (agent, _icon, desc) in enumerate(WORKFLOW_PIPELINE))
    ax.text(0.04, 0.95, "\n".join(lines), va="top", fontsize=12, family="sans-serif")
    workflow_path = RESULT_ASSET_DIR / "demo_agent_workflow_result.png"
    fig.savefig(workflow_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    created.append(workflow_path)

    png_paths = list_png_figures(state)[:4]
    if png_paths:
        fig, axes = plt.subplots(2, 2, figsize=(12, 9))
        for ax, path in zip(axes.flatten(), png_paths):
            ax.imshow(mpimg.imread(path))
            ax.set_title(path.stem.replace("_", " ").title(), fontsize=12, weight="bold")
            ax.axis("off")
        for ax in axes.flatten()[len(png_paths) :]:
            ax.axis("off")
        fig.suptitle("Demo Generated Figures", fontsize=18, weight="bold")
        fig.tight_layout()
        figures_path = RESULT_ASSET_DIR / "demo_generated_figures.png"
        fig.savefig(figures_path, dpi=180, facecolor="white")
        plt.close(fig)
        created.append(figures_path)

    report_md = PROJECT_DIR / "report" / "final_report.md"
    preview_text = _report_preview_text(state, report_md)
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.9), 0.96, 0.08, transform=ax.transAxes, color="#2f6f73", zorder=0))
    ax.text(
        0.5,
        0.94,
        "Demo Report Output Preview",
        ha="center",
        va="center",
        fontsize=16,
        weight="bold",
        color="white",
        transform=ax.transAxes,
    )
    ax.text(
        0.05,
        0.86,
        preview_text,
        va="top",
        fontsize=10.5,
        family="sans-serif",
        linespacing=1.45,
        transform=ax.transAxes,
    )
    report_path = RESULT_ASSET_DIR / "demo_report_output.png"
    fig.savefig(report_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    created.append(report_path)
    _copy_asset(report_path)
    (SCREENSHOT_OUTPUT_DIR / "results" / report_path.name).write_bytes(report_path.read_bytes())

    return created


def generate_fallback_ui_images(state) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ensure_dir(UI_ASSET_DIR)
    created: list[Path] = []

    def save_panel(filename: str, title: str, body: str) -> Path:
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0.9), 1, 0.1, transform=ax.transAxes, color="#2f6f73"))
        ax.text(0.03, 0.945, "FALLBACK DOCUMENTATION RENDER — NOT A BROWSER SCREENSHOT", color="white", fontsize=11, weight="bold", transform=ax.transAxes)
        ax.text(0.03, 0.82, title, fontsize=18, weight="bold", transform=ax.transAxes)
        ax.text(0.03, 0.74, body, fontsize=11, va="top", family="monospace", transform=ax.transAxes)
        path = UI_ASSET_DIR / filename
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        _copy_asset(path)
        created.append(path)
        return path

    save_panel("ui_home.png", "Overview", f"Evaluation: {state.evaluation.total}/100 | Sources: {len(state.sources)}")
    save_panel("ui_workflow.png", "Workflow", "Planner → Research → Analyst → Critic → Fact-Checker → Visualization → Report Writer → Evaluator → Presentation → Memory")
    save_panel("ui_agent_outputs.png", "Agents", "\n".join(f"{n.agent}: {n.content[:80]}" for n in state.notes[:6]))
    save_panel("ui_results.png", "Results", "\n".join(f"{n}: {s}" for n, s in evaluation_criteria_rows(state)))
    save_panel("ui_figures.png", "Figures", "\n".join(p.name for p in list_png_figures(state)[:6]))
    save_panel("ui_downloads.png", "Downloads", f"Report: {state.report_path}\nPresentation: {state.presentation_path}")
    write_capture_metadata("fallback", "Documentation renders generated because browser capture was unavailable.")
    return created


def _wait_for_streamlit(port: int, timeout: int = 120) -> bool:
    import urllib.error
    import urllib.request

    deadline = time.time() + timeout
    urls = [
        f"http://127.0.0.1:{port}/_stcore/health",
        f"http://127.0.0.1:{port}/",
    ]
    while time.time() < deadline:
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=3) as resp:
                    if resp.status == 200:
                        return True
            except urllib.error.HTTPError as exc:
                if exc.code in {200, 301, 302}:
                    return True
            except Exception:
                continue
        time.sleep(2)
    return False


def capture_with_playwright(state, port: int = 8511) -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return False, f"{PLAYWRIGHT_INSTALL}\nDetails: {exc}"

    env = os.environ.copy()
    env["USE_MOCK_LLM"] = "true"
    env["STREAMLIT_SCREENSHOT_SEED"] = "1"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_DIR / "app" / "ui" / "streamlit_app.py"),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
        "--browser.gatherUsageStats",
        "false",
    ]
    proc = subprocess.Popen(cmd, cwd=PROJECT_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        if not _wait_for_streamlit(port, timeout=90):
            output = ""
            if proc.stdout is not None:
                try:
                    output = proc.stdout.read(4000) or ""
                except Exception:
                    output = ""
            return False, f"Streamlit server did not become healthy in time.\n{output[-2000:]}"

        ensure_dir(UI_ASSET_DIR)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(f"http://127.0.0.1:{port}", wait_until="domcontentloaded", timeout=120000)
            try:
                page.wait_for_selector("text=Total evaluation score", timeout=180000)
            except Exception:
                page.wait_for_selector("text=Mock Mode Available", timeout=30000)
                page.wait_for_timeout(45000)

            for filename, tab_name in SCREENSHOT_TAB_MAP.items():
                page.get_by_role("tab", name=tab_name).click()
                page.wait_for_timeout(1500)
                target = UI_ASSET_DIR / filename
                page.screenshot(path=str(target), full_page=True)
                _copy_asset(target)

            browser.close()

        write_capture_metadata("browser", f"Captured with Playwright/Chromium on port {port} after seeded mock demo.")
        return True, f"Captured {len(SCREENSHOT_TAB_MAP)} browser screenshots via Playwright."
    except Exception as exc:
        return False, f"Playwright capture failed: {exc}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> int:
    if not _matplotlib_available():
        print("ERROR: matplotlib is required.")
        return 1

    print("Running demo workflow for assets...")
    state = run_workflow(
        "Multi-agent AI systems for trustworthy clinical decision support",
        use_mock_llm=True,
    )
    print(f"Run ID: {state.run_id} | Evaluation: {state.evaluation.total}/100")

    result_paths = generate_result_images(state)
    print(f"Generated {len(result_paths)} result images in {RESULT_ASSET_DIR}")

    browser_ok, browser_msg = capture_with_playwright(state)
    print(browser_msg)

    if not browser_ok:
        print("Falling back to labeled documentation renders...")
        generate_fallback_ui_images(state)

    missing_ui = [name for name in REQUIRED_UI_SCREENSHOTS if not (UI_ASSET_DIR / name).exists()]
    missing_results = [name for name in REQUIRED_RESULT_IMAGES if not (RESULT_ASSET_DIR / name).exists()]
    if missing_ui or missing_results:
        print("WARNING: Missing assets:")
        for name in missing_ui + missing_results:
            print(f"  - {name}")
        return 1

    meta_path = UI_ASSET_DIR / "capture_metadata.json"
    print(f"Capture metadata: {meta_path.read_text(encoding='utf-8').strip()}")
    print("SUCCESS: UI and result assets are ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
