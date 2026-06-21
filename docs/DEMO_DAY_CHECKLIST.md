# Demo Day Checklist

This checklist is optimized for a same-day professor presentation.

---

## Before You Present

Run these commands from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Use deterministic mode:

```bash
export USE_MOCK_LLM=true
```

Optional quick verification:

```bash
pytest -q
python scripts/run_demo.py
```

Start the UI:

```bash
streamlit run app/ui/streamlit_app.py
```

Keep these files open in separate tabs:

- `README.md`
- `PRESENTATION.md`
- `docs/USER_GUIDE.md`
- `app/graph/workflow.py`
- `app/graph/nodes.py`
- `app/models/schemas.py`

---

## Main Demo Topic

Use this exact topic unless your professor asks for another one:

```text
Multi-agent AI systems for trustworthy clinical decision support
```

Why this topic works well:

- It sounds serious and academic.
- It connects AI agents with a high-stakes domain.
- It gives you a reason to discuss evidence, citations, limitations, human oversight, and safety.
- It matches the existing report and screenshots.

---

## Best Presentation Order

### 1. Repository overview

Show the README and say:

> This is a complete final project, not only a script. It includes backend, UI, agents, workflow orchestration, reports, figures, tests, Docker support, and documentation.

### 2. Architecture

Open `app/graph/workflow.py` and explain:

> The workflow first tries LangGraph, and if that is not available, it still has a deterministic fallback runner. This makes the project more robust for demo and grading.

Show the conditional logic:

- Critic can route back to Research.
- Evaluator can route back to Report Writer.

### 3. Agents

Open `app/graph/nodes.py` and explain:

> Each node maps to a specialized agent. This keeps responsibilities separated and makes the system easier to inspect.

### 4. Shared state

Open `app/models/schemas.py` and explain:

> All intermediate results are stored in `WorkflowState`: plan, sources, notes, analysis, critique, claim checks, figures, report paths, evaluation score, and errors.

### 5. Streamlit UI

Run the UI and show tabs in this order:

1. Overview
2. Workflow
3. Agents
4. Results
5. Figures
6. Downloads

### 6. Artifacts

Show generated outputs:

- Final report
- PDF report if available
- Figures
- Presentation
- Evaluation JSON

---

## What To Say While The Workflow Runs

Use this short explanation:

> The system is not only producing a final text answer. It is producing a full trace: plan, evidence, analysis, critique, fact-checking, visualizations, report, presentation, evaluation, and saved memory. This traceability is the main value of the project.

---

## What To Emphasize For Grading

| Grading Area | What To Say |
| --- | --- |
| Agentic design | Ten specialized agents with conditional revision loops. |
| Engineering | FastAPI backend, Streamlit UI, SQLite memory, tests, Docker. |
| Reproducibility | Mock mode gives deterministic execution without API keys. |
| Research quality | Evidence, citations, critique, fact-checking, and evaluation. |
| Professional output | Markdown/PDF report, figures, presentation, and screenshots. |
| Responsible AI | Human oversight and no autonomous clinical decision claims. |

---

## Demo Failure Backup Plan

If Streamlit does not start:

```bash
USE_MOCK_LLM=true python scripts/run_demo.py
```

Then show:

- Console output with run ID, report path, presentation path, evaluation score, and figure count.
- Existing `report/final_report.pdf`.
- Existing screenshots under `report/assets/ui/`.
- `PRESENTATION.md` as your prepared speaking notes.

Say:

> The live UI is only one interface. The core workflow can also run from CLI and still generates the same artifact types.

---

## Avoid These Mistakes

- Do not say it is clinically validated.
- Do not say it replaces doctors.
- Do not say mock mode is a weakness. Explain it as reproducibility.
- Do not spend too long on installation.
- Do not show too much code unless asked.
- Do not hide limitations; explain them professionally.

---

## Best Final Sentence

> The result is a reproducible agentic research pipeline that converts a complex topic into a traceable workflow: plan, evidence, analysis, critique, fact-checking, visualizations, report, presentation, evaluation, and memory.
