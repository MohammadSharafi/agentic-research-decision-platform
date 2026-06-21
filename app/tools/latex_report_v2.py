from __future__ import annotations

import re
import shutil
from pathlib import Path

from app.models.schemas import AnalysisTable, Source, WorkflowState
from app.tools.file_tools import ensure_dir, write_text
from app.tools.latex_report_tools import compile_latex_pdf
from app.ui.ui_helpers import ui_screenshot_caption

EVALUATION_THRESHOLD = 78

CORE_FIGURES = [
    ("overall_system_architecture.png", "System architecture connecting UI, API, graph orchestration, specialized agents, tools, memory, and exported artifacts.", "overall-architecture"),
    ("multi_agent_workflow_diagram.png", "Conditional multi-agent workflow showing planning, retrieval, analysis, critique, fact-checking, report generation, evaluation, presentation, and memory.", "workflow"),
    ("agent_communication_diagram.png", "Agent communication through explicit shared WorkflowState fields rather than hidden ad-hoc messages.", "communication"),
    ("langgraph_state_transition_diagram.png", "State transition diagram showing how workflow status values move through the graph.", "state-transition"),
    ("report_generation_pipeline_diagram.png", "Report generation pipeline from evidence and tables to Markdown, LaTeX/PDF, presentation, and evaluation outputs.", "report-pipeline"),
    ("evaluation_pipeline_diagram.png", "Evaluation pipeline with rubric scoring, thresholding, and optional revision routing.", "evaluation-pipeline"),
    ("evidence_by_theme.png", "Evidence distribution by theme for the deterministic demonstration corpus.", "evidence-theme"),
    ("quality_radar.png", "Radar chart of selected quality dimensions for the generated artifact.", "quality-radar"),
    ("conceptual_grounding_pipeline.png", "Conceptual grounding pipeline from user question to evidence-backed synthesis.", "conceptual-grounding"),
]

UI_SCREENSHOTS = [
    ("ui/ui_home.png", "ui_home.png", "ui-home"),
    ("ui/ui_workflow.png", "ui_workflow.png", "ui-workflow"),
    ("ui/ui_agent_outputs.png", "ui_agent_outputs.png", "ui-agent-outputs"),
    ("ui/ui_results.png", "ui_results.png", "ui-results"),
    ("ui/ui_figures.png", "ui_figures.png", "ui-figures"),
    ("ui/ui_downloads.png", "ui_downloads.png", "ui-downloads"),
]

RESULT_SCREENSHOTS = [
    ("results/demo_evaluation_score.png", "Demo evaluation score panel generated from the reproducible workflow run.", "demo-eval"),
    ("results/demo_agent_workflow_result.png", "Demo workflow result panel summarizing run ID, status, sources, figures, and agent sequence.", "demo-workflow-result"),
    ("results/demo_generated_figures.png", "Demo gallery of generated figures used by the final report.", "demo-generated-figures"),
    ("results/demo_report_output.png", "Demo report preview showing generated academic sections and run metadata.", "demo-report-preview"),
]


def latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def citation_key(source_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", source_id).strip("_") or "source"


def write_bibtex(path: Path, sources: list[Source]) -> None:
    entries: list[str] = []
    for source in sources:
        entry_type = "misc" if source.source_type in {"documentation", "policy", "technical_blog"} else "article"
        entries.append(
            rf"""@{entry_type}{{{citation_key(source.id)},
  title = {{{source.title}}},
  author = {{{source.authors}}},
  year = {{{source.year or "n.d."}}},
  url = {{{source.url}}},
  note = {{{source.summary}}}
}}"""
        )
    write_text(path, "\n\n".join(entries) + "\n")


def _column_spec(column_count: int) -> str:
    if column_count <= 2:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.46\textwidth}>{\RaggedRight\arraybackslash}p{0.46\textwidth}@{}"
    return "@{}" + "".join(r">{\RaggedRight\arraybackslash}X" for _ in range(column_count)) + "@{}"


def table_tex(table: AnalysisTable, label: str) -> str:
    columns = [latex_escape(col) for col in table.columns]
    rows = [[latex_escape(cell) for cell in row] for row in table.rows]
    header = " & ".join(rf"\textbf{{{col}}}" for col in columns) + r" \\"
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    spec = _column_spec(len(columns))
    return rf"""
\begin{{table}}[!htbp]
\centering
\caption{{{latex_escape(table.title)}}}
\label{{tab:{label}}}
\footnotesize
\setlength{{\tabcolsep}}{{3pt}}
\renewcommand{{\arraystretch}}{{1.25}}
\begin{{adjustbox}}{{max width=\textwidth}}
\begin{{tabularx}}{{\textwidth}}{{{spec}}}
\toprule
{header}
\midrule
{body}
\bottomrule
\end{{tabularx}}
\end{{adjustbox}}
\end{{table}}
\FloatBarrier
"""


