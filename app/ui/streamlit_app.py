from __future__ import annotations

import html
import re
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
    safe_read_text,
    screenshot_seed_enabled,
)

st.set_page_config(page_title="Agentic Research Platform", page_icon="🧠", layout="wide")

st.markdown(
    """
<style>
:root { --bg:#f8fafc; --panel:#ffffff; --text:#0f172a; --muted:#475569; --line:#cbd5e1; --brand:#0f766e; --accent:#ef4444; }
html, body, .stApp, [data-testid="stAppViewContainer"] { background:var(--bg)!important; color:var(--text)!important; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif!important; letter-spacing:0!important; }
[data-testid="stHeader"] { background:var(--bg)!important; }
.block-container { max-width:1180px; padding-top:1.1rem; padding-bottom:2rem; }
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
.answer-card { background:#ffffff!important; border:1px solid #cbd5e1; border-radius:18px; padding:1.1rem 1.25rem; margin:1rem 0; box-shadow:0 10px 28px rgba(15,23,42,.06); }
.answer-card h1, .answer-card h2, .answer-card h3 { color:#0f172a!important; }
.answer-card p, .answer-card li { color:#334155!important; line-height:1.65!important; }
.query-card { background:#f8fafc!important; border:1px dashed #94a3b8; border-radius:14px; padding:.85rem 1rem; margin:.75rem 0 1rem; }
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
  <p>Ask a research, comparison, market, policy, or technical question and get the actual synthesized answer, sources, analysis, figures, score, and downloadable report.</p>
  <span class="badge">✅ Answer-first UI</span><span class="badge">🧠 10 agents</span><span class="badge">🔁 Revision loops</span><span class="badge">📄 Report + PPTX</span>
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
    has_api_key = bool(settings.openai_api_key or settings.tavily_api_key or settings.serpapi_api_key)
    default_mode_index = 1 if has_api_key else 0

    st.sidebar.markdown("## 🧠 Agentic Research")
    st.sidebar.caption("Ask a question and review the actual generated answer first.")
    st.sidebar.divider()
    st.sidebar.markdown("### 1) Execution mode")
    mode = st.sidebar.radio(
        "Execution mode",
        ["Mock mode (deterministic)", "Real LLM mode (uses configured API keys)"],
        index=default_mode_index,
        label_visibility="collapsed",
    )
    use_mock = mode.startswith("Mock")
    if use_mock:
        st.sidebar.success("Mock mode: stable, offline, reproducible.")
    elif has_api_key:
        st.sidebar.success("Real mode: API key configured.")
    else:
        st.sidebar.error("No API keys found in .env. Real mode may fall back or fail.")
    with st.sidebar.expander("API key status", expanded=not use_mock):
        st.write(f"OpenAI: **{key_state(settings.openai_api_key)}**")
        st.write(f"Tavily: **{key_state(settings.tavily_api_key)}**")
        st.write(f"SerpAPI: **{key_state(settings.serpapi_api_key)}**")

    st.sidebar.markdown("### 2) Question")
    topic = st.sidebar.selectbox("Preset topic", ["Custom question"] + list(DEMO_TOPICS.keys()))
    default_query = "Compare gold and silver prices, drivers, risks, and investment use cases."
    if topic != "Custom question":
        default_query = DEMO_TOPICS[topic]
    query = st.sidebar.text_area("Research, comparison, or decision question", value=default_query, height=145)

    st.sidebar.markdown("### 3) Run")
    clicked = st.sidebar.button("🚀 Generate Answer", type="primary", use_container_width=True)
    st.sidebar.divider()
    st.sidebar.markdown("### Review order")
    st.sidebar.markdown("1. Answer\n2. Evidence\n3. Analysis\n4. Figures\n5. Score\n6. Downloads\n7. Workflow\n8. Agents")
    with st.sidebar.expander("Output directory"):
        st.code(str(get_output_dir()), language="text")
    if clicked:
        return query, use_mock
    return None


def run_ui(query: str, use_mock: bool) -> None:
    try:
        with st.status("Running agentic answer workflow...", expanded=True) as status:
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
        st.markdown('<div class="notice">Start here: enter a comparison/research question, choose real mode if API keys are configured, then generate the answer.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="success-box">✅ Answer generated — Run ID: <code>{esc(state.run_id)}</code> | Score: <b>{esc(state.evaluation.total)}/100</b> | Status: <b>{esc(state.status)}</b></div>', unsafe_allow_html=True)


def empty() -> None:
    st.markdown('<div class="card" style="text-align:center;padding:2rem;border-style:dashed;"><h3>Ready for a question</h3><p>Enter a research or comparison prompt, then generate the answer.</p></div>', unsafe_allow_html=True)


def _clean_report_markdown(text: str, limit: int = 30000) -> str:
    text = text[:limit]
    text = re.sub(r"^#\s+Agentic Research.*?\n+", "", text, count=1, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _analysis_summary(state: Any) -> str:
    analysis = getattr(state, "analysis", {}) or {}
    for key in ("final_answer", "answer", "summary", "synthesis", "executive_summary", "conclusion"):
        value = analysis.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def answer(state: Any) -> None:
    st.markdown('<div class="kicker">Answer first</div>', unsafe_allow_html=True)
    st.subheader("Final answer for your prompt")
    st.markdown(f'<div class="query-card"><b>Question:</b><br>{esc(state.query)}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("Score", f"{state.evaluation.total}/100", f"Threshold {EVALUATION_THRESHOLD}", "#22c55e")
    with c2: metric("Sources", str(len(state.sources)), "Retrieved evidence", "#0ea5e9")
    with c3: metric("Figures", str(len(state.figures)), "Generated visuals", "#8b5cf6")
    with c4: metric("Mode", "Mock" if state.use_mock_llm else "Real", "Execution path", "#f97316")

    report = resolve_report_path(state)
    summary = _analysis_summary(state)
    if summary:
        st.markdown("### Synthesized answer")
        st.markdown(f'<div class="answer-card">{esc(summary)}</div>', unsafe_allow_html=True)

    if report:
        st.markdown("### Generated report content")
        report_text = _clean_report_markdown(safe_read_text(report, limit=35000))
        if report_text:
            st.markdown('<div class="answer-card">', unsafe_allow_html=True)
            st.markdown(report_text)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Report file exists, but no readable content was found.")
    elif not summary:
        st.warning("No generated report or answer summary was found for this run yet.")

    if state.tables:
        st.markdown("### Key structured outputs")
        for idx, table in enumerate(state.tables[:2], start=1):
            with st.expander(f"Table {idx}: {table.title}", expanded=idx == 1):
                st.dataframe({col: [row[i] if i < len(row) else "" for row in table.rows] for i, col in enumerate(table.columns)}, use_container_width=True)


def evidence(state: Any) -> None:
    st.markdown('<div class="kicker">Evidence used</div>', unsafe_allow_html=True)
    st.subheader("Sources and claim grounding")
    if not state.sources:
        st.warning("No sources were attached to this run.")
    for idx, source in enumerate(state.sources, start=1):
        with st.expander(f"{idx}. {source.title}", expanded=idx <= 3):
            st.write(f"**Type:** {source.source_type}")
            st.write(f"**Year:** {source.year or 'n.d.'}")
            st.write(f"**Credibility:** {source.credibility}")
            if source.tags:
                st.write(f"**Tags:** {', '.join(source.tags)}")
            st.write(source.summary)
            if source.url:
                st.write(source.url)

    if state.claim_checks:
        st.markdown("### Claim checks")
        for check in state.claim_checks:
            label = "Supported" if check.supported else "Unsupported / needs caution"
            st.write(f"**{label}:** {check.claim}")
            if check.citations:
                st.caption("Citations: " + ", ".join(check.citations))
            if check.note:
                st.caption(check.note)


def analysis(state: Any) -> None:
    st.markdown('<div class="kicker">Analysis outputs</div>', unsafe_allow_html=True)
    st.subheader("Tables, metrics, and structured analysis")
    if not state.tables:
        st.warning("No analysis tables were generated.")
        return
    for idx, table in enumerate(state.tables, start=1):
        with st.expander(f"{idx}. {table.title}", expanded=idx <= 2):
            data = {col: [row[i] if i < len(row) else "" for row in table.rows] for i, col in enumerate(table.columns)}
            st.dataframe(data, use_container_width=True, hide_index=True)


def workflow(state: Any) -> None:
    st.markdown('<div class="kicker">Workflow details</div>', unsafe_allow_html=True)
    st.subheader("How the answer was produced")
    left, right = st.columns(2)
    for idx, (name, icon, desc) in enumerate(WORKFLOW_PIPELINE, start=1):
        with (left if idx % 2 else right):
            st.markdown(f'<div class="card stage"><div class="num">{idx}</div><div><h4>{esc(icon)} {esc(name)}</h4><p>{esc(desc)}</p></div></div>', unsafe_allow_html=True)
    for note in ROUTING_NOTES:
        st.markdown(f'<div class="notice">{esc(note)}</div>', unsafe_allow_html=True)
    with st.expander("Execution plan for this run", expanded=False):
        for step in state.plan:
            st.markdown(f"- **{esc(step.agent)}:** {esc(step.description)}")


def agents(state: Any) -> None:
    st.markdown('<div class="kicker">Agent logs</div>', unsafe_allow_html=True)
    st.subheader("Agent execution details")
    for idx, item in enumerate(agent_output_cards(state), start=1):
        with st.expander(f"{idx}. {item['icon']} {item['label']} — {item['role']}", expanded=False):
            st.markdown(f'<div class="card"><span class="status-pill">{esc(item["status"])}</span><h4>{esc(item["label"])}</h4><p><b>Role:</b> {esc(item["role"])}</p><p><b>Output:</b> {esc(item["content"])}</p></div>', unsafe_allow_html=True)


def results(state: Any) -> None:
    st.markdown('<div class="kicker">Quality score</div>', unsafe_allow_html=True)
    st.subheader("Evaluation and grading score")
    total = float(state.evaluation.total)
    verdict = "Passed" if total >= EVALUATION_THRESHOLD else "Needs revision"
    card("Quality verdict", f"{verdict}: total score is {total}/100 with threshold {EVALUATION_THRESHOLD}.", "✅")
    for name, score in evaluation_criteria_rows(state):
        st.write(f"**{name}: {score}/100**")
        st.progress(min(max(float(score) / 100.0, 0.0), 1.0))
    st.dataframe({"Criterion": [r[0] for r in evaluation_rows(state)], "Score": [r[1] for r in evaluation_rows(state)]}, use_container_width=True, hide_index=True)


def figures(state: Any) -> None:
    st.markdown('<div class="kicker">Visual outputs</div>', unsafe_allow_html=True)
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


hero()
seed_demo()
request = sidebar()
if request:
    run_ui(*request)
current_state = st.session_state.get("last_state")
status(current_state)
renderers = [answer, evidence, analysis, figures, results, downloads, workflow, agents]
tab_names = ["Answer", "Evidence", "Analysis", "Figures", "Score", "Downloads", "Workflow", "Agents"]
for tab, renderer in zip(st.tabs(tab_names), renderers):
    with tab:
        if current_state:
            renderer(current_state)
        else:
            empty()
