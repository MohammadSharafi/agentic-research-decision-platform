# Screenshot Guide

## Purpose

Capture **real Streamlit browser screenshots** and **demo result images** for the LaTeX report, Markdown report, and presentation.

Automated capture:

```bash
USE_MOCK_LLM=true python scripts/capture_ui_screenshots.py
```

For real browser screenshots, install Playwright first:

```bash
pip install playwright
python -m playwright install chromium
python scripts/capture_ui_screenshots.py
```

Assets are saved to:

- `report/assets/ui/`
- `report/assets/results/`
- `outputs/screenshots/`

Capture metadata is written to `report/assets/ui/capture_metadata.json` and records whether images are **browser captures** or **fallback documentation renders**.

---

## Launch the Streamlit UI Manually

```bash
streamlit run app/ui/streamlit_app.py
```

Open the local URL (typically `http://localhost:8501`).

### Manual capture steps

1. Select **Mock mode (deterministic)** in the sidebar.
2. Choose a demo topic.
3. Click **Run Agentic Workflow** and wait for success.
4. Capture each tab and save with the exact filenames below.

| Tab to open | Save as |
| --- | --- |
| Overview (after demo run) | `report/assets/ui/ui_home.png` |
| Workflow | `report/assets/ui/ui_workflow.png` |
| Agents | `report/assets/ui/ui_agent_outputs.png` |
| Results | `report/assets/ui/ui_results.png` |
| Figures | `report/assets/ui/ui_figures.png` |
| Downloads | `report/assets/ui/ui_downloads.png` |

Also copy files to `outputs/screenshots/` if desired.

---

## Regenerate Report PDF

After updating screenshots:

```bash
USE_MOCK_LLM=true python scripts/run_demo.py
python scripts/capture_ui_screenshots.py
python scripts/build_report_pdf.py
```

---

## Fallback Behavior

If Playwright is unavailable, the capture script generates **labeled fallback documentation renders** (not real browser screenshots). The LaTeX report states this explicitly using `capture_metadata.json`.

Do not replace fallback images with real screenshots without rerunning the capture script or manual capture workflow.

---

## Demo Result Images

Generated automatically into `report/assets/results/`:

- `demo_evaluation_score.png`
- `demo_agent_workflow_result.png`
- `demo_generated_figures.png`
- `demo_report_output.png`

These are matplotlib summary images derived from real demo workflow output.