def figure_tex(report_dir: Path, asset_path: str, caption: str, label: str, width: str = r"0.96\linewidth") -> str:
    if not (report_dir / "assets" / asset_path).exists():
        return ""
    return rf"""
\begin{{figure}}[!htbp]
\centering
\includegraphics[width={width},height=0.70\textheight,keepaspectratio]{{assets/{asset_path}}}
\caption{{{latex_escape(caption)}}}
\label{{fig:{label}}}
\end{{figure}}
\FloatBarrier
"""


def compact_itemize(items: list[str]) -> str:
    if not items:
        return r"\item No items were recorded for this run."
    return "\n".join(rf"\item {latex_escape(item)}" for item in items)


def source_table(state: WorkflowState) -> str:
    rows = [
        [src.source_type, src.year or "n.d.", src.credibility, ", ".join(src.tags[:4]), src.title]
        for src in state.sources[:12]
    ]
    return table_tex(
        AnalysisTable(
            title="Representative Retrieved Evidence Sources",
            columns=["Type", "Year", "Credibility", "Tags", "Title"],
            rows=rows,
        ),
        "evidence-sources",
    )


def evaluation_table(state: WorkflowState) -> str:
    return table_tex(
        AnalysisTable(
            title="Final Evaluation Scores",
            columns=["Dimension", "Score", "Interpretation"],
            rows=[
                ["Factuality", state.evaluation.factuality, "Groundedness and unsupported-claim control"],
                ["Relevance", state.evaluation.relevance, "Alignment with the selected topic"],
                ["Completeness", state.evaluation.completeness, "Coverage of required deliverables"],
                ["Structure", state.evaluation.structure, "Organization and readability"],
                ["Citation quality", state.evaluation.citation_quality, "Evidence traceability"],
                ["Clarity", state.evaluation.clarity, "Presentation quality"],
                ["Visual quality", state.evaluation.visual_quality, "Figure and UI artifact quality"],
                ["Reproducibility", state.evaluation.reproducibility, "Repeatable mock-mode execution"],
                ["Total", state.evaluation.total, "Overall artifact score"],
            ],
        ),
        "evaluation-scores",
    )


def routing_table() -> str:
    return table_tex(
        AnalysisTable(
            title="Conditional Routing Rules",
            columns=["Decision point", "Condition", "Next node"],
            rows=[
                ["Critic", "Evidence is insufficient and revision budget remains", "Research Agent"],
                ["Critic", "Evidence is acceptable", "Fact-Checker Agent"],
                ["Evaluator", rf"Quality score $Q < \tau$ where $\tau={EVALUATION_THRESHOLD}$", "Report Writer Agent"],
                ["Evaluator", rf"Quality score $Q \geq \tau$", "Presentation Agent"],
                ["Presentation", "Slide artifact generated", "Memory Agent"],
            ],
        ),
        "routing-rules",
    )


def all_state_tables(state: WorkflowState) -> str:
    parts: list[str] = []
    for idx, table in enumerate(state.tables, start=1):
        parts.append(table_tex(table, f"state-table-{idx}"))
    return "\n".join(parts)


def core_figures(report_dir: Path) -> str:
    return "\n".join(figure_tex(report_dir, name, caption, label) for name, caption, label in CORE_FIGURES)


def ui_screenshots(report_dir: Path) -> str:
    parts: list[str] = []
    for asset_path, filename, label in UI_SCREENSHOTS:
        parts.append(figure_tex(report_dir, asset_path, ui_screenshot_caption(filename), label, r"0.98\linewidth"))
    for asset_path, caption, label in RESULT_SCREENSHOTS:
        parts.append(figure_tex(report_dir, asset_path, caption, label, r"0.95\linewidth"))
    return "\n".join(part for part in parts if part)


def claim_checks(state: WorkflowState) -> str:
    if not state.claim_checks:
        return r"\item No claim checks were recorded."
    lines: list[str] = []
    for check in state.claim_checks:
        status = "Supported" if check.supported else "Unsupported"
        citations = ", ".join(check.citations) if check.citations else "no retrieved-source citation"
        lines.append(rf"\item \textbf{{{status}}}: {latex_escape(check.claim)} ({latex_escape(citations)}). {latex_escape(check.note)}")
    return "\n".join(lines)


