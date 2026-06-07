#!/usr/bin/env python3
"""Build report/final_report.pdf from LaTeX source and assets."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app.tools.latex_report_tools import REQUIRED_ASSETS, compile_latex_pdf

REPORT_DIR = PROJECT_DIR / "report"
TEX_PATH = REPORT_DIR / "final_report.tex"
PDF_PATH = REPORT_DIR / "final_report.pdf"
BIB_PATH = REPORT_DIR / "references.bib"
ASSETS_DIR = REPORT_DIR / "assets"


def ensure_prerequisites() -> list[str]:
    errors: list[str] = []
    if not TEX_PATH.exists():
        errors.append(f"Missing LaTeX source: {TEX_PATH}")
    if not BIB_PATH.exists():
        errors.append(f"Missing bibliography: {BIB_PATH}")
    if not ASSETS_DIR.exists():
        errors.append(f"Missing assets directory: {ASSETS_DIR}")
    else:
        for asset in REQUIRED_ASSETS:
            if not (ASSETS_DIR / asset).exists():
                errors.append(f"Missing figure asset: {ASSETS_DIR / asset}")
    return errors


def main() -> int:
    missing = ensure_prerequisites()
    if missing:
        print("ERROR: Report build prerequisites are incomplete:")
        for item in missing:
            print(f"  - {item}")
        print("\nGenerate artifacts first:")
        print("  python scripts/run_demo.py")
        print("  python scripts/generate_latex_report.py")
        return 1

    ok, message = compile_latex_pdf(REPORT_DIR, TEX_PATH.name)
    if ok and PDF_PATH.exists():
        size_kb = PDF_PATH.stat().st_size / 1024
        print(f"SUCCESS: Built {PDF_PATH} ({size_kb:.1f} KB)")
        return 0

    print("ERROR: LaTeX PDF build failed.")
    print(message)
    print("\nInstall a LaTeX distribution providing pdflatex (and optionally latexmk).")
    print("Fallback: report/final_report.md remains available if LaTeX is unavailable.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
