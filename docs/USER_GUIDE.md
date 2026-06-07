# User Guide

## Start the Streamlit Interface

```bash
streamlit run app/ui/streamlit_app.py
```

The interface is the recommended way to demo the project to a professor. It supports mock mode (default), workflow progress, agent outputs, evaluation review, figure preview, and downloads.

---

## Step-by-Step UI Workflow

### 1. Start the Streamlit app

Run the command above and open the local URL shown in the terminal.

### 2. Enter a topic

Use the sidebar demo topic selector or edit the text area. Example:

```text
Multi-agent AI systems for trustworthy clinical decision support
```

### 3. Select mock mode

Choose **Mock mode (deterministic)** for reproducible grading without API keys. Real LLM mode requires configured provider keys in `.env`.

### 4. Run workflow

Click **Run Agentic Workflow** in the sidebar. Progress and per-agent status messages appear while the graph executes.

### 5. Review workflow

Open the **Workflow** tab to see the pipeline timeline and conditional routing notes.

### 6. Review agent outputs

Open the **Agents** tab to inspect agent cards (planner, research, critic, evaluator, etc.).

### 7. Review evaluation score

Open the **Results** tab for the total score, progress bars, and rubric table.

### 8. Preview figures

Open the **Figures** tab to view the figure gallery with captions.

### 9. Download final report

Open the **Downloads** tab to download:

- Markdown report
- PDF report (when available)
- Presentation (PPTX or Markdown)
- Evaluation JSON

---

## Interface Tabs

| Tab | Purpose |
| --- | --- |
| Overview | Run metrics, workflow summary, run ID |
| Agent Workflow | Execution plan and graph stages |
| Agent Outputs | Expandable agent note cards |
| Results | Evaluation dataframe and downloads |
| Figures | PNG figure previews |
| Downloads | Report, PDF, presentation, evaluation files |
| About | Commands, limitations, academic disclaimer |

---

## CLI Alternative

```bash
USE_MOCK_LLM=true python scripts/run_demo.py
```

This generates the same artifacts without the UI.

---

## Capture UI Screenshots for the Report

```bash
python scripts/capture_ui_screenshots.py
```

See [`docs/SCREENSHOT_GUIDE.md`](SCREENSHOT_GUIDE.md) for required filenames and manual capture steps.

---

## Interpret Evaluation Scores

Scores range from 0 to 100:

- 90–100: strong prototype artifact
- 80–89: good artifact with minor gaps
- 70–79: acceptable but should be revised
- Below 70: major gaps in evidence, structure, or reproducibility

The score measures **artifact quality**, not clinical validation.

---

## Important Notes

- Mock mode uses a **static local corpus** for reproducibility.
- The clinical demo is **academic only** and not medical advice.
- Human review is required before any high-stakes use.
