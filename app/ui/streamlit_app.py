from __future__ import annotations

import html
import sys
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import streamlit as st

from app.config.settings import get_settings
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

st.set_page_config(page_title="Agentic Research Platform", page_icon="🧠", layout="wide")

st.markdown(
    """
<style>
:root { --bg:#f8fafc; --panel:#ffffff; --text:#0f172a; --muted:#475569; --line:#cbd5e1; --brand:#0f766e; --accent:#ef4444; }
html, body, .stApp, [data-testid="stAppViewContainer"] { background:var(--bg)!important; color:var(--text)!important; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif!important; letter-spacing:0!important; }
[data-testid="stHeader"] { background:var(--bg)!important; }
.block-container { max-width:1120px; padding-top:1.1rem; padding-bottom:2rem; }
h1,h2,h3,h4,h5,h6,p,li,label,span,div { letter-spacing:0!important; }
[data-testid="stSidebar"] { background:#eef2f7!important; border-right:1px solid #dbe4ea!important; }
[data-testid="stSidebar"] * { color:var(--text)!important; }

/* Force readable Streamlit controls */
div[data-baseweb="select"]>div, div[data-baseweb="base-input"], textarea, input { background:#fff!important; color:var(--text)!important; border-color:var(--line)!important; }
div[data-baseweb="select"] *, div[data-baseweb="base-input"] *, textarea, input { color:var(--text)!important; }
textarea::placeholder, input::placeholder { color:#64748b!important; opacity:1!important; }
div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"], div[role="option"], div[role="option"] * { background:#fff!important; color:var(--text)!important; }

/* Sidebar run button only */
[data-testid="stSidebar"] .stButton>button { background:linear-gradient(135deg,#ef4444,#f97316)!important; color:white!important; border:0!important; border-radius:12px!important; font-weight:850!important; padding:.72rem 1rem!important; }
[data-testid="stSidebar"] .stButton>button * { color:white!important; }

/* Tabs: keep inactive tabs visible */
div[data-baseweb="tab-list"] { gap:1rem!important; border-bottom:1px solid #e2e8f0!important; }
button[data-baseweb="tab"] { background:transparent!important; opacity:1!important; color:#334155!important; padding:.65rem 0!important; }
button[data-baseweb="tab"] p, button[data-baseweb="tab"] span, button[data-baseweb="tab"] div { color:#334155!important; font-weight:800!important; opacity:1!important; }
button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span, button[data-baseweb="tab"][aria-selected="true"] div { color:var(--accent)!important; }
button[data-baseweb="tab"][aria-selected="true"] { border-bottom:2px solid var(--accent)!important; }

/* Download buttons: prevent black-on-black */
div[data-testid="stDownloadButton"] button { background:#ffffff!important; color:#0f172a!important; border:1px solid #cbd5e1!important; border-radius:12px!important; font-weight:850!important; }
div[data-testid="stDownloadButton"] button * { color:#0f172a!important; }
div[data-testid="stDownloadButton"] button:hover { background:#f1f5f9!important; border-color:#94a3b8!important; }

.hero { background:linear-gradient(135deg,#0f172a 0%,#155e75 58%,#0f766e 100%); color:white!important; border-radius:18px; padding:1.35rem 1.55rem; margin-bottom:1rem; box-shadow:0 16px 38px rgba(15,23,42,.18); }
.hero * { color:white!important; }
.hero h1 { margin:0 0 .35rem 0; font-size:1.85rem; line-height:1.15; font-weight:900; }
.hero p { margin:.25rem 0 .9rem 0; color:#e0f2fe!important; line-height:1.55; }
.badge { display:inline-flex; margin:.25rem .4rem .1rem 0; background:rgba(255,255,255,.13); border:1px solid rgba(255,255,255,.25); border-radius:999px; padding:.28rem .75rem; font-size:.82rem; font-weight:850; }
.notice { background:#eff6ff; color:#1e3a8a!important; border:1px solid #bfdbfe; border-radius:14px; padding:.85rem 1rem; margin:.85rem 0; font-weight:750; }
.success-box { background:#ecfdf5; color:#14532d!important; border:1px solid #bbf7d0; border-radius:14px; padding:.85rem 1rem; margin:.85rem 0; font-weight:800; }
.notice *, .success-box * { color:inherit!important; }
.card { background:var(--panel)!important; color:var(--text)!important; border:1px solid #dbe4ea; border-radius:16px; padding:1rem; margin-bottom:.85rem; box-shadow:0 8px 26px rgba(15,23,42,.055); overflow:hidden; }
.card * { color:var(--text)!important; }
.card p { color:var(--muted)!important; line-height:1.55; margin:.25rem 0; }
.metric { border-top:4px solid var(--brand); min-height:96px; }
.metric-label { color:#64748b!important; font-size:.73rem; font-weight:900; text-transform:uppercase; }
.metric-value { color:var(--text)!important; font-size:1.32rem; font-weight:900; line-height:1.15; word-break:break-word; }
.metric-help { color:#64748b!important; font-size:.80rem; margin-top:.25rem; }
.stage { display:grid; grid-template-columns:2rem minmax(0,1fr); gap:.75rem; min-height:88px; }
.num { width:2rem; height:2rem; border-radius:999px; background:var(--brand); color:white!important; display:flex; align-items:center; justify-content:center; font-weight:900; }
.kicker { color:var(--brand)!important; text-transform:uppercase; font-size:.75rem; font-weight:900; }
.status-pill { float:right; background:#dcfce7; color:#166534!important; padding:.16rem .58rem; border-radius:999px; font-size:.74rem; font-weight:900; }
.path { color:#64748b!important; font-size:.76rem; word-break:break-all; margin-top:.45rem; }
div[data-testid="stExpander"] { background:#fff!important; border:1px solid #dbe4ea!important; border-radius:14px!important; }
.stButton>button { border-radius:12px!important; font-weight:800!important; }
code { background:#e2e8f0!important; color:#0f172a!important; white-space:pre-wrap!important; word-break:break-word!important; }
</style>
""",
    unsafe_allow_html=True,
)

