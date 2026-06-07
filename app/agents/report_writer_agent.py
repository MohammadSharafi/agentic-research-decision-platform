from __future__ import annotations

from pathlib import Path

from app.config.settings import PROJECT_DIR, get_settings
from app.models.schemas import WorkflowState
from app.tools.citation_tools import numbered_references
from app.tools.file_tools import copy_file, ensure_dir, write_text
from app.ui.ui_helpers import REQUIRED_RESULT_IMAGES, REQUIRED_UI_SCREENSHOTS
from app.tools.latex_report_tools import generate_latex_report
from app.tools.report_tools import markdown_table, markdown_to_simple_pdf


class ReportWriterAgent:
    name = "report_writer_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        settings = get_settings()
        report_dir = ensure_dir(settings.output_dir / "reports")
        report_path = report_dir / f"{state.run_id}_final_report.md"
        canonical_md = PROJECT_DIR / "report" / "final_report.md"
        canonical_pdf = PROJECT_DIR / "report" / "final_report.pdf"
        references_path = PROJECT_DIR / "report" / "references.bib"

        sections = self._build_report(state)
        write_text(report_path, sections)
        write_text(canonical_md, sections)
        self._sync_screenshot_assets(report_dir)
        if not references_path.exists() or references_path.read_text(encoding="utf-8").count("@") < 20:
            write_text(references_path, self._build_bibtex(state))
        run_pdf = report_dir / f"{state.run_id}_final_report.pdf"
        _, latex_pdf, latex_ok, latex_message = generate_latex_report(state, PROJECT_DIR / "report", run_pdf)
        if latex_ok:
            canonical_pdf = latex_pdf
        else:
            markdown_to_simple_pdf(sections, canonical_pdf, "Agentic Research & Decision Intelligence Platform")
            copy_file(canonical_pdf, run_pdf)

        state.report_path = str(report_path)
        state.report_pdf_path = str(run_pdf)
        state.status = "reported"
        state.add_note(self.name, f"Wrote final report to {report_path} and PDF to {run_pdf}.", latex_pdf=latex_ok, latex_message=latex_message)
        return state

    def _build_report(self, state: WorkflowState) -> str:
        table_blocks = [
            f"**Table {idx}. {table.title}**\n\n{markdown_table(table.columns, table.rows)}"
            for idx, table in enumerate(state.tables, start=1)
        ]
        figure_lines = []
        for idx, figure in enumerate(state.figures, start=1):
            rel = Path(figure.path).name
            if figure.figure_type == "mermaid":
                figure_lines.append(f"**Figure {idx}. {figure.title}.** See `report/assets/{rel}` for Mermaid source.")
            else:
                figure_lines.append(f"**Figure {idx}. {figure.title}.**\n\n![{figure.title}](assets/{rel})")

        claim_lines = []
        for check in state.claim_checks:
            citations = "; ".join(check.citations) if check.citations else "not supported by retrieved sources"
            status = "Supported" if check.supported else "Unsupported"
            claim_lines.append(f"- **{status}:** {check.claim} {citations}. {check.note}")

        critique = "\n".join(f"- {item}" for item in state.critique)
        formulas = state.analysis.get("formulas", [])
        references = numbered_references(state.sources)
        confidence = state.analysis.get("confidence_score", 0)
        source_count = state.analysis.get("source_count", 0)
        task_formula = formulas[0] if formulas else r"T = \{t_1, t_2, ..., t_n\}"
        confidence_formula = (
            formulas[1]
            if len(formulas) > 1
            else r"C = \frac{\sum_{i=1}^{n} w_i s_i}{\sum_{i=1}^{n} w_i}"
        )
        evaluation_formula = (
            formulas[2]
            if len(formulas) > 2
            else r"Q = \alpha F + \beta R + \gamma S + \delta C"
        )
        agent_table = table_blocks[0] if len(table_blocks) > 0 else ""
        framework_table = table_blocks[1] if len(table_blocks) > 1 else ""
        api_table = table_blocks[2] if len(table_blocks) > 2 else ""
        rubric_table = table_blocks[3] if len(table_blocks) > 3 else ""
        limitations_table = table_blocks[4] if len(table_blocks) > 4 else ""
        evaluation_table = table_blocks[5] if len(table_blocks) > 5 else ""
        eval_score = state.evaluation.total
        claim_check_text = "\n".join(claim_lines)
        figure_text = "\n".join(figure_lines)

        return f"""# Agentic Research & Decision Intelligence Platform

**Final Course Project Report**  
**Topic:** {state.query}  
**Mode:** {"Deterministic mock/offline mode" if state.use_mock_llm else "External model/search capable mode"}  
**Run ID:** `{state.run_id}`  
**Final quality score:** {eval_score}/100  
**Confidence score:** {confidence}/100

## Abstract

This report documents the Agentic Research & Decision Intelligence Platform, a multi-agent system that transforms a complex research query into an evidence-grounded academic report, figures, evaluation artifacts, and presentation. Ten specialized agents plan, retrieve, analyze, critique, verify, visualize, write, evaluate, present, and persist results through typed `WorkflowState` and conditional LangGraph routing. The default path is fully reproducible via `USE_MOCK_LLM=true`, a local corpus of verified references, Pytest coverage, and one-command demo scripts.

## 1. Introduction

Research and decision-support tasks require inspectable planning, retrieval, critique, and citation grounding—not only fluent prose. This project implements a multi-agent platform for trustworthy clinical decision support as a demanding demonstration scenario.

## 2. Problem Statement

Given a broad topic, the system must produce a professional evidence-grounded report and presentation with task decomposition, ranked retrieval, critique loops, claim checks, figures, LaTeX/PDF output, rubric evaluation, and persistent memory—without paid API keys in the grading path.

## 3. Motivation

Clinical decision support illustrates high-stakes requirements: workflow fit, governance, and hallucination risk control matter as much as model fluency.

## 4. Related Work

The design draws on retrieval-augmented generation, ReAct-style tool use, Reflexion/Self-Refine critique loops, multi-agent frameworks (LangGraph, AutoGen, CrewAI, Semantic Kernel, Google ADK), and clinical AI reporting guidance (CONSORT-AI, SPIRIT-AI, DECIDE-AI).

## 5. System Overview

Five layers: Streamlit/FastAPI interfaces, graph orchestration, specialized agents, tool adapters, and SQLite/filesystem outputs.

{figure_lines[0] if len(figure_lines) > 0 else ""}

## 6. Multi-Agent Architecture

Ten agents collaborate through `WorkflowState`. Figure below shows shared-state communication.

{figure_lines[2] if len(figure_lines) > 2 else ""}

{agent_table}

## 7. Agent Roles and Responsibilities

Planner decomposes; Research retrieves; Analyst structures metrics; Critic challenges evidence; Fact-Checker grounds claims; Visualization renders diagrams; Report Writer compiles Markdown/LaTeX/PDF; Evaluator scores rubric; Presentation produces slides; Memory persists runs.

## 8. LangGraph Workflow Design

Conditional edges enable research revision and report revision loops.

{figure_lines[1] if len(figure_lines) > 1 else ""}

{figure_lines[3] if len(figure_lines) > 3 else ""}

## 9. Agentic Behavior and Conditional Routing

`route_after_critic` returns `research` when evidence is weak; `route_after_evaluator` returns `report` when quality score Q < τ (τ = 78).

## 10. State Management and Memory

Serializable `WorkflowState` and SQLite run records support API inspection via `GET /runs/{{run_id}}` without hidden cross-run prompt conditioning.

## 11. Tool-Use Design

Deterministic tools handle search, citations, visualization, LaTeX compilation, and safe file IO. Agents remain orchestration-focused.

## 12. Retrieval and Citation Strategy

The mock corpus contains **{source_count}** references. Retrieval ranks by keyword overlap and credibility; the fact checker uses only sources already in state.

## 13. Mathematical Formulation

Task decomposition:

```latex
{task_formula}
```

Weighted confidence:

```latex
{confidence_formula}
```

Overall quality (demo confidence: **{confidence}/100**):

```latex
{evaluation_formula}
```

Revision decision:

```latex
r = \\begin{{cases}} 1, & Q < \\tau \\\\ 0, & Q \\geq \\tau \\end{{cases}}
```

## 14. Implementation Details

Python modules under `app/agents`, `app/graph`, `app/tools`, `app/models`, `app/storage`, `app/api`, and `app/ui`. LangGraph compiles when installed; fallback runner preserves routing semantics.

## 15. FastAPI Backend Design

{api_table}

## 16. User Interface and Demonstration

A polished Streamlit interface (`app/ui/streamlit_app.py`) provides a professor-friendly demo surface. Users enter a topic, select mock or real mode, launch the workflow, inspect agent cards, review rubric scores with progress bars, preview figures, and download PDF/Markdown reports, presentations, and evaluation files.

**Tabs:** Overview | Workflow | Agents | Results | Figures | Downloads | About

**Why the UI matters:** It makes multi-agent behavior inspectable during grading and live demonstration.

**Launch:**

```bash
streamlit run app/ui/streamlit_app.py
```

**Capture assets:**

```bash
python scripts/capture_ui_screenshots.py
```

![Actual Streamlit overview interface](assets/ui/ui_home.png)

![Workflow tab with pipeline timeline](assets/ui/ui_workflow.png)

![Agents tab with agent output cards](assets/ui/ui_agent_outputs.png)

![Results tab with evaluation breakdown](assets/ui/ui_results.png)

![Figures tab gallery preview](assets/ui/ui_figures.png)

![Downloads tab with artifact download buttons](assets/ui/ui_downloads.png)

**Demo result summaries** (generated from the mock workflow run):

![Demo evaluation score summary](assets/results/demo_evaluation_score.png)

![Demo workflow result summary](assets/results/demo_agent_workflow_result.png)

![Demo generated figures preview](assets/results/demo_generated_figures.png)

![Demo report output preview](assets/results/demo_report_output.png)

Mock mode uses a local deterministic corpus. The clinical demo is academic only and not medical advice. See `report/assets/ui/capture_metadata.json` for whether UI images are browser captures or fallback documentation renders.

## 17. Report Generation Pipeline

{figure_lines[4] if len(figure_lines) > 4 else ""}

Canonical outputs: `report/final_report.tex`, `report/final_report.pdf`, `report/final_report.md`. Build PDF with `python scripts/build_report_pdf.py`.

## 18. Evaluation Methodology

{figure_lines[5] if len(figure_lines) > 5 else ""}

{rubric_table}

{evaluation_table}

## 19. Results

Retrieved **{source_count}** sources, generated **{len(state.figures)}** figures, final score **{eval_score}/100**.

{figure_lines[6] if len(figure_lines) > 6 else ""}

{figure_lines[7] if len(figure_lines) > 7 else ""}

## 20. Testing and Reproducibility

Run `python -m compileall app scripts`, `python scripts/run_demo.py`, `python scripts/build_report_pdf.py`, and `pytest -v`.

## 21. Error Analysis

Expected errors: stale evidence, incomplete retrieval, weak claim alignment, overconfident clinical wording. Mitigations: critique loops, claim checks, limitations, evaluator thresholds, human review.

## 22. Limitations

{limitations_table}

## AI-Assisted Development Disclosure

This submission was developed with external AI engineering assistants used transparently as development aids—not as unsupervised authors. The student defined requirements, directed architecture, reviewed outputs, ran tests, and prepared final deliverables.

| Tool | Purpose | Human Oversight |
| --- | --- | --- |
| ChatGPT | Planning, architecture, documentation, prompt engineering | Student reviewed and refined outputs |
| Codex-style assistant | Code generation, tests, scripts, docs | Student tested and validated implementation |
| Cursor AI | Refactoring, report polishing, LaTeX improvement | Student supervised edits and verified behavior |
| NotebookLM | Presentation drafting and speaker notes | Student reviewed and adapted slides |

**Development AI vs. project AI:** External tools helped *build* the repository. The implemented platform also contains **internal runtime agents** (Planner, Research, Analyst, Critic, Fact-Checker, Visualization, Report Writer, Evaluator, Presentation, Memory) orchestrated at execution time. See `docs/AI_USAGE_GUIDE.md` and `docs/AI_GUIDE.md`.

> AI tools were used as development assistants. The student directed the project requirements, reviewed the generated outputs, tested the system, selected the architecture, validated the deliverables, and prepared the final submission.

## 23. Ethical Considerations

Not a medical device. No patient-specific diagnosis. Requires governance, PHI controls, and clinician responsibility in any real deployment.

## 24. Future Work

Live retrieval, vector stores, entailment-based fact checking, human-in-the-loop approval, async jobs, and formal clinical evaluation.

## 25. Conclusion

The platform demonstrates graph-based multi-agent orchestration producing transparent, evidence-grounded academic deliverables suitable for university evaluation.

## 26. Framework Comparison

{framework_table}

## 27. Claim Checks

{claim_check_text}

## 28. Figures Appendix

{figure_text}

## Critic Notes

{critique}

## References

See `report/references.bib` for BibTeX entries. Retrieved sources in this run:

{references}
"""

    def _sync_screenshot_assets(self, run_report_dir: Path) -> None:
        """Copy UI and demo result screenshots so run-specific Markdown renders images."""
        asset_root = PROJECT_DIR / "report" / "assets"
        for subdir, filenames in (
            ("ui", REQUIRED_UI_SCREENSHOTS + ["capture_metadata.json"]),
            ("results", REQUIRED_RESULT_IMAGES),
        ):
            src_dir = asset_root / subdir
            if not src_dir.exists():
                continue
            dest_dir = ensure_dir(run_report_dir / "assets" / subdir)
            for name in filenames:
                src = src_dir / name
                if src.exists():
                    copy_file(src, dest_dir / name)

    def _build_bibtex(self, state: WorkflowState) -> str:
        entries = []
        for source in state.sources:
            key = source.id.replace("-", "_")
            entries.append(
                f"""@misc{{{key},
  title = {{{source.title}}},
  author = {{{source.authors}}},
  year = {{{source.year or "n.d."}}},
  url = {{{source.url}}},
  note = {{{source.summary}}}
}}"""
            )
        return "\n\n".join(entries) + "\n"
