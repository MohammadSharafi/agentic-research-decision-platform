# Submission Checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Project runs | Verified | `python scripts/run_demo.py` completed successfully |
| Mock mode works | Verified | `USE_MOCK_LLM=true` default; deterministic outputs |
| Tests pass | Verified | `pytest -v` — 16 passed |
| Report PDF generated | Verified | `report/final_report.pdf` (LaTeX, 9 pages) |
| LaTeX source included | Verified | `report/final_report.tex` with 28 sections |
| Figures generated | Verified | 9 PNG figures in `report/assets/` plus run-specific outputs |
| References checked | Verified | `report/references.bib` — 23 real sources with DOI/official URLs |
| Presentation generated | Verified | `presentation/final_presentation.md` (19 slides) and `.pptx` |
| PDF build script | Verified | `python scripts/build_report_pdf.py` succeeds |
| Docker checked | Partially verified | `Dockerfile` and `docker-compose.yml` present; validate with `docker-compose config` |
| README complete | Verified | Installation, demo, tests, LaTeX build, limitations documented |
| Known limitations documented | Verified | `docs/LIMITATIONS.md`, report Section 22, README |
| AI usage disclosed | Verified | `docs/AI_USAGE_GUIDE.md` |
| Internal agent guide completed | Verified | `docs/AI_GUIDE.md` |
| README AI transparency | Verified | README `## AI Usage Transparency` |
| Report AI disclosure | Verified | Report section *AI-Assisted Development Disclosure* |
| Presentation AI slide | Verified | Slide *AI Usage and Development Transparency* |

## UI Documentation Checklist

- [x] Streamlit UI runs locally (`streamlit run app/ui/streamlit_app.py`)
- [x] Real UI screenshots captured (`capture_metadata.json` capture_type=browser)
- [x] UI screenshots added to final LaTeX report
- [x] UI screenshots visible in final PDF (1778 KB)
- [x] UI screenshots added to final presentation
- [x] Demo results included in report (`report/assets/results/`)
- [x] User guide updated with UI instructions (`docs/USER_GUIDE.md`)
- [x] Screenshot guide updated (`docs/SCREENSHOT_GUIDE.md`)

## AI Documentation Checklist

- [x] AI usage disclosed in `docs/AI_USAGE_GUIDE.md`
- [x] Internal agent guide completed in `docs/AI_GUIDE.md`
- [x] README includes AI usage transparency
- [x] Report includes AI assistance disclosure
- [x] Presentation includes responsible AI / development transparency slide
- [x] Final verification includes AI usage documentation status

## Reproducibility Commands

```bash
python -m compileall app scripts
python scripts/run_demo.py
python scripts/build_report_pdf.py
pytest -v
```

## Known Limitations

- Default evidence corpus is static for reproducible offline grading
- Live web search and real LLM providers require API keys and adapters
- Not a medical device; not for patient-specific clinical decisions
- Fact checker uses source metadata tags; production needs entailment verification
- LaTeX (`pdflatex` or `latexmk`) required for the polished academic PDF
