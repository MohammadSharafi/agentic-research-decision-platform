from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from app.models.schemas import AnalysisTable, Source, WorkflowState
from app.tools.file_tools import ensure_dir, write_text
from app.ui.ui_helpers import read_capture_metadata, ui_screenshot_caption

REQUIRED_ASSETS = [
    "overall_system_architecture.png",
    "agent_communication_diagram.png",
    "multi_agent_workflow_diagram.png",
    "langgraph_state_transition_diagram.png",
    "report_generation_pipeline_diagram.png",
    "evaluation_pipeline_diagram.png",
    "evidence_by_theme.png",
    "quality_radar.png",
    "conceptual_grounding_pipeline.png",
]

EVALUATION_THRESHOLD = 78


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
    return re.sub(r"[^A-Za-z0-9]+", "_", source_id).strip("_")


def table_tex(table: AnalysisTable, label: str, colspec: str | None = None) -> str:
    if colspec is None:
        n = len(table.columns)
        if n == 4:
            colspec = r"p{0.14\linewidth}p{0.28\linewidth}p{0.26\linewidth}p{0.26\linewidth}"
        elif n == 3:
            colspec = r"p{0.18\linewidth}p{0.12\linewidth}p{0.62\linewidth}"
        else:
            colspec = "l" * n
    header = " & ".join(latex_escape(col) for col in table.columns) + r" \\"
    rows = "\n".join(" & ".join(latex_escape(cell) for cell in row) + r" \\" for row in table.rows)
    return rf"""
\begin{{table}}[H]
\centering
\caption{{{latex_escape(table.title)}}}
\label{{tab:{label}}}
\small
\begin{{tabular}}{{{colspec}}}
\toprule
{header}
\midrule
{rows}
\bottomrule
\end{{tabular}}
\end{{table}}
"""


def figure_tex(filename: str, caption: str, label: str, width: str = r"0.92\linewidth") -> str:
    return rf"""
\begin{{figure}}[H]
\centering
\includegraphics[width={width}]{{assets/{filename}}}
\caption{{{latex_escape(caption)}}}
\label{{fig:{label}}}
\end{{figure}}
"""


def optional_figure_tex(
    report_dir: Path,
    filename: str,
    caption: str,
    label: str,
    width: str = r"0.95\linewidth",
) -> str:
    if (report_dir / "assets" / filename).exists():
        return figure_tex(filename, caption, label, width)
    return ""


def write_bibtex(path: Path, sources: list[Source]) -> None:
    """Append run-specific sources only when the canonical bibliography is missing."""
    if path.exists() and path.read_text(encoding="utf-8").count("@") >= 20:
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


def compile_latex_pdf(report_dir: Path, tex_name: str = "final_report.tex") -> tuple[bool, str]:
    tex_path = report_dir / tex_name
    pdf_path = report_dir / tex_name.replace(".tex", ".pdf")
    if not tex_path.exists():
        return False, f"Missing LaTeX source: {tex_path}"

    latexmk = shutil.which("latexmk")
    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    stem = tex_path.stem

    try:
        if latexmk:
            subprocess.run(
                [latexmk, "-C", tex_name],
                cwd=report_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=60,
            )
            result = subprocess.run(
                [latexmk, "-pdf", "-interaction=nonstopmode", "-f", tex_name],
                cwd=report_dir,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=180,
            )
            if pdf_path.exists() and pdf_path.stat().st_size > 10_000:
                return True, "LaTeX PDF compiled successfully via latexmk."
            output = result.stdout[-4000:]
        elif pdflatex:
            commands: list[list[str]] = [
                [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_name],
            ]
            if bibtex and (report_dir / "references.bib").exists():
                commands.extend(
                    [
                        [bibtex, stem],
                        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_name],
                        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_name],
                    ]
                )
            else:
                commands.append([pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_name])

            output = ""
            for command in commands:
                result = subprocess.run(
                    command,
                    cwd=report_dir,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=90,
                )
                output = result.stdout
                if result.returncode != 0:
                    return False, output[-4000:]
            if pdf_path.exists():
                return True, "LaTeX PDF compiled successfully via pdflatex."
            return False, output[-4000:]
        else:
            return False, "pdflatex was not found on PATH."
    except subprocess.TimeoutExpired:
        return False, "LaTeX compilation timed out."

    return pdf_path.exists(), output if pdf_path.exists() else output