if "last_state" not in st.session_state:
    st.session_state["last_state"] = None
if "seed_started" not in st.session_state:
    st.session_state["seed_started"] = False


def esc(value: object) -> str:
    return html.escape(str(value))


def key_state(value: str) -> str:
    return "Configured" if value else "Missing"


def card(title: str, body: str, icon: str = "💡") -> None:
    st.markdown(f'<div class="card"><h4>{esc(icon)} {esc(title)}</h4><p>{esc(body)}</p></div>', unsafe_allow_html=True)


def metric(label: str, value: str, help_text: str = "", color: str = "#0f766e") -> None:
    st.markdown(
        f'<div class="card metric" style="border-top-color:{color};"><div class="metric-label">{esc(label)}</div><div class="metric-value">{esc(value)}</div><div class="metric-help">{esc(help_text)}</div></div>',
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
<div class="hero">
  <h1>Agentic Research & Decision Intelligence Platform</h1>
  <p>A presentation-ready multi-agent system that turns one research topic into evidence, analysis, critique, fact-checks, figures, a report, a slide deck, evaluation scores, and saved memory.</p>
  <span class="badge">✅ Mock demo ready</span><span class="badge">🧠 10 agents</span><span class="badge">🔁 Revision loops</span><span class="badge">📄 Report + PPTX</span>
</div>
""",
        unsafe_allow_html=True,
    )


def seed_demo() -> None:
    if not screenshot_seed_enabled() or st.session_state["last_state"] is not None or st.session_state["seed_started"]:
        return
    st.session_state["seed_started"] = True
    with st.spinner("Seeding demo workflow..."):
        st.session_state["last_state"] = run_workflow("Multi-agent AI systems for trustworthy clinical decision support", use_mock_llm=True)


def sidebar() -> tuple[str, bool] | None:
    settings = get_settings()
    st.sidebar.markdown("## 🧠 Agentic Research")
    st.sidebar.caption("Clean demo controls for your final-project presentation.")
    st.sidebar.divider()
    st.sidebar.markdown("### 1) Execution mode")
    mode = st.sidebar.radio("Execution mode", ["Mock mode (deterministic)", "Real LLM mode (requires API keys)"], index=0, label_visibility="collapsed")
    use_mock = mode.startswith("Mock")
    if use_mock:
        st.sidebar.success("Recommended: stable, offline, no API keys.")
    elif settings.openai_api_key or settings.tavily_api_key or settings.serpapi_api_key:
        st.sidebar.success("At least one API key is configured.")
    else:
        st.sidebar.error("No API keys found in .env.")
    with st.sidebar.expander("API key status", expanded=not use_mock):
        st.write(f"OpenAI: **{key_state(settings.openai_api_key)}**")
        st.write(f"Tavily: **{key_state(settings.tavily_api_key)}**")
        st.write(f"SerpAPI: **{key_state(settings.serpapi_api_key)}**")
    st.sidebar.markdown("### 2) Demo topic")
    topic = st.sidebar.selectbox("Preset topic", list(DEMO_TOPICS.keys()))
    query = st.sidebar.text_area("Research or decision topic", value=DEMO_TOPICS[topic], height=120)
    st.sidebar.markdown("### 3) Run")
    clicked = st.sidebar.button("🚀 Run Agentic Workflow", type="primary", use_container_width=True)
    st.sidebar.divider()
    st.sidebar.markdown("### Presentation path")
    st.sidebar.markdown("1. Overview\n2. Workflow\n3. Agents\n4. Results\n5. Figures\n6. Downloads")
    with st.sidebar.expander("Output directory"):
        st.code(str(get_output_dir()), language="text")
    if clicked:
        return query, use_mock
    return None


def run_ui(query: str, use_mock: bool) -> None:
    try:
        with st.status("Running 10-agent workflow...", expanded=True) as status:
            progress = st.progress(0, text="Starting...")
            state = run_workflow(query, use_mock_llm=use_mock)
            for idx, (name, icon, desc) in enumerate(WORKFLOW_PIPELINE, start=1):
                st.write(f"{icon} **{name}** — {desc}")
                progress.progress(idx / len(WORKFLOW_PIPELINE), text=f"Completed {idx}/{len(WORKFLOW_PIPELINE)}: {name}")
            status.update(label="Workflow complete", state="complete")
        st.session_state["last_state"] = state
        st.rerun()
    except Exception as exc:
        st.error(f"Workflow failed: {exc}")


def status(state: Any | None) -> None:
    if not state:
        st.markdown('<div class="notice">Start here: keep Mock mode selected, run the workflow, then present tabs left to right.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="success-box">✅ Workflow completed — Run ID: <code>{esc(state.run_id)}</code> | Score: <b>{esc(state.evaluation.total)}/100</b> | Status: <b>{esc(state.status)}</b></div>', unsafe_allow_html=True)


def empty() -> None:
    st.markdown('<div class="card" style="text-align:center;padding:2rem;border-style:dashed;"><h3>Ready for demo</h3><p>Choose Mock mode, keep the default topic, and run the workflow.</p></div>', unsafe_allow_html=True)


def overview(state: Any) -> None:
    st.markdown('<div class="kicker">Presentation overview</div>', unsafe_allow_html=True)
    st.subheader("What this project demonstrates")
    card("Main idea", "A full multi-agent research pipeline: planning, evidence, critique, fact-checking, visualization, reporting, evaluation, and memory.", "🎯")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("Run", state.run_id[:8] + "…", "Saved trace")
    with c2: metric("Sources", str(len(state.sources)), "Evidence items", "#0ea5e9")
    with c3: metric("Figures", str(len(state.figures)), "Generated visuals", "#8b5cf6")
    with c4: metric("Score", f"{state.evaluation.total}/100", f"Threshold {EVALUATION_THRESHOLD}", "#22c55e")
    c5, c6, c7 = st.columns(3)
    with c5: metric("Report", artifact_status(resolve_report_path(state)), "Markdown")
    with c6: metric("PDF", artifact_status(resolve_report_pdf_path(state)), "Final report")
    with c7: metric("Slides", artifact_status(resolve_presentation_path(state)), "Presentation")


def workflow(state: Any) -> None:
    st.markdown('<div class="kicker">Agentic control flow</div>', unsafe_allow_html=True)
    st.subheader("Workflow with conditional revision loops")
    left, right = st.columns(2)
    for idx, (name, icon, desc) in enumerate(WORKFLOW_PIPELINE, start=1):
        with (left if idx % 2 else right):
            st.markdown(f'<div class="card stage"><div class="num">{idx}</div><div><h4>{esc(icon)} {esc(name)}</h4><p>{esc(desc)}</p></div></div>', unsafe_allow_html=True)
    for note in ROUTING_NOTES:
        st.markdown(f'<div class="notice">{esc(note)}</div>', unsafe_allow_html=True)
    with st.expander("Execution plan for this run", expanded=True):
        for step in state.plan:
            st.markdown(f"- **{esc(step.agent)}:** {esc(step.description)}")


def agents(state: Any) -> None:
    st.markdown('<div class="kicker">Intermediate outputs</div>', unsafe_allow_html=True)
    st.subheader("Agents: who did what")
    for idx, item in enumerate(agent_output_cards(state), start=1):
        with st.expander(f"{idx}. {item['icon']} {item['label']} — {item['role']}", expanded=idx <= 3):
            st.markdown(f'<div class="card"><span class="status-pill">{esc(item["status"])}</span><h4>{esc(item["label"])}</h4><p><b>Role:</b> {esc(item["role"])}</p><p><b>Output:</b> {esc(item["content"])}</p></div>', unsafe_allow_html=True)


def results(state: Any) -> None:
    st.markdown('<div class="kicker">Quality evaluation</div>', unsafe_allow_html=True)
    st.subheader("Results and grading score")
    total = float(state.evaluation.total)
    verdict = "Passed" if total >= EVALUATION_THRESHOLD else "Needs revision"
    card("Quality verdict", f"{verdict}: total score is {total}/100 with threshold {EVALUATION_THRESHOLD}.", "✅")
    for name, score in evaluation_criteria_rows(state):
        st.write(f"**{name}: {score}/100**")
        st.progress(min(max(float(score) / 100.0, 0.0), 1.0))
    st.dataframe({"Criterion": [r[0] for r in evaluation_rows(state)], "Score": [r[1] for r in evaluation_rows(state)]}, use_container_width=True, hide_index=True)


def figures(state: Any) -> None:
    st.markdown('<div class="kicker">Visual artifacts</div>', unsafe_allow_html=True)
    st.subheader("Generated figures")
    paths = list_png_figures(state)
    if not paths:
        st.warning("No PNG figures available.")
        return
    cols = st.columns(2)
    for idx, path in enumerate(paths[:8]):
        with cols[idx % 2]:
            st.image(str(path), use_container_width=True)
            st.caption(f"**{path.name}** — {figure_caption(path)}")


def downloads(state: Any) -> None:
    st.markdown('<div class="kicker">Exported artifacts</div>', unsafe_allow_html=True)
    st.subheader("Downloads")
    report = resolve_report_path(state)
    pdf = resolve_report_pdf_path(state)
    presentation = resolve_presentation_path(state)
    eval_json, eval_md = resolve_evaluation_paths(state)
    def dl(title: str, path: Path | None, mime: str, label: str) -> None:
        st.markdown(f'<div class="card"><h4>{esc(title)}</h4>', unsafe_allow_html=True)
        if path:
            st.download_button(f"⬇️ Download {label}", path.read_bytes(), file_name=path.name, mime=mime, use_container_width=True)
            st.markdown(f'<div class="path">{esc(path)}</div>', unsafe_allow_html=True)
        else:
            st.warning(f"{label} not available.")
        st.markdown("</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        dl("Final PDF Report", pdf, "application/pdf", "PDF")
        dl("Presentation", presentation, "application/vnd.openxmlformats-officedocument.presentationml.presentation" if presentation and presentation.suffix == ".pptx" else "text/markdown", "presentation")
        dl("Evaluation JSON", eval_json, "application/json", "evaluation JSON")
    with c2:
        dl("Markdown Report", report, "text/markdown", "Markdown")
        dl("Evaluation Markdown", eval_md, "text/markdown", "evaluation Markdown")


def about(_: Any | None = None) -> None:
    st.markdown('<div class="kicker">Project defense</div>', unsafe_allow_html=True)
    st.subheader("What to say if the professor asks")
    card("Why it is agentic", "Specialized agents exchange typed workflow state, and the graph has revision loops.", "🧠")
    card("Technology stack", "Python, LangGraph-compatible workflow, FastAPI, Streamlit, SQLite, Matplotlib, LaTeX, Pytest.", "🛠️")
    card("Limitation", "The default demo uses a static mock corpus for reproducibility.", "⚠️")


hero()
seed_demo()
request = sidebar()
if request:
    run_ui(*request)
current_state = st.session_state.get("last_state")
status(current_state)
renderers = [overview, workflow, agents, results, figures, downloads, about]
for tab, renderer in zip(st.tabs(TAB_NAMES), renderers):
    with tab:
        if current_state or renderer is about:
            renderer(current_state)
        else:
            empty()