def build_latex_document(state: WorkflowState, report_dir: Path) -> str:
    confidence = state.analysis.get("confidence_score", 0)
    source_count = state.analysis.get("source_count", len(state.sources))
    tag_counts = state.analysis.get("tag_counts", {})
    top_tags = ", ".join(f"{latex_escape(k)} ({v})" for k, v in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:8]) or "not available"

    return rf"""\documentclass[11pt]{{article}}
\usepackage[a4paper,margin=0.82in]{{geometry}}
\usepackage{{microtype}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{tabularx}}
\usepackage{{array}}
\usepackage{{ragged2e}}
\usepackage{{adjustbox}}
\usepackage{{float}}
\usepackage{{placeins}}
\usepackage{{caption}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\usepackage{{fancyhdr}}
\usepackage{{enumitem}}
\usepackage{{listings}}
\usepackage{{url}}
\hypersetup{{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}}
\graphicspath{{{{assets/}}}}
\definecolor{{codegray}}{{RGB}}{{245,247,250}}
\definecolor{{deepteal}}{{RGB}}{{15,118,110}}
\lstset{{
  backgroundcolor=\color{{codegray}},
  basicstyle=\ttfamily\footnotesize,
  breaklines=true,
  frame=single,
  columns=fullflexible,
  keepspaces=true
}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small Agentic Research \& Decision Intelligence Platform}}
\fancyhead[R]{{\small Final Project Report}}
\fancyfoot[C]{{\thepage}}
\setlist[itemize]{{leftmargin=1.2em,itemsep=0.25em}}
\setlength{{\parskip}}{{0.45em}}
\setlength{{\parindent}}{{0pt}}

\title{{\textbf{{Agentic Research \& Decision Intelligence Platform}}\\\large Robust Multi-Agent Research Workflow with Evidence, Algorithms, Formulas, UI Artifacts, and Reproducible Evaluation}}
\author{{Final Course Project}}
\date{{\today}}

\begin{{document}}
\maketitle

\begin{{abstract}}
This report presents a complete multi-agent research and decision-intelligence platform. The system converts one high-level topic into a reproducible research workflow: planning, evidence retrieval, structured analysis, critique, fact-checking, visualization, report generation, evaluation, presentation export, and persistent memory. The report intentionally includes the mathematical scoring formulation, conditional-routing algorithm, implementation tables, generated architecture figures, UI screenshots, and export artifacts. The default demonstration uses deterministic mock mode so that the project can be graded without paid API keys while remaining extensible to live retrieval and model providers.
\end{{abstract}}

\tableofcontents
\listoffigures
\listoftables
\newpage

\section{{Executive Summary}}
The submitted system is not a single chatbot. It is an inspectable multi-agent pipeline. The run analyzed here used topic \textit{{{latex_escape(state.query)}}}, retrieved {source_count} evidence items, generated {len(state.figures)} figures, and achieved an evaluation score of {state.evaluation.total}/100 with confidence {confidence}/100. The most important engineering contribution is the separation of responsibilities across specialized agents and a typed state object that makes each intermediate decision visible.

\section{{Problem Definition}}
Research workflows often fail when generation, evidence retrieval, critique, and evaluation are hidden inside one prompt. This project addresses that limitation by decomposing work into explicit stages. The system must produce a professional artifact containing: (i) an execution plan, (ii) evidence tables, (iii) decision logic, (iv) mathematical evaluation, (v) visual diagrams, (vi) UI screenshots, and (vii) downloadable reports and slides.

\section{{System Architecture}}
The platform has five layers: Streamlit and FastAPI interfaces, graph orchestration, agent layer, deterministic tool layer, and persistence/export layer. Figures in this section are constrained with \texttt{{keepaspectratio}} and a maximum height so they no longer overflow pages.

{core_figures(report_dir)}

\section{{Agent Design}}
Each agent owns one responsibility. Planner decomposes the topic, Research retrieves evidence, Analyst generates metrics and tables, Critic checks weakness, Fact-Checker grounds claims, Visualization creates figures, Report Writer compiles artifacts, Evaluator scores quality, Presentation creates slides, and Memory persists the run. This separation makes the workflow explainable during a live presentation.

{all_state_tables(state)}

\section{{Mathematical Formulation}}
The Planner converts the user query into an ordered task set:
\begin{{equation}}
T = \{{t_1,t_2,\ldots,t_n\}}
\end{{equation}}
where each $t_i$ is assigned to an agent and may depend on previous outputs.

The confidence score is modeled as a weighted evidence aggregate:
\begin{{equation}}
C = \frac{{\sum_{{i=1}}^n w_i s_i}}{{\sum_{{i=1}}^n w_i}},
\end{{equation}}
where $s_i$ is a source-quality signal and $w_i$ is its weight. In this run, $C={confidence}/100$.

The evaluator combines several quality dimensions:
\begin{{equation}}
Q = \alpha F + \beta R + \gamma K + \delta S + \epsilon V + \zeta P,
\end{{equation}}
where $F$ is factuality, $R$ relevance, $K$ citation quality, $S$ structure, $V$ visual quality, and $P$ reproducibility.

The revision gate is:
\begin{{equation}}
r = \begin{{cases}}
1, & Q < \tau \\
0, & Q \geq \tau
\end{{cases}}
\quad \text{{with}} \quad \tau={EVALUATION_THRESHOLD}.
\end{{equation}}
If $r=1$ and revision budget remains, the graph routes back to the Report Writer or Research Agent.

\section{{Algorithmic Workflow}}
\begin{{lstlisting}}[caption={{Algorithm 1: Conditional multi-agent execution}},label={{lst:agentic-algorithm}}]
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
\end{{lstlisting}}

\section{{Evidence and Citation Strategy}}
The retrieval component ranks sources by query overlap, credibility, and tags. The fact checker only cites already-retrieved sources and does not invent references. The strongest evidence themes in this run were: {top_tags}.

{source_table(state)}

\section{{Evaluation Methodology}}
The evaluator scores the output using factuality, relevance, completeness, structure, citation quality, clarity, visual quality, and reproducibility. These dimensions are important because a research assistant should be graded not only on final prose but also on traceability and reproducibility.

{evaluation_table(state)}

\section{{Conditional Routing Rules}}
{routing_table()}

\section{{User Interface and Panel Screenshots}}
The screenshots below document the current Streamlit panel and demonstrate that the professor can inspect the workflow from left to right: overview, workflow, agents, results, figures, downloads, and about. These screenshots should be regenerated after UI edits by running \texttt{{python scripts/capture\_ui\_screenshots.py}}.

{ui_screenshots(report_dir)}

\section{{Claim Checks}}
\begin{{itemize}}
{claim_checks(state)}
\end{{itemize}}

\section{{Critic Notes}}
\begin{{itemize}}
{compact_itemize(state.critique)}
\end{{itemize}}

\section{{Implementation and Reproducibility}}
Run the system locally with:
\begin{{lstlisting}}[caption={{Local demo commands}}]
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_MOCK_LLM=true
python scripts/capture_ui_screenshots.py
python scripts/build_report_pdf.py
streamlit run app/ui/streamlit_app.py
\end{{lstlisting}}
The report generator uses \texttt{{tabularx}}, \texttt{{adjustbox}}, smaller table padding, increased row spacing, and constrained image height to prevent overlapping table text and poorly scaled figures.

\section{{Limitations}}
The project is a research prototype. It demonstrates architecture, reproducibility, and evidence-grounded workflow behavior, but it is not a validated production decision system. Live external retrieval, stronger entailment models, human approval gates, and formal domain evaluation are future work.

\section{{Conclusion}}
The platform demonstrates a complete, reproducible, and inspectable agentic research workflow. The improved report generator now produces a more readable academic report with robust tables, constrained figures, formulas, algorithmic pseudocode, UI screenshots, and a clearer explanation of how the multi-agent system works.

\bibliographystyle{{plain}}
\bibliography{{references}}
\end{{document}}
"""


def generate_latex_report(state: WorkflowState, report_dir: Path, output_report_pdf: Path | None = None) -> tuple[Path, Path, bool, str]:
    ensure_dir(report_dir)
    tex_path = report_dir / "final_report.tex"
    pdf_path = report_dir / "final_report.pdf"
    bib_path = report_dir / "references.bib"
    write_bibtex(bib_path, state.sources)
    write_text(tex_path, build_latex_document(state, report_dir))
    ok, message = compile_latex_pdf(report_dir, tex_path.name)
    if output_report_pdf is not None and pdf_path.exists():
        ensure_dir(output_report_pdf.parent)
        shutil.copy2(pdf_path, output_report_pdf)
    return tex_path, pdf_path, ok and pdf_path.exists(), message
