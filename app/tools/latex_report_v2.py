from __future__ import annotations

import re
import shutil
from pathlib import Path

from app.models.schemas import AnalysisTable, Source, WorkflowState
from app.tools.file_tools import ensure_dir, write_text
from app.tools.latex_report_tools import compile_latex_pdf
from app.ui.ui_helpers import read_capture_metadata, ui_screenshot_caption

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


def _escape_latex_text(text: str) -> str:
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


def latex_escape(value: object) -> str:
    text = str(value)
    parts = re.split(r"(\$[^$]+\$)", text)
    escaped: list[str] = []
    for part in parts:
        if len(part) >= 2 and part.startswith("$") and part.endswith("$"):
            escaped.append(part)
        else:
            escaped.append(_escape_latex_text(part))
    return "".join(escaped)


def citation_key(source_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", source_id).strip("_") or "source"


def write_bibtex(path: Path, sources: list[Source]) -> None:
    if path.exists() and path.read_text(encoding="utf-8").count("@") >= len(sources):
        return
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


def _column_spec(columns: list[str]) -> str:
    column_count = len(columns)
    normalized = [col.lower() for col in columns]
    if normalized == ["endpoint", "method", "purpose"]:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.31\textwidth}>{\RaggedRight\arraybackslash}p{0.10\textwidth}Y@{}"
    if normalized == ["criterion", "description", "weight"]:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.18\textwidth}Y>{\RaggedRight\arraybackslash}p{0.10\textwidth}@{}"
    if normalized == ["decision point", "condition", "next node"]:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.18\textwidth}Y>{\RaggedRight\arraybackslash}p{0.24\textwidth}@{}"
    if normalized == ["dimension", "score", "interpretation"]:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.20\textwidth}>{\RaggedRight\arraybackslash}p{0.11\textwidth}Y@{}"
    if normalized == ["limitation", "impact", "mitigation"]:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.22\textwidth}>{\RaggedRight\arraybackslash}p{0.25\textwidth}Y@{}"
    if column_count <= 2:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.43\textwidth}>{\RaggedRight\arraybackslash}p{0.51\textwidth}@{}"
    if column_count == 3:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.22\textwidth}>{\RaggedRight\arraybackslash}p{0.18\textwidth}Y@{}"
    if column_count == 4:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.16\textwidth}YYY@{}"
    if column_count == 5:
        return r"@{}>{\RaggedRight\arraybackslash}p{0.13\textwidth}>{\RaggedRight\arraybackslash}p{0.08\textwidth}>{\RaggedRight\arraybackslash}p{0.11\textwidth}>{\RaggedRight\arraybackslash}p{0.20\textwidth}Y@{}"
    return "@{}" + "".join("Y" for _ in range(column_count)) + "@{}"


def table_tex(table: AnalysisTable, label: str) -> str:
    columns = [latex_escape(col) for col in table.columns]
    rows = [[latex_escape(cell) for cell in row] for row in table.rows]
    header = " & ".join(rf"\textbf{{{col}}}" for col in columns) + r" \\"
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    spec = _column_spec([str(col) for col in table.columns])
    font_size = r"\scriptsize" if len(columns) >= 4 or len(rows) > 8 else r"\footnotesize"
    return rf"""
\begin{{table}}[!htbp]
\centering
\caption{{{latex_escape(table.title)}}}
\label{{tab:{label}}}
\begingroup
{font_size}
\setlength{{\tabcolsep}}{{2.8pt}}
\renewcommand{{\arraystretch}}{{1.35}}
\begin{{adjustbox}}{{max width=\textwidth}}
\begin{{tabularx}}{{\textwidth}}{{{spec}}}
\toprule
{header}
\midrule
{body}
\bottomrule
\end{{tabularx}}
\end{{adjustbox}}
\endgroup
\end{{table}}
\FloatBarrier
"""


