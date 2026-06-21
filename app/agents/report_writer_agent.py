from __future__ import annotations

from pathlib import Path

from app.config.settings import PROJECT_DIR, get_settings
from app.models.schemas import WorkflowState
from app.tools.citation_tools import numbered_references
from app.tools.file_tools import copy_file, ensure_dir, write_text
from app.tools.latex_report_v2 import generate_latex_report
from app.tools.report_tools import markdown_table, markdown_to_simple_pdf
from app.ui.ui_helpers import REQUIRED_RESULT_IMAGES, REQUIRED_UI_SCREENSHOTS


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
        state.add_note(
            self.name,
            f"Wrote expanded Markdown report to {report_path} and robust LaTeX/PDF report to {run_pdf}.",
            latex_pdf=latex_ok,
            latex_message=latex_message,
        )
        return state

    def _build_report(self, state: WorkflowState) -> str:
        if not state.use_mock_llm:
            return self._build_research_report(state)

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
            claim_lines.append(f"- **{status}:** {check.claim} — {citations}. {check.note}")

        critique = "\n".join(f"- {item}" for item in state.critique) or "- No critique notes were recorded."
        references = numbered_references(state.sources)
        confidence = state.analysis.get("confidence_score", 0)
        source_count = state.analysis.get("source_count", len(state.sources))
        eval_score = state.evaluation.total
        tag_counts = state.analysis.get("tag_counts", {})
        top_tags = ", ".join(f"{k} ({v})" for k, v in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:8]) or "not available"

        all_tables = "\n\n".join(table_blocks)
        figure_text = "\n\n".join(figure_lines)
        claim_check_text = "\n".join(claim_lines) or "- No claim checks were recorded."

        return rf"""# Agentic Research & Decision Intelligence Platform

**Final Course Project Report**  
**Topic:** {state.query}  
**Mode:** {"Deterministic mock/offline mode" if state.use_mock_llm else "External model/search capable mode"}  
**Run ID:** `{state.run_id}`  
**Final quality score:** {eval_score}/100  
**Confidence score:** {confidence}/100

## Abstract

This report documents a complete multi-agent research and decision-intelligence platform. The system converts a broad topic into a reproducible workflow: planning, evidence retrieval, analysis, critique, fact-checking, visualization, report generation, evaluation, presentation export, and persistent memory. The revised report emphasizes mathematical formulation, conditional algorithms, readable tables, correctly scaled figures, panel screenshots, and reproducible demo commands.

## 1. Problem Definition

Single-prompt systems hide too many decisions. A serious research assistant should expose the task plan, retrieved evidence, intermediate tables, critique, claim checks, visual artifacts, evaluation scores, and final downloads. This project implements that inspectable workflow using specialized agents and shared workflow state.

## 2. System Overview

The platform has five layers: Streamlit UI, FastAPI backend, graph orchestration, agent/tool layer, and SQLite plus filesystem persistence. The default mock mode keeps the project deterministic for grading while preserving extension points for external search and model providers.

## 3. Agentic Architecture

Ten agents collaborate through typed `WorkflowState`: Planner, Research, Analyst, Critic, Fact-Checker, Visualization, Report Writer, Evaluator, Presentation, and Memory. Each agent owns one responsibility, which makes the system easier to test, explain, and present.

## 4. Mathematical Formulation

Task decomposition:

```latex
T = \{{t_1,t_2,\ldots,t_n\}}
```

Weighted confidence:

```latex
C = \frac{{\sum_{{i=1}}^{{n}} w_i s_i}}{{\sum_{{i=1}}^{{n}} w_i}}
```

Quality score:

```latex
Q = \alpha F + \beta R + \gamma K + \delta S + \epsilon V + \zeta P
```

Revision gate:

```latex
r = \begin{{cases}} 1, & Q < \tau \\ 0, & Q \geq \tau \end{{cases}}, \quad \tau = 78
```

## 5. Algorithmic Workflow

```text
Input: query q, maximum revisions m
state <- initialize WorkflowState(q)
state.plan <- Planner(q)
state.sources <- Research(state.plan)
state.analysis <- Analyst(state.sources)
state.critique <- Critic(state.analysis)
if state.needs_revision and state.revision_count < m:
    state.revision_count += 1
    state.sources <- Research(state.critique)
state.claim_checks <- FactChecker(state.sources, state.analysis)
state.figures <- Visualization(state)
state.report <- ReportWriter(state)
state.evaluation <- Evaluator(state.report)
if state.evaluation.total < threshold and state.revision_count < m:
    state.report <- ReportWriter(state)
state.presentation <- Presentation(state.report)
Memory.save(state)
return state
```

## 6. Evidence and Retrieval

The run retrieved **{source_count}** evidence sources. Top evidence themes: **{top_tags}**. The fact checker only grounds claims in retrieved sources and does not invent citations.

## 7. Tables

The LaTeX report now uses `tabularx`, `adjustbox`, smaller padding, and increased row spacing so text in tables does not overlap.

{all_tables}

## 8. Figures and Images

The LaTeX report now constrains every figure using `keepaspectratio` and a maximum height so diagrams and screenshots do not overflow or distort.

{figure_text}

## 9. UI Panel Screenshots

The report expects current screenshots under `report/assets/ui/`. Regenerate them after UI edits:

```bash
python scripts/capture_ui_screenshots.py
python scripts/build_report_pdf.py
```

Included panel assets:

- `assets/ui/ui_home.png`
- `assets/ui/ui_workflow.png`
- `assets/ui/ui_agent_outputs.png`
- `assets/ui/ui_results.png`
- `assets/ui/ui_figures.png`
- `assets/ui/ui_downloads.png`

## 10. Evaluation

Final quality score: **{eval_score}/100**. Confidence score: **{confidence}/100**. The evaluation measures artifact quality, not production validity.

## 11. Claim Checks

{claim_check_text}

## 12. Critic Notes

{critique}

## 13. Reproducibility

```bash
source .venv/bin/activate
export USE_MOCK_LLM=true
python scripts/capture_ui_screenshots.py
python scripts/build_report_pdf.py
streamlit run app/ui/streamlit_app.py
```

## 14. Limitations

This is a research prototype. It demonstrates architecture, reproducibility, and evidence-grounded workflow behavior. Live retrieval, stronger entailment checking, human approval gates, and formal domain evaluation are future work.

## 15. Conclusion

The project demonstrates a reproducible and inspectable agentic research workflow. The updated report generator now produces a fuller academic report with robust tables, constrained figures, mathematical formulation, algorithmic pseudocode, UI screenshots, and clearer explanations.

## References

{references}
"""

    def _build_research_report(self, state: WorkflowState) -> str:
        confidence = state.analysis.get("confidence_score", 0)
        eval_score = state.evaluation.total
        executive_summary = state.analysis.get("executive_summary", "")
        key_findings = state.analysis.get("key_findings", [])

        table_blocks = []
        for idx, table in enumerate(state.tables, start=1):
            if table.title.lower() == "final evaluation scores":
                continue
            table_blocks.append(f"**Table {idx}. {table.title}**\n\n{markdown_table(table.columns, table.rows)}")

        figure_blocks = []
        for idx, figure in enumerate(state.figures, start=1):
            rel = Path(figure.path).name
            if figure.figure_type == "mermaid":
                figure_blocks.append(f"**Figure {idx}. {figure.title}.** See `report/assets/{rel}`.")
            else:
                figure_blocks.append(f"**Figure {idx}. {figure.title}.**\n\n![{figure.title}](assets/{rel})")

        claim_lines = []
        for check in state.claim_checks:
            citations = "; ".join(check.citations) if check.citations else "not supported by retrieved sources"
            status = "Supported" if check.supported else "Needs caution"
            claim_lines.append(f"- **{status}:** {check.claim} — {citations}. {check.note}")

        critique = "\n".join(f"- {item}" for item in state.critique) or "- No critique notes were recorded."
        findings = "\n".join(f"- {item}" for item in key_findings) or "- No key findings were recorded."
        references = numbered_references(state.sources)

        return rf"""# Research Report: {state.query}

**Mode:** External model/search capable mode  
**Run ID:** `{state.run_id}`  
**Sources retrieved:** {len(state.sources)}  
**Confidence score:** {confidence}/100  
**Evaluation score:** {eval_score}/100

## Abstract

{executive_summary}

## 1. Research Question

This report answers the user request:

> {state.query}

The system treated the prompt as a topic-specific research task. It planned the work, retrieved sources, built analysis tables, checked claims, generated figures, wrote this report, and scored the output.

## 2. Methodology

The workflow used a multi-agent pipeline:

1. Planner created a task plan for the prompt.
2. Research retrieved external sources when API keys were configured.
3. Analyst synthesized evidence into findings and tables.
4. Critic identified gaps and cautions.
5. Fact-Checker mapped claims to retrieved-source citations.
6. Visualization generated evidence and support charts.
7. Report Writer produced Markdown and LaTeX/PDF artifacts.
8. Evaluator scored artifact quality.

The retrieval and synthesis process is summarized by:

```latex
S(x,q)=\lambda_1 overlap(x,q)+\lambda_2 credibility(x)+\lambda_3 tag\_match(x,q)
C = 100 \cdot \frac{{\sum_i w_i s_i}}{{\sum_i w_i}}
Q = \frac{{F+R+M+S+K+L+V+P}}{{8}}
```

## 3. Key Findings

{findings}

## 4. Analysis Tables

{chr(10).join(table_blocks)}

## 5. Figures

{chr(10).join(figure_blocks) if figure_blocks else "No figures were generated for this run."}

## 6. Claim Checks

{chr(10).join(claim_lines) if claim_lines else "- No claim checks were recorded."}

## 7. Critic Notes and Limitations

{critique}

This report is a machine-generated research synthesis. It should be treated as a first draft that requires human review, especially for policy, financial, health, or legal decisions.

## 8. Evaluation

Final artifact score: **{eval_score}/100**. The score reflects source coverage, claim support, structure, visual artifacts, and reproducibility. It is not a guarantee that every fact is complete or current.

## 9. Conclusion

The run produced a topic-specific research artifact for the prompt rather than a fixed project report. The strongest conclusions are the claims that were supported by retrieved sources; unsupported or weakly supported claims are explicitly marked for caution.

## References

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