def generate_latex_report(state: WorkflowState, report_dir: Path, output_report_pdf: Path | None = None) -> tuple[Path, Path, bool, str]:
    """Write final_report.tex and compile final_report.pdf when LaTeX is available."""
    ensure_dir(report_dir)
    tex_path = report_dir / "final_report.tex"
    pdf_path = report_dir / "final_report.pdf"
    bib_path = report_dir / "references.bib"
    write_bibtex(bib_path, state.sources)
    write_text(tex_path, build_latex_document(state))

    ok, message = compile_latex_pdf(report_dir, tex_path.name)
    if output_report_pdf is not None and pdf_path.exists():
        ensure_dir(output_report_pdf.parent)
        shutil.copy2(pdf_path, output_report_pdf)
    return tex_path, pdf_path, ok and pdf_path.exists(), message


def build_latex_document(state: WorkflowState) -> str:
    confidence = state.analysis.get("confidence_score", 0)
    source_count = state.analysis.get("source_count", len(state.sources))
    eval_score = state.evaluation.total
    tag_counts = state.analysis.get("tag_counts", {})
    sorted_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)[:8]
    top_tags = ", ".join(f"{latex_escape(k)} ({v})" for k, v in sorted_tags) or "none"

    tables = list(state.tables)
    if len(tables) >= 6:
        tables[5] = AnalysisTable(
            title="Final Evaluation Scores",
            columns=["Dimension", "Score"],
            rows=[
                ["Factuality", state.evaluation.factuality],
                ["Relevance", state.evaluation.relevance],
                ["Completeness", state.evaluation.completeness],
                ["Structure", state.evaluation.structure],
                ["Citation quality", state.evaluation.citation_quality],
                ["Clarity", state.evaluation.clarity],
                ["Visual quality", state.evaluation.visual_quality],
                ["Reproducibility", state.evaluation.reproducibility],
                ["Total", state.evaluation.total],
            ],
        )

    agent_table = table_tex(tables[0], "agents") if tables else ""
    framework_table = table_tex(tables[1], "frameworks") if len(tables) > 1 else ""
    api_table = table_tex(tables[2], "api") if len(tables) > 2 else ""
    rubric_table = table_tex(tables[3], "rubric") if len(tables) > 3 else ""
    limitations_table = table_tex(tables[4], "limitations") if len(tables) > 4 else ""
    eval_table_tex = table_tex(tables[5], "evaluation-results", colspec="lr") if len(tables) > 5 else ""

    routing_table = table_tex(
        AnalysisTable(
            title="Conditional Routing Rules",
            columns=["Decision Point", "Condition", "Next Node"],
            rows=[
                ["Critic", "Evidence is insufficient and revision budget remains", "Research Agent"],
                ["Critic", "Evidence is acceptable", "Fact-Checking Agent"],
                ["Evaluator", f"Quality score $Q < \\tau$ ({EVALUATION_THRESHOLD})", "Report Writer Agent"],
                ["Evaluator", "Quality score is acceptable", "Finalize Report then Presentation"],
                ["Presentation", "Presentation generated", "Memory Agent"],
            ],
        ),
        "routing",
        colspec=r"p{0.22\linewidth}p{0.42\linewidth}p{0.28\linewidth}",
    )

    source_profile_rows = [
        [src.source_type, src.year or "n.d.", src.credibility, ", ".join(src.tags[:3])]
        for src in state.sources[:10]
    ]
    source_profile_tex = table_tex(
        AnalysisTable(
            title="Sample of Retrieved Evidence Sources",
            columns=["Type", "Year", "Credibility", "Tags"],
            rows=source_profile_rows,
        ),
        "source-profile",
        colspec="llll",
    )

    claim_checks = "\n".join(
        rf"\item \textbf{{{'Supported' if check.supported else 'Unsupported'}}}: {latex_escape(check.claim)}"
        for check in state.claim_checks
    )

    report_dir = Path(__file__).resolve().parents[2] / "report"
    capture_meta = read_capture_metadata()
    capture_note = latex_escape(capture_meta.get("details", ""))
    capture_type = capture_meta.get("capture_type", "unknown")
    screenshot_kind = "browser captures" if capture_type == "browser" else "fallback documentation renders"

    ui_figures = {
        "ui_home": optional_figure_tex(
            report_dir,
            "ui/ui_home.png",
            ui_screenshot_caption("ui_home.png"),
            "ui-home",
        ),
        "ui_workflow": optional_figure_tex(
            report_dir,
            "ui/ui_workflow.png",
            ui_screenshot_caption("ui_workflow.png"),
            "ui-workflow",
        ),
        "ui_outputs": optional_figure_tex(
            report_dir,
            "ui/ui_agent_outputs.png",
            ui_screenshot_caption("ui_agent_outputs.png"),
            "ui-outputs",
        ),
        "ui_results": optional_figure_tex(
            report_dir,
            "ui/ui_results.png",
            ui_screenshot_caption("ui_results.png"),
            "ui-results",
        ),
        "ui_figures_tab": optional_figure_tex(
            report_dir,
            "ui/ui_figures.png",
            ui_screenshot_caption("ui_figures.png"),
            "ui-figures-tab",
        ),
        "ui_downloads": optional_figure_tex(
            report_dir,
            "ui/ui_downloads.png",
            ui_screenshot_caption("ui_downloads.png"),
            "ui-downloads",
        ),
        "demo_eval": optional_figure_tex(
            report_dir,
            "results/demo_evaluation_score.png",
            "Demo evaluation score summary generated from the mock workflow run.",
            "demo-eval",
            r"0.88\linewidth",
        ),
        "demo_workflow": optional_figure_tex(
            report_dir,
            "results/demo_agent_workflow_result.png",
            "Demo workflow result summary showing agent stages and routing from the mock run.",
            "demo-workflow",
            r"0.88\linewidth",
        ),
        "demo_figures": optional_figure_tex(
            report_dir,
            "results/demo_generated_figures.png",
            "Demo figure gallery preview generated from workflow outputs.",
            "demo-figures",
            r"0.88\linewidth",
        ),
        "demo_report": optional_figure_tex(
            report_dir,
            "results/demo_report_output.png",
            "Demo report artifact preview showing generated Markdown and PDF deliverables.",
            "demo-report",
            r"0.88\linewidth",
        ),
    }

    figures = {
        "overall": figure_tex(
            "overall_system_architecture.png",
            "Overall system architecture connecting Streamlit, FastAPI, LangGraph, agents, tools, memory, and final outputs.",
            "overall-architecture",
        ),
        "communication": figure_tex(
            "agent_communication_diagram.png",
            "Agent communication through shared structured state rather than hidden chat transcripts.",
            "communication",
        ),
        "workflow": figure_tex(
            "multi_agent_workflow_diagram.png",
            "Conditional multi-agent workflow with research revision and report evaluation loops.",
            "workflow",
        ),
        "state_transition": figure_tex(
            "langgraph_state_transition_diagram.png",
            "LangGraph state transition diagram showing how status values move through the graph.",
            "state-transition",
        ),
        "report_pipeline": figure_tex(
            "report_generation_pipeline_diagram.png",
            "Report generation pipeline from retrieved sources to LaTeX/PDF and presentation artifacts.",
            "report-pipeline",
        ),
        "evaluation_pipeline": figure_tex(
            "evaluation_pipeline_diagram.png",
            "Evaluation pipeline with rubric scoring, thresholding, and revision routing.",
            "evaluation-pipeline",
        ),
        "evidence": figure_tex(
            "evidence_by_theme.png",
            "Evidence source distribution by theme from the deterministic demo corpus.",
            "evidence-theme",
        ),
        "quality": figure_tex(
            "quality_radar.png",
            "Radar chart summarizing selected quality dimensions for the prototype output.",
            "quality-radar",
            r"0.70\linewidth",
        ),
        "conceptual": figure_tex(
            "conceptual_grounding_pipeline.png",
            "Conceptual view of grounded synthesis from question to evidence-backed report.",
            "conceptual-grounding",
            r"0.82\linewidth",
        ),
    }

    return rf"""\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{longtable}}
\usepackage{{array}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\usepackage{{caption}}
\usepackage{{float}}
\usepackage{{listings}}
\usepackage{{fancyhdr}}
\usepackage{{enumitem}}
\usepackage{{tikz}}
\usepackage{{url}}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{{hyperref}}

\definecolor{{codegray}}{{RGB}}{{245,247,250}}
\definecolor{{deepteal}}{{RGB}}{{47,111,115}}
\lstset{{
  backgroundcolor=\color{{codegray}},
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  columns=fullflexible
}}

\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small Agentic Research \& Decision Intelligence Platform}}
\fancyhead[R]{{\small Final Project Report}}
\fancyfoot[C]{{\thepage}}
\renewcommand{{\headrulewidth}}{{0.4pt}}
\renewcommand{{\footrulewidth}}{{0pt}}

\title{{\textbf{{Agentic Research \& Decision Intelligence Platform}}\\
\large A Multi-Agent AI System for Evidence-Grounded Research and Decision Support}}
\author{{Final Course Project}}
\date{{\today}}

\begin{{document}}

\begin{{titlepage}}
\thispagestyle{{empty}}
\centering
\vspace*{{1.2cm}}
{{\Huge\bfseries Agentic Research \& Decision Intelligence Platform\par}}
\vspace{{0.4cm}}
{{\Large A Multi-Agent AI System for Evidence-Grounded Research and Decision Support\par}}
\vspace{{1cm}}
{{\large Demonstration Topic: {latex_escape(state.query)}\par}}
\vfill
\begin{{tabular}}{{ll}}
System mode: & Deterministic mock mode (\texttt{{USE\_MOCK\_LLM=true}})\\
Primary stack: & Python, LangGraph, FastAPI, Streamlit, SQLite, Pytest\\
Run ID: & \texttt{{{latex_escape(state.run_id)}}}\\
Final quality score: & {eval_score}/100\\
Confidence score: & {confidence}/100\\
\end{{tabular}}
\vfill
{{\large University Final Project Submission\par}}
\end{{titlepage}}

\pagenumbering{{roman}}
\begin{{abstract}}
This report documents the Agentic Research \& Decision Intelligence Platform, a multi-agent system that transforms a complex research query into an evidence-grounded academic report, figures, evaluation artifacts, and presentation. The demonstration topic---trustworthy clinical decision support with multi-agent AI---requires traceable retrieval, claim-level fact checking, critique loops, and explicit human oversight. Unlike a single-prompt chatbot, the platform routes control through typed \texttt{{WorkflowState}}, conditional LangGraph edges, and bounded revision budgets. Ten specialized agents plan, retrieve, analyze, critique, verify, visualize, write, evaluate, present, and persist results. The default execution path is fully reproducible: a local corpus of 21 verified references, deterministic mock mode, Pytest coverage, and one-command demo scripts. Optional extension points support live search and external LLM providers without changing agent contracts.
\end{{abstract}}

\tableofcontents
\listoffigures
\listoftables
\newpage
\pagenumbering{{arabic}}

\section{{Introduction}}
Research and decision-support tasks require more than fluent text generation. Practitioners need to inspect planning decisions, retrieved evidence, intermediate tables, critique notes, and citation grounding before trusting a synthesis \cite{{lewis_2020_rag}}, \cite{{yao_2022_react}}. This project implements a multi-agent platform that produces those inspectable artifacts for a demanding scenario: multi-agent AI systems for trustworthy clinical decision support. The design prioritizes auditability, reproducibility, and academic presentation quality suitable for university evaluation.

\section{{Problem Statement}}
Given a broad research or decision scenario, the system must automatically produce a professional evidence-grounded report and presentation. For the demo query, the platform must explain how multi-agent orchestration can improve clinical decision support while reducing hallucination risk. Concrete requirements include task decomposition, ranked evidence retrieval, structured comparison tables, critique with optional research revision, claim-level fact checking, figure generation, LaTeX/PDF report compilation, rubric-based evaluation with optional report revision, and persistent run memory---all without requiring paid API keys in the default grading path.

\section{{Motivation}}
Clinical decision support is a useful motivating domain because errors have high stakes and because prior reviews show that effectiveness depends on workflow integration, timing, and governance rather than model fluency alone \cite{{garg_2005_cdss}}, \cite{{kawamoto_2005_cdss}}, \cite{{sutton_2020_cdss}}. Large language models can appear authoritative while remaining unsupported or outdated \cite{{ji_2023_hallucination_survey}}, \cite{{bender_2021_stochastic_parrots}}. A multi-agent architecture makes control explicit: planning, retrieval, critique, verification, and evaluation are separate responsibilities with inspectable state transitions \cite{{weng_2023_agents}}, \cite{{langgraph_docs}}.

\section{{Related Work}}
Retrieval-augmented generation grounds generation in external evidence \cite{{lewis_2020_rag}}. ReAct interleaves reasoning traces with tool actions \cite{{yao_2022_react}}. Reflexion and Self-Refine demonstrate verbal reinforcement and iterative self-feedback \cite{{shinn_2023_reflexion}}, \cite{{madaan_2023_self_refine}}. AutoGen, CrewAI, Semantic Kernel, and Google ADK represent alternative multi-agent orchestration styles \cite{{autogen_2023}}, \cite{{crewai_docs}}, \cite{{semantic_kernel_docs}}, \cite{{google_adk_docs}}. For clinical AI, reporting frameworks such as CONSORT-AI, SPIRIT-AI, and DECIDE-AI stress transparency and implementation readiness \cite{{liu_2020_consort_ai}}, \cite{{rivera_2020_spirit_ai}}, \cite{{vasey_2022_decide_ai}}. Automated RAG evaluation methods such as RAGAS inform the rubric design \cite{{es_2023_ragas}}.

\section{{System Overview}}
The platform spans five layers: Streamlit UI and FastAPI API, graph orchestration, ten specialized agents, deterministic tool adapters, and SQLite plus filesystem outputs. Figure~\ref{{fig:overall-architecture}} summarizes the architecture. Synchronous endpoints suit the course-demo scale; the explicit state model supports future job queues and asynchronous execution.

{figures["overall"]}

\section{{Multi-Agent Architecture}}
Ten agents collaborate through \texttt{{WorkflowState}}, a typed container for the query, plan, sources, tables, critique, claim checks, figures, artifact paths, evaluation scores, and agent notes. Figure~\ref{{fig:communication}} shows that agents exchange structured fields rather than hidden chat transcripts, which improves testability and grading transparency.

{figures["communication"]}

{agent_table}

\section{{Agent Roles and Responsibilities}}
The \textbf{{Planner}} decomposes the user query into subtasks and assigns agents. The \textbf{{Research}} agent retrieves ranked sources from the mock corpus or optional external search tools. The \textbf{{Analyst}} computes coverage metrics, comparison tables, and formula blocks. The \textbf{{Critic}} inspects evidence sufficiency and can set \texttt{{needs\_revision}}. The \textbf{{Fact-Checker}} maps claims to citation markers from retrieved sources only. The \textbf{{Visualization}} agent renders architecture diagrams and evaluation charts. The \textbf{{Report Writer}} emits Markdown, LaTeX, and PDF deliverables. The \textbf{{Evaluator}} applies the rubric in Table~\ref{{tab:rubric}}. The \textbf{{Presentation}} agent produces slide artifacts. The \textbf{{Memory}} agent persists run metadata to SQLite.

\section{{LangGraph Workflow Design}}
LangGraph (or a deterministic fallback runner with identical routing rules) executes the workflow as a state graph. Figure~\ref{{fig:workflow}} shows agent ordering and revision loops; Figure~\ref{{fig:state-transition}} shows status transitions. Conditional edges are the primary mechanism that makes the system agentic rather than a fixed prompt chain \cite{{langgraph_docs}}.

{figures["workflow"]}

{figures["state_transition"]}

{routing_table}

\section{{Agentic Behavior and Conditional Routing}}
Agentic behavior here means routing decisions depend on structured state, not only on the latest model token. After analysis, \texttt{{route\_after\_critic}} returns \texttt{{research}} when evidence is weak and revision budget remains; otherwise execution proceeds to fact checking. After report writing, \texttt{{route\_after\_evaluator}} returns \texttt{{report}} when $Q < \tau$ with $\tau = {EVALUATION_THRESHOLD}$; otherwise execution proceeds to presentation. Listing~\ref{{lst:routing}} shows the core routing logic implemented in \texttt{{app/graph/nodes.py}}.

\begin{{lstlisting}}[caption={{Core conditional routing logic}},label={{lst:routing}}]
def route_after_critic(state):
    if state.needs_revision and state.revision_count <= state.max_revisions:
        return "research"
    return "fact_check"

def route_after_evaluator(state):
    if state.evaluation.total < {EVALUATION_THRESHOLD} and state.revision_count < state.max_revisions:
        state.revision_count += 1
        return "report"
    return "presentation"
\end{{lstlisting}}

\section{{State Management and Memory}}
\texttt{{WorkflowState}} is serializable and validated with Pydantic when available, with a compatibility shim for constrained environments. SQLite stores run IDs, artifact paths, evaluation totals, timestamps, and serialized state for API inspection via \texttt{{GET /runs/\{{run\_id\}}}}. Memory is used for auditability, not hidden cross-run prompt conditioning, which keeps mock-mode grading deterministic.

\section{{Tool-Use Design}}
Tools are small deterministic functions: \texttt{{search\_tools}} for mock or external retrieval, \texttt{{citation\_tools}} for markers, \texttt{{visualization\_tools}} for diagrams and charts, \texttt{{latex\_report\_tools}} for academic PDF compilation, and \texttt{{file\_tools}} for safe path handling. Agents remain orchestration-focused; tools encapsulate repeatable IO and formatting. This mirrors the tool-use pattern described in ReAct \cite{{yao_2022_react}}.

\section{{Retrieval and Citation Strategy}}
The offline corpus contains {source_count} references with DOI or official documentation URLs. Mock retrieval ranks sources by keyword overlap and credibility, yielding deterministic outputs for tests. The fact checker never invents citations; it only links claims to \texttt{{Source}} objects already present in state. Top evidence themes in the demo run were: {top_tags}.

{source_profile_tex}

\section{{Mathematical Formulation}}
The Planner decomposes a high-level user query into subtasks:
\begin{{equation}}
T = \{{t_1, t_2, \ldots, t_n\}}
\label{{eq:decomposition}}
\end{{equation}}
Each $t_i$ maps to an agent responsibility and optional dependency edges in the execution plan.

The Analyst aggregates weighted evidence signals into a confidence score:
\begin{{equation}}
C = \frac{{\sum_{{i=1}}^{{n}} w_i s_i}}{{\sum_{{i=1}}^{{n}} w_i}}
\label{{eq:confidence}}
\end{{equation}}
where $s_i$ is a quality signal (for example source credibility or coverage) and $w_i$ is its weight. The demo confidence score is {confidence}/100, computed from credibility, citation coverage, and tag diversity.

The Evaluator combines rubric dimensions into an overall quality score:
\begin{{equation}}
Q = \alpha F + \beta R + \gamma S + \delta C_q
\label{{eq:quality}}
\end{{equation}}
where $F$ is factuality, $R$ is relevance, $S$ is structure, and $C_q$ is citation quality. The implementation extends this with completeness, clarity, visual quality, and reproducibility dimensions summarized in Table~\ref{{tab:evaluation-results}}.

The graph uses a thresholded revision decision:
\begin{{equation}}
r =
\begin{{cases}}
1, & Q < \tau \\
0, & Q \geq \tau
\end{{cases}}
\label{{eq:revision}}
\end{{equation}}
When $r = 1$, the workflow routes back to the Report Writer (subject to revision budget), implementing a quality gate before presentation generation.

\section{{Implementation Details}}
The repository is organized into \texttt{{app/agents}}, \texttt{{app/graph}}, \texttt{{app/tools}}, \texttt{{app/models}}, \texttt{{app/storage}}, \texttt{{app/api}}, and \texttt{{app/ui}}. LangGraph compiles when installed; otherwise the fallback runner in \texttt{{app/graph/workflow.py}} executes identical conditional logic. External providers are configuration-driven---no API keys are hardcoded. Report compilation prefers \texttt{{latexmk}} and falls back to \texttt{{pdflatex}} plus \texttt{{bibtex}} via \texttt{{scripts/build\_report\_pdf.py}}.

\section{{FastAPI Backend Design}}
FastAPI exposes a minimal synchronous API for demo and grading. Table~\ref{{tab:api}} lists endpoints. \texttt{{POST /run}} accepts a JSON query payload, executes the workflow, and returns run metadata including artifact paths and evaluation score. File endpoints stream Markdown reports, presentations, and figure listings.

{api_table}

\section{{User Interface and Demonstration}}
A Streamlit interface (\texttt{{app/ui/streamlit\_app.py}}) provides a professor-friendly demo surface alongside the FastAPI API. The UI allows evaluators to enter a topic, launch the multi-agent workflow, inspect agent outputs, review evaluation scores, preview generated figures, and download report/presentation artifacts without writing code.

\textbf{{Why a UI was added:}} The project is easier to grade and demonstrate when workflow behavior, intermediate outputs, and final artifacts are visible in one place. The interface exposes typed agent notes, rubric scores, figure previews, and download buttons rather than hiding collaboration inside a single chat box.

\textbf{{Tabs:}} Overview (run metrics and artifact status), Workflow (pipeline timeline and conditional routing), Agents (agent cards), Results (rubric breakdown and progress bars), Figures (gallery preview), Downloads (PDF/Markdown/PPTX/JSON), and About (agentic design and limitations).

\textbf{{Mock mode:}} The sidebar defaults to deterministic mock execution using the local evidence corpus, supporting reproducible grading without paid API keys. A visible warning states that the clinical scenario is academic only.

\textbf{{Screenshot note:}} UI images in this report are {latex_escape(screenshot_kind)}. Metadata: {capture_note}.

{ui_figures["ui_home"]}

{ui_figures["ui_workflow"]}

{ui_figures["ui_outputs"]}

{ui_figures["ui_results"]}

{ui_figures["ui_figures_tab"]}

{ui_figures["ui_downloads"]}

{ui_figures["demo_eval"]}

{ui_figures["demo_workflow"]}

{ui_figures["demo_figures"]}

{ui_figures["demo_report"]}

Launch: \texttt{{streamlit run app/ui/streamlit\_app.py}}. Capture assets: \texttt{{python scripts/capture\_ui\_screenshots.py}}. See \texttt{{docs/SCREENSHOT\_GUIDE.md}}.

\section{{Report Generation Pipeline}}
The Report Writer assembles Markdown and LaTeX from tables, formulas, figures, critiques, and claim checks. Figure~\ref{{fig:report-pipeline}} shows the pipeline. Canonical deliverables are written to \texttt{{report/final\_report.tex}}, \texttt{{report/final\_report.pdf}}, and \texttt{{report/final\_report.md}}; run-specific copies are stored under \texttt{{outputs/reports/}}.

{figures["report_pipeline"]}

\section{{Evaluation Methodology}}
The Evaluator scores eight rubric dimensions from 0 to 100 using transparent heuristics tied to claim support, artifact completeness, figure count, and reproducibility features. Table~\ref{{tab:rubric}} defines criteria and weights. Figure~\ref{{fig:evaluation-pipeline}} shows threshold gating. The score measures project artifact quality, not clinical validity \cite{{es_2023_ragas}}.

{figures["evaluation_pipeline"]}

{rubric_table}

{eval_table_tex}

\section{{Results}}
The final mock run retrieved {source_count} sources, generated {len(state.figures)} figures, compiled a LaTeX PDF, produced a presentation, and saved evaluation JSON/Markdown under \texttt{{outputs/evaluation/}}. The final quality score was {eval_score}/100. Figure~\ref{{fig:evidence-theme}} shows corpus theme distribution; Figure~\ref{{fig:quality-radar}} summarizes rubric dimensions.

{figures["evidence"]}

{figures["quality"]}

\section{{Testing and Reproducibility}}
Pytest covers unit tests for each core agent, integration tests for workflow and API behavior, and an end-to-end demo test. Primary verification commands are \texttt{{python -m compileall app scripts}}, \texttt{{python scripts/run\_demo.py}}, \texttt{{python scripts/build\_report\_pdf.py}}, and \texttt{{pytest -v}}. Docker Compose files support containerized execution. Mock mode (\texttt{{USE\_MOCK\_LLM=true}}) is the supported grading default \cite{{pytest_docs}}.

\section{{Error Analysis}}
Expected failure modes include stale evidence, incomplete retrieval, weak claim-to-source alignment, shallow critique, and overconfident clinical wording. Mitigations include retrieval grounding, explicit critique, metadata-level claim checks, limitations sections, evaluator thresholds, and mandatory human review for high-stakes use. Production deployments should add passage-level entailment and source freshness scoring \cite{{ji_2023_hallucination_survey}}.

\section{{Limitations}}
Table~\ref{{tab:limitations}} summarizes prototype limitations and mitigations. The system is not clinically validated and must not be used for patient-specific diagnosis or treatment \cite{{who_2021_ai_health}}.

{limitations_table}

\section{{AI-Assisted Development Disclosure}}
This submission was developed with external AI engineering assistants used transparently as development aids. ChatGPT supported project planning, architecture discussions, prompt engineering, documentation drafting, and report structure. A Codex-style coding assistant supported source code, tests, scripts, and documentation generation. Cursor AI served as the AI-assisted IDE for refactoring, LaTeX/PDF polishing, and consistency validation. NotebookLM assisted presentation drafting and speaker notes. Equivalent tools may substitute, but the submitted repository must remain runnable without them.

AI tools were used as development assistants. The student directed project requirements, reviewed generated outputs, tested the system, selected the architecture, validated deliverables, and prepared the final submission. The student remains responsible for correctness and academic integrity.

Table~\ref{{tab:ai-dev-tools}} summarizes external development tools. These are distinct from the ten \textbf{{internal runtime agents}} (Planner, Research, Analyst, Critic, Fact-Checker, Visualization, Report Writer, Evaluator, Presentation, Memory) orchestrated by LangGraph when the platform executes. Development AI helped build the project; internal agents are part of the implemented system documented in \texttt{{docs/AI\_GUIDE.md}} and \texttt{{docs/AI\_USAGE\_GUIDE.md}}.

\begin{{table}}[H]
\centering
\caption{{AI tools used during development}}
\label{{tab:ai-dev-tools}}
\small
\begin{{tabular}}{{p{{3cm}}p{{4cm}}p{{6cm}}}}
\toprule
Tool & Purpose & Human Oversight \\
\midrule
ChatGPT & Planning, architecture, documentation, prompt engineering & Student reviewed and refined outputs \\
Codex-style assistant & Code generation, tests, scripts, docs & Student tested and validated implementation \\
Cursor AI & Refactoring, report polishing, LaTeX improvement & Student supervised edits and verified behavior \\
NotebookLM & Presentation drafting and speaker notes & Student reviewed and adapted slides \\
\bottomrule
\end{{tabular}}
\end{{table}}

\section{{Ethical Considerations}}
Clinical AI introduces automation bias, privacy risk, inequitable recommendations, and misplaced trust in fluent prose \cite{{who_2021_ai_health}}, \cite{{bender_2021_stochastic_parrots}}. This prototype is a research engineering artifact. Deployment would require PHI controls, institutional governance, security review, monitoring, audit logs, and explicit clinician responsibility.

\section{{Future Work}}
Planned extensions include live search adapters, vector retrieval over institution-approved corpora, stronger natural-language entailment for fact checking, human-in-the-loop approval checkpoints, asynchronous job queues, authentication, and formal evaluation against clinical reporting standards such as DECIDE-AI \cite{{vasey_2022_decide_ai}}.

\section{{Conclusion}}
The Agentic Research \& Decision Intelligence Platform demonstrates how graph-based multi-agent orchestration can produce transparent, evidence-grounded academic deliverables. Its contribution is the combination of typed state, conditional critique and evaluation loops, deterministic mock mode, professional LaTeX reporting, and reproducible verification scripts suitable for university final-project evaluation.

\appendix
\section{{Framework Comparison}}
{framework_table}

\section{{Conceptual Grounding Figure}}
{figures["conceptual"]}

\section{{Claim Checks}}
\begin{{itemize}}[leftmargin=*]
{claim_checks}
\end{{itemize}}

\bibliographystyle{{plain}}
\bibliography{{references}}

\end{{document}}
"""