def figure_tex(report_dir: Path, asset_path: str, caption: str, label: str, width: str = r"0.96\linewidth") -> str:
    if not (report_dir / "assets" / asset_path).exists():
        return ""
    return rf"""
\begin{{figure}}[!htbp]
\centering
\includegraphics[width={width},height=0.78\textheight,keepaspectratio]{{assets/{asset_path}}}
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
    type_labels = {
        "documentation": "docs",
        "technical_blog": "blog",
    }
    rows = [
        [
            type_labels.get(src.source_type, src.source_type),
            src.year or "n.d.",
            src.credibility,
            ", ".join(src.tags[:4]),
            src.title,
        ]
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
        if table.title.lower() == "final evaluation scores":
            continue
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
    capture_meta = read_capture_metadata()
    capture_kind = capture_meta.get("capture_type", "unknown")
    capture_details = latex_escape(capture_meta.get("details", "No capture metadata found."))
    mode_label = "Deterministic mock/offline mode" if state.use_mock_llm else "External model/search capable mode"

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
\newcolumntype{{Y}}{{>{{\RaggedRight\arraybackslash}}X}}
\captionsetup{{font=small,labelfont=bf}}
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
\setlength{{\headheight}}{{14pt}}
\setlist[itemize]{{leftmargin=1.2em,itemsep=0.25em}}
\setlength{{\parskip}}{{0.45em}}
\setlength{{\parindent}}{{0pt}}
\emergencystretch=2em

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
This final report documents an inspectable agentic research platform, not a single chatbot response. The analyzed run used the topic \textit{{{latex_escape(state.query)}}}, operated in {latex_escape(mode_label)}, retrieved {source_count} evidence items, generated {len(state.figures)} visual artifacts, and achieved an evaluation score of {state.evaluation.total}/100 with confidence {confidence}/100. The main engineering contribution is a transparent workflow in which planning, retrieval, analysis, critique, fact checking, visualization, reporting, evaluation, presentation, and memory are separate stages with explicit state.

\section{{Research Question and Scope}}
The project asks whether a graph-based multi-agent system can produce a more trustworthy research artifact than a one-shot prompt. The scope is a university-grade prototype for evidence-grounded research and decision support, demonstrated on trustworthy clinical decision support. It is not a medical device and it does not provide patient-specific recommendations. The deliverable scope includes runnable code, a Streamlit panel, FastAPI endpoints, SQLite memory, generated figures, Markdown/LaTeX/PDF reports, evaluation output, and presentation material.

\section{{Background and Related Work}}
Retrieval-augmented generation connects model output to external evidence \cite{{lewis_2020_rag}}. ReAct-style agents combine reasoning and tool use \cite{{yao_2022_react}}, while Reflexion and Self-Refine demonstrate iterative critique and revision \cite{{shinn_2023_reflexion}}, \cite{{madaan_2023_self_refine}}. Evaluation methods for RAG emphasize faithfulness, relevance, and context use \cite{{es_2023_ragas}}. Clinical decision support research stresses workflow fit, safety, and governance \cite{{sutton_2020_cdss}}, while hallucination surveys show why fluent text alone is not enough \cite{{ji_2023_hallucination_survey}}.

\section{{System Requirements}}
The platform is designed around six requirements. First, the default path must be reproducible without paid API keys. Second, each agent decision must be inspectable through typed state. Third, retrieved evidence and claim checks must be visible. Fourth, tables and figures must compile cleanly into LaTeX without overlapping text or distorted images. Fifth, the UI must expose intermediate and final artifacts for live grading. Sixth, scripts and tests must regenerate the report and screenshots from source.

\section{{System Architecture}}
The platform has five layers: Streamlit and FastAPI interfaces, graph orchestration, specialized agents, deterministic tools, and persistence/export storage. The figures below are included with constrained width, constrained height, and \texttt{{keepaspectratio}} so page layout remains stable.

{core_figures(report_dir)}

\section{{Agent Responsibilities}}
Each agent owns one responsibility. Planner decomposes the task; Research retrieves sources; Analyst computes metrics and tables; Critic searches for weaknesses; Fact-Checker grounds claims; Visualization creates charts and diagrams; Report Writer produces Markdown, LaTeX, and PDF artifacts; Evaluator scores output quality; Presentation exports slides; Memory persists the run. The tables below are generated from workflow state and use adaptive column widths to avoid text overlap.

{all_state_tables(state)}

\section{{Workflow and State Model}}
The workflow is stateful rather than conversationally implicit. \texttt{{WorkflowState}} contains the query, plan, sources, notes, analysis values, tables, critique, revision flags, claim checks, figure paths, report paths, evaluation scores, status, and errors. Conditional routing occurs after the Critic and Evaluator, which makes the graph agentic: weak evidence can route back to Research, and a low report score can route back to Report Writer before finalization.

{routing_table()}

\section{{Mathematical Formulation}}
The Planner decomposes a user request $q$ into ordered tasks:
\begin{{equation}}
T(q)=\{{t_1,t_2,\ldots,t_n\}}, \qquad t_i=(d_i,a_i,D_i)
\end{{equation}}
where $d_i$ is the task description, $a_i$ is the assigned agent, and $D_i$ is the dependency set.

Mock retrieval ranks each source $x$ with a transparent heuristic:
\begin{{equation}}
S(x,q)=\lambda_1\,\operatorname{{overlap}}(x,q)+\lambda_2\,\operatorname{{credibility}}(x)+\lambda_3\,\operatorname{{tag\_match}}(x,q).
\end{{equation}}
This keeps grading deterministic while preserving a clear extension point for live search.

The confidence score is modeled as a weighted evidence aggregate:
\begin{{equation}}
C = 100 \cdot \frac{{\sum_{{i=1}}^n w_i s_i}}{{\sum_{{i=1}}^n w_i}},
\end{{equation}}
where $s_i$ is a source-quality or coverage signal and $w_i$ is its weight. In this run, $C={confidence}/100$.

The evaluator combines quality dimensions into an overall score:
\begin{{equation}}
Q=\frac{{F+R+M+S+K+L+V+P}}{{8}},
\end{{equation}}
where $F$ is factuality, $R$ relevance, $M$ completeness, $S$ structure, $K$ citation quality, $L$ clarity, $V$ visual quality, and $P$ reproducibility.

The revision gate is:
\begin{{equation}}
r=\begin{{cases}}
1, & Q < \tau \ \text{{and revision budget remains}},\\
0, & Q \geq \tau \ \text{{or budget is exhausted}},
\end{{cases}}
\qquad \tau={EVALUATION_THRESHOLD}.
\end{{equation}}
When $r=1$, the graph returns to a previous generation stage instead of silently accepting a weak artifact.

\section{{Algorithmic Workflow}}
\begin{{lstlisting}}[caption={{Algorithm 1: Conditional multi-agent execution}},label={{lst:agentic-algorithm}}]
Input: query q, threshold tau, maximum revisions m
state <- initialize WorkflowState(q)
state.plan <- Planner(q)
state.sources <- Research(state.plan)
state.analysis <- Analyst(state.sources)
state.critique <- Critic(state.analysis, state.sources)
while state.needs_revision and state.revision_count < m:
    state.revision_count <- state.revision_count + 1
    state.sources <- Research(state.critique)
    state.analysis <- Analyst(state.sources)
    state.critique <- Critic(state.analysis, state.sources)
state.claim_checks <- FactChecker(state.sources, state.analysis)
state.figures <- Visualization(state)
state.report <- ReportWriter(state)
state.evaluation <- Evaluator(state.report, state.figures)
while state.evaluation.total < tau and state.revision_count < m:
    state.revision_count <- state.revision_count + 1
    state.report <- ReportWriter(state)
    state.evaluation <- Evaluator(state.report, state.figures)
state.report <- ReportWriter(state)  # final pass with final score
state.presentation <- Presentation(state.report)
Memory.save(state)
return state
\end{{lstlisting}}

\begin{{lstlisting}}[caption={{Algorithm 2: Claim grounding and citation gating}},label={{lst:claim-gating}}]
Input: candidate claims, retrieved sources
for each claim in candidate claims:
    matching_sources <- sources with related tags, title terms, or summaries
    if matching_sources is empty:
        mark claim unsupported
        attach no generated citation
    else:
        mark claim supported
        attach only retrieved-source citation markers
return claim check list
\end{{lstlisting}}

\section{{Evidence and Citation Strategy}}
The retrieval component ranks sources by query overlap, credibility, and tags. The fact checker only cites already-retrieved sources and does not invent references. The strongest evidence themes in this run were: {top_tags}. Table~\ref{{tab:evidence-sources}} samples the evidence base used by the generated report.

{source_table(state)}

\section{{Implementation Details}}
The repository separates concerns into \texttt{{app/agents}}, \texttt{{app/graph}}, \texttt{{app/tools}}, \texttt{{app/models}}, \texttt{{app/storage}}, \texttt{{app/ui}}, and \texttt{{scripts}}. The graph runner uses LangGraph when available and a deterministic fallback runner otherwise. Tools handle retrieval, citation formatting, visualization, report generation, presentation export, and filesystem writes. This separation keeps the agents simple and makes the project easier to test.

\section{{API, Storage, and Artifacts}}
FastAPI provides health, run, report, presentation, and figure endpoints. SQLite stores run metadata and serialized state for later inspection. Generated artifacts are written to \texttt{{outputs/}} for run-specific files and \texttt{{report/}} for canonical submission files. The canonical report paths are \texttt{{report/final\_report.tex}}, \texttt{{report/final\_report.pdf}}, \texttt{{report/final\_report.md}}, and \texttt{{report/references.bib}}.

\section{{User Interface and Panel Screenshots}}
The Streamlit panel exposes the project without requiring graders to read code first. It includes topic input, mock/real mode selection, run execution, workflow inspection, agent outputs, evaluation metrics, figure previews, and download controls. Screenshot capture type: \texttt{{{latex_escape(capture_kind)}}}. Metadata: {capture_details}

{ui_screenshots(report_dir)}

\section{{Report Generation and LaTeX Formatting}}
The LaTeX generator now uses \texttt{{tabularx}}, an adaptive \texttt{{Y}} column type, \texttt{{adjustbox}}, smaller table padding, increased row spacing, and constrained figure dimensions. Inline math is preserved while regular text is escaped, so table cells can contain formulas such as $Q < \tau$ without being converted into broken text. Figures and screenshots use \texttt{{keepaspectratio}} with a maximum height, which prevents stretched diagrams and tiny unreadable page images.

\section{{Evaluation Methodology}}
The evaluator scores factuality, relevance, completeness, structure, citation quality, clarity, visual quality, and reproducibility. These dimensions are important because a research assistant should be graded on traceability and artifact quality, not just prose fluency. The final score in this run is {state.evaluation.total}/100.

{evaluation_table(state)}

\section{{Results}}
The mock run completed with {source_count} sources, {len(state.figures)} figure records, a canonical LaTeX source, a compiled PDF, demo screenshots, result images, evaluation JSON/Markdown, and presentation output. The report is intentionally artifact-heavy: tables document agent behavior and API design; formulas document scoring; algorithms document control flow; figures document architecture and UI behavior.

\section{{Claim Checks}}
\begin{{itemize}}
{claim_checks(state)}
\end{{itemize}}

\section{{Critic Notes}}
\begin{{itemize}}
{compact_itemize(state.critique)}
\end{{itemize}}

\section{{Error Analysis}}
Expected errors include stale sources, unsupported claims, shallow critique, malformed citations, and broken rendering. The system mitigates these through deterministic retrieval, explicit critic notes, citation gating, evaluation thresholds, generated screenshots, and a render-and-check PDF workflow. For production, passage-level entailment and source freshness checks should be added before any high-stakes deployment.

\section{{Ethical and Safety Considerations}}
The clinical scenario is used only as a demanding research context. The system must not be used for diagnosis or treatment. Real deployment would require privacy controls, audit logs, security review, institution-approved source corpora, clinician accountability, bias evaluation, and human approval gates. The report therefore frames clinical decision support as a governance and workflow problem, not merely a model-quality problem.

\section{{Testing and Reproducibility}}
The project can be regenerated with the commands below. Mock mode is the grading default because it produces repeatable evidence, figures, screenshots, evaluation files, and reports.
\begin{{lstlisting}}[caption={{Local verification commands}}]
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export USE_MOCK_LLM=true
python scripts/capture_ui_screenshots.py
python scripts/generate_latex_report.py
python scripts/build_report_pdf.py
pytest
\end{{lstlisting}}

\section{{Limitations}}
The current corpus is static, the fact checker is metadata-level rather than entailment-level, and the evaluator uses deterministic heuristics. The UI is intended for demonstration rather than production operations. These limitations are acceptable for a final project because they make grading reproducible, but they must be addressed before real deployment.

\section{{Future Work}}
Future work should add live retrieval adapters, vector search over approved corpora, stronger natural-language entailment, asynchronous job queues, authentication, richer audit trails, human review checkpoints, and benchmarking against clinical reporting standards. The architecture already isolates these improvements behind agent and tool contracts.

\section{{Conclusion}}
The platform demonstrates a complete, reproducible, and inspectable agentic research workflow. The updated LaTeX generator produces a fuller academic report with robust tables, preserved mathematical notation, explicit algorithms, constrained figures, refreshed UI screenshots, and clearer explanations of how the multi-agent system works.

\nocite{{*}}
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
