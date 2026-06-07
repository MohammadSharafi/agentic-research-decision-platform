from __future__ import annotations

import sys
from pathlib import Path

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
    safe_read_text,
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
    .block-container { padding-top: 1rem; max-width: 1200px; }
    .hero {
        background: linear-gradient(135deg, #1f4e5f 0%, #2f6f73 55%, #3d8b8f 100%);
        color: white;
        padding: 1.6rem 1.8rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0 0 0.35rem 0; font-size: 1.9rem; }
    .hero p { margin: 0.2rem 0 0.9rem 0; opacity: 0.95; }
    .badge-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }
    .badge {
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.28);
        border-radius: 999px;
        padding: 0.2rem 0.75rem;
        font-size: 0.82rem;
        font-weight: 600;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.65rem 0.85rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }
    .agent-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2f6f73;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
    }
    .workflow-card {
        background: #f8fafc;
        border: 1px solid #dbe4ea;
        border-radius: 12px;
        padding: 0.8rem 0.95rem;
        margin-bottom: 0.55rem;
    }
    .download-panel {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "last_state" not in st.session_state:
    st.session_state["last_state"] = None
if "seed_started" not in st.session_state:
    st.session_state["seed_started"] = False


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Agentic Research & Decision Intelligence Platform</h1>
            <p>A multi-agent AI system for planning, research, analysis, critique, fact-checking,
            report generation, evaluation, and presentation.</p>
            <div class="badge-row">
                <span class="badge">Mock Mode Available</span>
                <span class="badge">10-Agent Workflow</span>
                <span class="badge">Academic Final Project</span>
            </div>
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


def render_sidebar() -> str | None:
    st.sidebar.markdown("### Agentic Research Platform")
    st.sidebar.caption("University final-project demonstration interface.")
    st.sidebar.divider()

    st.sidebar.markdown("#### Run Settings")
    use_mock = st.sidebar.radio(
        "Execution mode",
        options=["Mock mode (deterministic)", "Real LLM mode (requires API keys)"],
        index=0,
    )
    use_mock_llm = use_mock.startswith("Mock")

    st.sidebar.markdown("#### Demo Topic")
    topic_choice = st.sidebar.selectbox("Preset topic", list(DEMO_TOPICS.keys()), label_visibility="collapsed")
    query = st.sidebar.text_area("Research or decision topic", value=DEMO_TOPICS[topic_choice], height=110)

    run_clicked = st.sidebar.button("Run Agentic Workflow", type="primary", use_container_width=True)

    st.sidebar.divider()
    st.sidebar.markdown("#### Quick Instructions")
    st.sidebar.markdown(
        "1. Select mock mode\n2. Choose a demo topic\n3. Click **Run Agentic Workflow**\n4. Review tabs for outputs\n5. Download artifacts"
    )
    st.sidebar.markdown("#### Output Directory")
    st.sidebar.code(str(get_output_dir()), language="text")
    st.sidebar.warning("Clinical demo is academic only. Not medical advice.")

    if run_clicked:
        return query, use_mock_llm
    return None


def run_workflow_ui(query: str, use_mock_llm: bool) -> None:
    progress = st.progress(0, text="Starting multi-agent workflow...")
    try:
        with st.status("Running agents...", expanded=True) as status:
            state = run_workflow(query, use_mock_llm=use_mock_llm)
            total = max(len(WORKFLOW_PIPELINE), 1)
            for idx, (agent, _icon, description) in enumerate(WORKFLOW_PIPELINE, start=1):
                st.write(f"**{agent}** — {description}")
                progress.progress(min(idx / total, 1.0), text=f"Completed: {agent}")
            status.update(label="Workflow complete", state="complete")
        st.session_state["last_state"] = state
        st.success(f"Workflow finished successfully. Run ID: `{state.run_id}`")
    except Exception as exc:
        st.error(f"Workflow failed: {exc}")
    finally:
        progress.empty()


def render_overview(state) -> None:
    st.subheader("Overview")
    st.write(
        "Launch the multi-agent workflow, inspect intermediate outputs, and download academic artifacts. "
        "Mock mode uses a local deterministic corpus for reproducible grading."
    )
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Run ID", state.run_id[:8] + "…")
    c2.metric("Status", state.status)
    c3.metric("Sources", len(state.sources))
    c4.metric("Figures", len(state.figures))
    c5.metric("Evaluation", f"{state.evaluation.total}/100")
    c6.metric("Mode", "Mock" if state.use_mock_llm else "Real")

    c7, c8, c9 = st.columns(3)
    c7.metric("Report", artifact_status(resolve_report_path(state)))
    c8.metric("Presentation", artifact_status(resolve_presentation_path(state)))
    c9.metric("PDF", artifact_status(resolve_report_pdf_path(state)))


def render_workflow_tab(state) -> None:
    st.subheader("Workflow")
    st.caption("Conditional LangGraph-style routing with critique and evaluation loops.")
    cols = st.columns(len(WORKFLOW_PIPELINE))
    for col, (agent, icon, description) in zip(cols, WORKFLOW_PIPELINE):
        with col:
            st.markdown(
                f'<div class="workflow-card"><strong>{icon} {agent}</strong><br><span style="font-size:0.85rem;">{description}</span></div>',
                unsafe_allow_html=True,
            )
    st.markdown("**Conditional routing**")
    for note in ROUTING_NOTES:
        st.info(note)
    st.markdown("**Execution plan for this run**")
    for step in state.plan:
        st.write(f"- **{step.agent}:** {step.description}")


def render_agents_tab(state) -> None:
    st.subheader("Agents")
    cards = agent_output_cards(state)
    if not cards:
        st.warning("No agent outputs recorded.")
        return
    for card in cards:
        st.markdown(
            f"""
            <div class="agent-card">
                <strong>{card['icon']} {card['label']}</strong>
                <span style="float:right;background:#e6f4f1;color:#1f4e5f;padding:0.1rem 0.55rem;border-radius:999px;font-size:0.75rem;">
                {card['status']}</span><br>
                <span style="color:#475569;font-size:0.9rem;">{card['role']}</span><br>
                <span style="font-size:0.92rem;">{card['content']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_results_tab(state) -> None:
    st.subheader("Results")
    total = state.evaluation.total
    st.metric("Total evaluation score", f"{total}/100")
    if total >= EVALUATION_THRESHOLD:
        st.success(f"Passed quality threshold τ = {EVALUATION_THRESHOLD}.")
    else:
        st.warning(f"Below quality threshold τ = {EVALUATION_THRESHOLD}; revision would be triggered.")

    for name, score in evaluation_criteria_rows(state):
        st.write(f"**{name}**")
        st.progress(min(max(score / 100.0, 0.0), 1.0), text=f"{score}/100")

    st.dataframe(
        {"Criterion": [r[0] for r in evaluation_rows(state)], "Score": [r[1] for r in evaluation_rows(state)]},
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Score reflects artifact quality, not clinical validation.")


def render_figures_tab(state) -> None:
    st.subheader("Figures")
    png_paths = list_png_figures(state)
    if not png_paths:
        st.warning("No PNG figures available.")
        return
    cols = st.columns(2)
    for idx, path in enumerate(png_paths[:8]):
        with cols[idx % 2]:
            st.image(str(path), use_container_width=True)
            st.caption(f"**{path.name}** — {figure_caption(path)}")


def render_downloads_tab(state) -> None:
    st.subheader("Downloads")
    report_path = resolve_report_path(state)
    pdf_path = resolve_report_pdf_path(state)
    presentation_path = resolve_presentation_path(state)
    eval_json, eval_md = resolve_evaluation_paths(state)

    def panel(title: str, path: Path | None, mime: str, label: str) -> None:
        st.markdown('<div class="download-panel">', unsafe_allow_html=True)
        st.markdown(f"**{title}**")
        if path:
            st.download_button(label, path.read_bytes(), file_name=path.name, mime=mime, use_container_width=True)
            st.caption(str(path))
        else:
            st.warning(f"{label} not available for this run.")
        st.markdown("</div>", unsafe_allow_html=True)

    panel("Final PDF Report", pdf_path, "application/pdf", "PDF report")
    panel("Markdown Report", report_path, "text/markdown", "Markdown report")
    panel(
        "Presentation",
        presentation_path,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        if presentation_path and presentation_path.suffix == ".pptx"
        else "text/markdown",
        "Presentation",
    )
    panel("Evaluation JSON", eval_json, "application/json", "Evaluation JSON")
    panel("Evaluation Markdown", eval_md, "text/markdown", "Evaluation Markdown")


def render_about_tab() -> None:
    st.subheader("About")
    st.markdown(
        """
        **What makes this system agentic?** Ten specialized agents exchange typed `WorkflowState`,
        conditional graph edges route critique and evaluation loops, and outputs remain inspectable.

        **Technologies:** Python, LangGraph-compatible workflow, FastAPI, Streamlit, SQLite, Matplotlib, LaTeX, Pytest.

        **Development AI vs runtime agents:** External AI tools assisted building the repository.
        The running platform implements its own internal agents (Planner, Research, Analyst, Critic, etc.).

        See `docs/AI_USAGE_GUIDE.md` and `docs/AI_GUIDE.md` for transparency details.

        **Academic limitations:** Static mock corpus by default; metadata-level fact checking; not a medical device.
        """
    )


render_hero()
maybe_seed_demo_state()

run_request = render_sidebar()
if run_request is not None:
    query, use_mock_llm = run_request
    run_workflow_ui(query, use_mock_llm)

state = st.session_state.get("last_state")
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
            st.info("Run the workflow from the sidebar to populate this tab.")

if not state:
    st.divider()
    st.caption("Tip: use mock mode for reproducible demo runs without paid API keys.")
