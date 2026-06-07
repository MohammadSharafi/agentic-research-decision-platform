# Project Summary

## Title

**Agentic Research & Decision Intelligence Platform** — A Multi-Agent AI System for Evidence-Grounded Research and Decision Support

## Abstract

This project implements a reproducible multi-agent research platform that transforms a complex query into an evidence-grounded academic report, figures, evaluation artifacts, and presentation. The demonstration topic is multi-agent AI systems for trustworthy clinical decision support. Ten specialized agents collaborate through typed `WorkflowState`, conditional LangGraph routing, critique loops, fact checking, and rubric-based evaluation. The default execution path runs without paid API keys using deterministic mock mode and a local corpus of 23 verified references.

## Main Contribution

The platform demonstrates **inspectable agentic control flow** rather than a single linear prompt chain. Conditional edges allow the Critic to return to Research when evidence is weak and the Evaluator to return to Report Writer when quality is below threshold. After evaluation passes, a finalize-report step regenerates canonical LaTeX/Markdown/PDF artifacts with final scores.

## Architecture Summary

- **Interfaces:** Streamlit UI and FastAPI REST API
- **Orchestration:** LangGraph state graph with deterministic fallback runner
- **Agents:** Planner, Research, Analyst, Critic, Fact-Checker, Visualization, Report Writer, Evaluator, Presentation, Memory
- **Tools:** Search, citation, visualization, LaTeX report compilation, file IO
- **Persistence:** SQLite run memory plus filesystem artifacts under `outputs/`

## Agent List

| Agent | Role |
| --- | --- |
| Planner | Task decomposition |
| Research | Evidence retrieval |
| Analyst | Metrics, tables, formulas |
| Critic | Evidence critique and revision routing |
| Fact-Checker | Claim grounding |
| Visualization | Diagrams and charts |
| Report Writer | Markdown, LaTeX, PDF |
| Evaluator | Rubric scoring |
| Presentation | Slide deck generation |
| Memory | SQLite persistence |

## Technologies Used

Python 3.11+, LangGraph-compatible workflow, FastAPI, Streamlit, SQLite, Pydantic-compatible schemas, Matplotlib, LaTeX (`pdflatex`/`latexmk`), BibTeX, Pytest, Docker Compose

## Evaluation Result

Latest verified demo run: **93.1/100** (artifact-quality rubric, not clinical validation). Confidence score: **95.5/100**. Sources retrieved: **21**. Figures generated: **14**.

## User Interface

A polished Streamlit demo UI (`app/ui/streamlit_app.py`) provides seven tabs (Overview, Workflow, Agents, Results, Figures, Downloads, About) for launching the workflow, reviewing agent outputs, inspecting evaluation scores, previewing figures, and downloading reports and presentations. Real browser screenshots are captured with Playwright into `report/assets/ui/`; demo result summaries are in `report/assets/results/` and embedded in the final PDF report and presentation.

## Output Deliverables

- `report/final_report.tex` — LaTeX source (28 sections, 4 equations, 8 tables, 9 figures)
- `report/final_report.pdf` — Compiled academic PDF
- `report/final_report.md` — Markdown fallback report
- `report/references.bib` — 23 BibTeX references
- `report/assets/` — PNG/SVG figures and Mermaid sources
- `presentation/final_presentation.md` — 19-slide deck
- `presentation/final_presentation.pptx` — PowerPoint artifact
- `outputs/reports/`, `outputs/figures/`, `outputs/evaluation/`, `outputs/presentations/`

## AI-Assisted Development Disclosure

This submission was prepared with transparent use of external AI engineering assistants, including ChatGPT (planning and documentation), Codex-style coding assistants (implementation and tests), Cursor AI (refactoring and report polishing), and NotebookLM (presentation drafting). These tools supported development; they did not replace human responsibility.

The student defined project requirements, directed the multi-agent architecture, reviewed generated code and reports, executed `pytest` and demo verification, validated references and limitations, and prepared final deliverables. The runnable platform additionally implements its own internal ten-agent workflow, which is distinct from the external tools used to build the repository.

Full disclosure: [`docs/AI_USAGE_GUIDE.md`](docs/AI_USAGE_GUIDE.md). Internal agent design: [`docs/AI_GUIDE.md`](docs/AI_GUIDE.md).

## Limitations

- Static mock evidence corpus for reproducible grading
- Metadata-level fact checking (not passage-level entailment)
- Not clinically validated; not a medical device
- Human review required for any high-stakes use
- Real LLM/search providers require optional API keys and adapters
