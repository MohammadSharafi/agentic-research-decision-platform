from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import streamlit as st

from app.graph.workflow import run_workflow
from app.ui.ui_helpers import (
    DEMO_TOPICS,
    EVALUATION_THRESHOLD,
    ROUTING_NOTES,
    TAB_NAMES,
    WORKFLOW_PIPELINE,
    agent_output_cards,
    artifact_status,
    evaluation_criteria_rows,
    evaluation_rows,
    get_output_dir,
    list_png_figures,
    resolve_evaluation_paths,
    resolve_presentation_path,
    resolve_report_path,
    resolve_report_pdf_path,
    figure_caption,
    screenshot_seed_enabled,
)

st.set_page_config(
    page_title="Agentic Research Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #ef4444, #f97316);
        color: white !important;
        border: 0;
        border-radius: 12px;
        font-weight: 800;
        padding: 0.75rem 1rem;
    }

    .hero {
        background:
          radial-gradient(circle at 15% 15%, rgba(20,184,166,0.28), transparent 28%),
          linear-gradient(135deg, #0f172a 0%, #164e63 56%, #0f766e 100%);
        color: white;
        padding: 1.35rem 1.5rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.14);
        box-shadow: 0 18px 45px rgba(2,6,23,0.22);
    }

    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 2rem;
        line-height: 1.12;
        letter-spacing: -0.035em;
    }

    .hero p {
        margin: 0.25rem 0 1rem 0;
        color: #dbeafe;
        font-size: 1rem;
        max-width: 880px;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .badge {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.24);
        border-radius: 999px;
        padding: 0.28rem 0.75rem;
        font-size: 0.82rem;
        font-weight: 800;
        color: #ffffff !important;
    }

    .section-kicker {
        color: #38bdf8 !important;
        text-transform: uppercase;
        font-size: 0.76rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }

    .app-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 8px 26px rgba(15,23,42,0.07);
        color: #0f172a !important;
    }

    .app-card * {
        color: #0f172a !important;
    }

    .app-card h3,
    .app-card h4 {
        margin: 0 0 0.3rem 0;
        line-height: 1.18;
    }

    .app-card p {
        margin: 0.25rem 0;
        color: #475569 !important;
    }

    .metric-card {
        min-height: 104px;
        border-top: 4px solid #14b8a6;
    }

    .metric-label {
        font-size: 0.78rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b !important;
    }

    .metric-value {
        font-size: 1.55rem;
        font-weight: 900;
        margin-top: 0.2rem;
        color: #0f172a !important;
        overflow-wrap: anywhere;
    }

    .metric-help {
        margin-top: 0.25rem;
        font-size: 0.86rem;
        color: #64748b !important;
    }

    .story-card {
        background: linear-gradient(135deg, #ecfeff, #f8fafc);
        border-left: 5px solid #0891b2;
    }

    .stage-card {
        display: flex;
        gap: 0.85rem;
        align-items: flex-start;
        min-height: 112px;
    }

    .stage-number {
        min-width: 2rem;
        height: 2rem;
        border-radius: 999px;
        background: #0f766e;
        color: #ffffff !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
    }

    .agent-status {
        float: right;
        background: #dcfce7;
        color: #166534 !important;
        padding: 0.16rem 0.58rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 900;
    }

    .download-title {
        font-size: 1rem;
        font-weight: 900;
        margin-bottom: 0.35rem;
    }

    .path-text {
        font-size: 0.78rem;
        color: #64748b !important;
        word-break: break-all;
        margin-top: 0.45rem;
    }

    .soft-alert {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a !important;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.85rem;
        font-weight: 700;
    }

    .soft-alert * {
        color: #1e3a8a !important;
    }

    .success-banner {
        background: #ecfdf5;
        border: 1px solid #bbf7d0;
        color: #14532d !important;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin: 0.85rem 0;
        font-weight: 800;
    }

    .success-banner * {
        color: #14532d !important;
    }

    .empty-state {
        background: #ffffff;
        color: #0f172a !important;
        border: 1px dashed #cbd5e1;
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        margin-top: 1rem;
    }

    .empty-state * {
        color: #0f172a !important;
    }

    div[data-testid="stTabs"] button p {
        font-weight: 800;
    }

    .stDownloadButton > button {
        border-radius: 12px;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "last_state" not in st.session_state:
    st.session_state["last_state"] = None
if "seed_started" not in st.session_state:
    st.session_state["seed_started"] = False


def _esc(value: object) -> str:
    return html.escape(str(value))


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Agentic Research & Decision Intelligence Platform</h1>
            <p>
                A presentation-ready multi-agent system that turns one research topic into
                evidence, analysis, critique, fact-checks, figures, a report, a slide deck,
                evaluation scores, and saved memory.
            </p>
            <div class="badge-row">
                <span class="badge">✅ Mock demo ready</span>
                <span class="badge">🧠 10 specialized agents</span>
                <span class="badge">🔁 Conditional revision loops</span>
                <span class="badge">📄 Report + PPTX outputs</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, help_text: str = "", border_color: str = "#14b8a6") -> None:
    st.markdown(
        f"""
        <div class="app-card metric-card" style="border-top-color:{border_color};">
            <div class="metric-label">{_esc(label)}</div>
            <div class="metric-value">{_esc(value)}</div>
            <div class="metric-help">{_esc(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_story_card(title: str, body: str, icon: str = "💡") -> None:
    st.markdown(
        f"""
        <div class="app-card story-card">
            <h4>{_esc(icon)} {_esc(title)}</h4>
            <p>{_esc(body)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_banner(state: Any | None) -> None:
    if state is None:
        st.markdown(
            """
            <div class="soft-alert">
                Start here: keep Mock mode selected, click <b>Run Agentic Workflow</b>,
                then present the tabs from left to right.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="success-banner">
            ✅ Workflow completed — Run ID:
            <code>{_esc(state.run_id)}</code>
            &nbsp; | &nbsp; Score:
            <b>{_esc(state.evaluation.total)}/100</b>
            &nbsp; | &nbsp; Status:
            <b>{_esc(state.status)}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


def maybe_seed_demo_state() -> None:
    if not screenshot_seed_enabled() or st.session_state["last_state"] is not None or st.session_state["seed_started"]:
        return
    st.session_state["seed_started"] = True
    with st.spinner("Seeding demo workflow for screenshot capture..."):
        st.session_state["last_state"] = run_workflow(
            "Multi-agent AI systems for trustworthy clinical decision support",
            use_mock_llm=True,
        )


def render_sidebar() -> tuple[str, bool] | None:
    st.sidebar.markdown("## 🧠 Agentic Research")
    st.sidebar.caption("Clean demo controls for your final-project presentation.")
    st.sidebar.divider()

    st.sidebar.markdown("### 1) Execution mode")
    use_mock = st.sidebar.radio(
        "Execution mode",
        options=["Mock mode (deterministic)", "Real LLM mode (requires API keys)"],
        index=0,
        label_visibility="collapsed",
    )
    use_mock_llm = use_mock.startswith("Mock")
    if use_mock_llm:
        st.sidebar.success("Recommended for presentation: stable, offline, no API keys.")
    else:
        st.sidebar.warning("Use only if API keys are configured.")

    st.sidebar.markdown("### 2) Demo topic")
    topic_choice = st.sidebar.selectbox("Preset topic", list(DEMO_TOPICS.keys()))
    query = st.sidebar.text_area("Research or decision topic", value=DEMO_TOPICS[topic_choice], height=120)

    st.sidebar.markdown("### 3) Run")
    run_clicked = st.sidebar.button("🚀 Run Agentic Workflow", type="primary", use_container_width=True)

    st.sidebar.divider()
    st.sidebar.markdown("### Presentation path")
    st.sidebar.markdown(
        """
        1. Overview: story + score  
        2. Workflow: why agentic  
        3. Agents: who did what  
        4. Results: quality score  
        5. Figures: visual proof  
        6. Downloads: report + PPTX
        """
    )

    with st.sidebar.expander("Output directory"):
        st.code(str(get_output_dir()), language="text")

    st.sidebar.info("Academic demo only — not medical advice.")

    if run_clicked:
        return query, use_mock_llm
    return None


def run_workflow_ui(query: str, use_mock_llm: bool) -> None:
    try:
        with st.status("Running 10-agent workflow...", expanded=True) as status:
            progress = st.progress(0, text="Starting planner...")
            state = run_workflow(query, use_mock_llm=use_mock_llm)
            total = max(len(WORKFLOW_PIPELINE), 1)
            for idx, (agent, icon, description) in enumerate(WORKFLOW_PIPELINE, start=1):
                st.write(f"{icon} **{agent}** — {description}")
                progress.progress(min(idx / total, 1.0), text=f"Completed {idx}/{total}: {agent}")
            status.update(label="Workflow complete", state="complete")
        st.session_state["last_state"] = state
        st.rerun()
    except Exception as exc:
        st.error(f"Workflow failed: {exc}")


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <h3>Ready for demo</h3>
            <p>
                Choose <b>Mock mode</b>, keep the clinical decision-support topic,
                and run the workflow. The output will populate every tab.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(state) -> None:
    st.markdown('<div class="section-kicker">Presentation overview</div>', unsafe_allow_html=True)
    st.subheader("What this project demonstrates")

    render_story_card(
        "Main idea",
        "This is not a single chatbot. It is a full multi-agent research pipeline with planning, evidence, critique, fact-checking, visualization, reporting, evaluation, and memory.",
        "🎯",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Run", state.run_id[:8] + "…", "Saved workflow trace")
    with c2:
        render_metric_card("Sources", str(len(state.sources)), "Ranked evidence items", "#0ea5e9")
    with c3:
        render_metric_card("Figures", str(len(state.figures)), "Generated visuals", "#8b5cf6")
    with c4:
        render_metric_card("Score", f"{state.evaluation.total}/100", f"Threshold {EVALUATION_THRESHOLD}", "#22c55e")

    c5, c6, c7 = st.columns(3)
    with c5:
        render_metric_card("Report", artifact_status(resolve_report_path(state)), "Markdown artifact")
    with c6:
        render_metric_card("PDF", artifact_status(resolve_report_pdf_path(state)), "Academic report")
    with c7:
        render_metric_card("Slides", artifact_status(resolve_presentation_path(state)), "Presentation artifact")

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("#### How to explain it")
        st.markdown(
            """
            - **Problem:** one prompt is not enough for serious research.
            - **Solution:** 10 agents collaborate through typed workflow state.
            - **Agentic part:** critic/evaluator loops can trigger revisions.
            - **Output:** report, figures, presentation, score, and memory.
            """
        )
    with right:
        st.markdown("#### Best demo order")
        st.markdown(
            """
            1. Open **Workflow** and show revision loops.  
            2. Open **Agents** and show responsibilities.  
            3. Open **Results** and show score.  
            4. Open **Figures** and show diagrams.  
            5. Open **Downloads** and show report/PPTX.
            """
        )


def render_workflow_tab(state) -> None:
    st.markdown('<div class="section-kicker">Agentic control flow</div>', unsafe_allow_html=True)
    st.subheader("Workflow with conditional revision loops")
    st.write("Use this tab to prove the system is more than a fixed prompt chain.")

    left, right = st.columns(2)
    for idx, (agent, icon, description) in enumerate(WORKFLOW_PIPELINE, start=1):
        target = left if idx % 2 else right
        with target:
            st.markdown(
                f"""
                <div class="app-card stage-card">
                    <div class="stage-number">{idx}</div>
                    <div>
                        <h4>{_esc(icon)} {_esc(agent)}</h4>
                        <p>{_esc(description)}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### Conditional routing")
    r1, r2 = st.columns(2)
    for idx, note in enumerate(ROUTING_NOTES):
        with (r1 if idx == 0 else r2):
            st.markdown(f'<div class="soft-alert">{_esc(note)}</div>', unsafe_allow_html=True)

    with st.expander("Execution plan for this run", expanded=True):
        for step in state.plan:
            st.markdown(f"- **{_esc(step.agent)}:** {_esc(step.description)}")


def render_agents_tab(state) -> None:
    st.markdown('<div class="section-kicker">Intermediate agent outputs</div>', unsafe_allow_html=True)
    st.subheader("Agents: who did what")
    cards = agent_output_cards(state)
    if not cards:
        st.warning("No agent outputs recorded.")
        return

    for idx, card in enumerate(cards, start=1):
        with st.expander(f"{idx}. {card['icon']} {card['label']} — {card['role']}", expanded=idx <= 3):
            st.markdown(
                f"""
                <div class="app-card">
                    <span class="agent-status">{_esc(card['status'])}</span>
                    <h4>{_esc(card['label'])}</h4>
                    <p><b>Role:</b> {_esc(card['role'])}</p>
                    <p><b>Output:</b> {_esc(card['content'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_results_tab(state) -> None:
    st.markdown('<div class="section-kicker">Quality evaluation</div>', unsafe_allow_html=True)
    st.subheader("Results and grading score")

    total = float(state.evaluation.total)
    passed = total >= EVALUATION_THRESHOLD
    render_story_card(
        "Quality verdict",
        f"{'Passed' if passed else 'Needs revision'}: total score is {total}/100 with threshold {EVALUATION_THRESHOLD}. This score measures artifact quality, not clinical validation.",
        "✅" if passed else "⚠️",
    )

    for name, score in evaluation_criteria_rows(state):
        st.write(f"**{name}: {score}/100**")
        st.progress(min(max(float(score) / 100.0, 0.0), 1.0))

    st.markdown("#### Full rubric")
    st.dataframe(
        {"Criterion": [r[0] for r in evaluation_rows(state)], "Score": [r[1] for r in evaluation_rows(state)]},
        use_container_width=True,
        hide_index=True,
    )


def render_figures_tab(state) -> None:
    st.markdown('<div class="section-kicker">Visual artifacts</div>', unsafe_allow_html=True)
    st.subheader("Generated figures")
    png_paths = list_png_figures(state)
    if not png_paths:
        st.warning("No PNG figures available.")
        return

    cols = st.columns(2)
    for idx, path in enumerate(png_paths[:8]):
        with cols[idx % 2]:
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            st.image(str(path), use_container_width=True)
            st.caption(f"**{path.name}** — {figure_caption(path)}")
            st.markdown("</div>", unsafe_allow_html=True)


def render_download_card(title: str, path: Path | None, mime: str, label: str, help_text: str) -> None:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="download-title">{_esc(title)}</div>', unsafe_allow_html=True)
    st.caption(help_text)
    if path:
        st.download_button(f"⬇️ Download {label}", path.read_bytes(), file_name=path.name, mime=mime, use_container_width=True)
        st.markdown(f'<div class="path-text">{_esc(path)}</div>', unsafe_allow_html=True)
    else:
        st.warning(f"{label} not available for this run.")
    st.markdown("</div>", unsafe_allow_html=True)


def render_downloads_tab(state) -> None:
    st.markdown('<div class="section-kicker">Exported artifacts</div>', unsafe_allow_html=True)
    st.subheader("Downloads for submission and presentation")

    report_path = resolve_report_path(state)
    pdf_path = resolve_report_pdf_path(state)
    presentation_path = resolve_presentation_path(state)
    eval_json, eval_md = resolve_evaluation_paths(state)

    c1, c2 = st.columns(2)
    with c1:
        render_download_card("Final PDF Report", pdf_path, "application/pdf", "PDF report", "Best file to show to the professor.")
        render_download_card(
            "Presentation",
            presentation_path,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            if presentation_path and presentation_path.suffix == ".pptx"
            else "text/markdown",
            "presentation",
            "Slide artifact generated by the workflow.",
        )
        render_download_card("Evaluation JSON", eval_json, "application/json", "evaluation JSON", "Machine-readable score breakdown.")
    with c2:
        render_download_card("Markdown Report", report_path, "text/markdown", "Markdown report", "Run-specific report generated from the workflow.")
        render_download_card("Evaluation Markdown", eval_md, "text/markdown", "evaluation Markdown", "Human-readable evaluation summary.")


def render_about_tab() -> None:
    st.markdown('<div class="section-kicker">Project defense</div>', unsafe_allow_html=True)
    st.subheader("What to say if the professor asks")

    render_story_card(
        "Why it is agentic",
        "Ten specialized agents exchange typed WorkflowState. The Critic and Evaluator can route the graph back for revision, so the workflow is conditional and inspectable.",
        "🧠",
    )
    render_story_card(
        "Technology stack",
        "Python, LangGraph-compatible workflow, FastAPI, Streamlit, SQLite, Matplotlib, LaTeX, Pytest, and generated report/presentation artifacts.",
        "🛠️",
    )
    render_story_card(
        "Academic limitation",
        "The default demo uses a static mock corpus for reproducibility. It is not a medical device and it is not clinically validated.",
        "⚠️",
    )

    with st.expander("Quick talk track"):
        st.markdown(
            """
            This project turns one complex research topic into a full workflow:
            plan, evidence, analysis, critique, fact-checking, visualizations,
            report, presentation, evaluation, and memory.
            """
        )


render_hero()
maybe_seed_demo_state()

run_request = render_sidebar()
if run_request is not None:
    query, use_mock_llm = run_request
    run_workflow_ui(query, use_mock_llm)

state = st.session_state.get("last_state")
render_status_banner(state)

tabs = st.tabs(TAB_NAMES)

renderers = [
    render_overview,
    render_workflow_tab,
    render_agents_tab,
    render_results_tab,
    render_figures_tab,
    render_downloads_tab,
    render_about_tab,
]

for tab, renderer in zip(tabs, renderers):
    with tab:
        if renderer is render_about_tab:
            renderer()
        elif state:
            renderer(state)
        else:
            render_empty_state()
