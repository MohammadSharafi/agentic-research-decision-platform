# AI Guide — Internal Runtime Agents

> **Note:** This file describes the **AI agents implemented inside the project** (runtime behavior). For information about **external AI tools used during development** (ChatGPT, Codex-style assistants, Cursor AI, NotebookLM), see [`docs/AI_USAGE_GUIDE.md`](AI_USAGE_GUIDE.md).

---

## Overview

The Agentic Research & Decision Intelligence Platform implements ten specialized agents that collaborate through shared `WorkflowState`. LangGraph compiles the workflow when available; otherwise a deterministic fallback runner executes the same conditional routing. In default mock mode (`USE_MOCK_LLM=true`), agents run without paid external LLM API calls.

---

## Agent Architecture

```text
Streamlit / FastAPI
        ↓
LangGraph Workflow (or fallback runner)
        ↓
Planner → Research → Analyst → Critic
              ↑___________|
Critic → Fact-Checker → Visualization → Report Writer → Evaluator
              ↑______________________________|
Evaluator → Finalize Report → Presentation → Memory
```

Agents do not chat in an unstructured group thread. They read and write **typed state fields**, which makes execution auditable and testable.

---

## Agent Responsibilities

| Agent | What it does | State fields used |
| --- | --- | --- |
| Planner | Breaks the query into subtasks and assigns agents | `plan` |
| Research | Retrieves sources from mock data or optional search adapters | `sources` |
| Data Analyst | Computes evidence metrics, tables, formulas, and comparisons | `analysis`, `tables` |
| Critic | Reviews evidence quality, bias, uncertainty, and revision needs | `critique`, `needs_revision` |
| Fact-Checker | Checks major claims against tagged sources and citation markers | `claim_checks` |
| Visualization | Generates Mermaid diagrams, PNG/SVG figures, and charts | `figures` |
| Report Writer | Creates Markdown, LaTeX, PDF, and reference files | `report_path`, `report_pdf_path` |
| Evaluator | Scores output quality using a transparent rubric | `evaluation` |
| Presentation | Creates Markdown slides and PPTX when supported | `presentation_path` |
| Memory | Saves run metadata and state to SQLite | database record |

---

## Agent Prompt Contracts

Mock mode is deterministic and does not call a live LLM. Production prompts should follow the same contract:

| Agent | Prompt contract |
| --- | --- |
| Planner | Decompose the user query into subtasks, assign agents, and preserve dependencies. |
| Research | Retrieve relevant sources, summarize them, and return structured `Source` records only. |
| Analyst | Convert evidence into metrics, comparisons, tables, and mathematical signals. |
| Critic | Identify missing evidence, bias, uncertainty, and decide whether revision is required. |
| Fact-Checker | Check major claims against retrieved sources and flag unsupported claims. |
| Visualization | Generate architecture, workflow, state, pipeline, and evaluation figures. |
| Report Writer | Produce academic report artifacts with citations, equations, tables, and figures. |
| Evaluator | Score outputs using a transparent rubric and trigger revision when needed. |
| Presentation | Generate a concise slide narrative for project defense. |
| Memory | Persist run state for traceability, not hidden prompt conditioning. |

### Prompt structure (production)

- **Role:** agent identity and responsibility.
- **Inputs:** relevant fields from `WorkflowState`.
- **Required output schema:** Pydantic-compatible model fields.
- **Safety constraints:** cite sources, expose uncertainty, avoid clinical diagnosis.
- **Revision behavior:** update state without overwriting unrelated fields.

---

## State Passing

All agents receive and return `WorkflowState`. Key fields:

`run_id`, `query`, `plan`, `sources`, `notes`, `analysis`, `tables`, `critique`, `needs_revision`, `claim_checks`, `figures`, `report_path`, `report_pdf_path`, `presentation_path`, `evaluation`, `status`, `errors`, `revision_count`, `max_revisions`, `use_mock_llm`

Each agent appends an `AgentMessage` to `notes`, preserving human-readable execution rationale alongside machine-readable artifacts.

---

## Conditional Routing

| Route function | Condition | Next step |
| --- | --- | --- |
| `route_after_critic` | Evidence insufficient and revision budget remains | Research Agent |
| `route_after_critic` | Evidence acceptable | Fact-Checker |
| `route_after_evaluator` | Quality score below threshold (τ = 78) | Report Writer (revision) |
| `route_after_evaluator` | Quality score acceptable | Finalize Report → Presentation |

Implementation: `app/graph/nodes.py` and `app/graph/workflow.py`.

---

## Tool Use

Agents call narrow deterministic tools rather than embedding all logic inline:

| Tool module | Responsibility |
| --- | --- |
| `search_tools.py` | Mock/offline search and optional external adapters |
| `citation_tools.py` | Citation markers and numbered references |
| `visualization_tools.py` | Mermaid, PNG/SVG diagrams, Matplotlib charts |
| `latex_report_tools.py` | LaTeX report generation and PDF compilation |
| `report_tools.py` | Markdown tables and fallback PDF export |
| `file_tools.py` | Safe file creation and copying |

---

## Memory

The Memory Agent stores run ID, query, status, report path, presentation path, evaluation score, and serialized state in SQLite (`app/storage/memory.py`). Memory supports API inspection via `GET /runs/{run_id}` and is **not** used for hidden cross-run prompt conditioning in mock mode.

---

## Mock Mode

Set in `.env` or environment:

```bash
USE_MOCK_LLM=true
```

Effects:

- Deterministic agent behavior without paid API keys.
- Local mock corpus for evidence retrieval.
- Reproducible outputs for grading and Pytest.
- Same agent contracts as production mode.

Demo command:

```bash
python scripts/run_demo.py
```

---

## Model Provider Abstraction

Real LLM providers are extension points, not hardcoded dependencies:

1. Set `USE_MOCK_LLM=false`.
2. Add keys to `.env` (`OPENAI_API_KEY`, etc.).
3. Implement adapters behind agent or tool boundaries without changing `WorkflowState` contracts.

Document new variables in `.env.example`. Never commit secrets.

---

## Add a New Agent

1. Create `app/agents/my_agent.py` with `run(self, state: WorkflowState) -> WorkflowState`.
2. Add a node wrapper in `app/graph/nodes.py`.
3. Register the node and edges in `app/graph/workflow.py`.
4. Add unit tests under `tests/unit/`.
5. Update this guide and `docs/ARCHITECTURE.md`.

---

## Test an Agent

```bash
pytest tests/unit/test_planner_agent.py -v
pytest tests/unit/ -v
pytest tests/integration/test_workflow.py -v
```

Each agent has a dedicated unit test. Integration and end-to-end tests validate graph routing and artifact generation.

---

## Evaluate Output Quality

The Evaluator Agent scores factuality, relevance, completeness, structure, citation quality, clarity, visual quality, and reproducibility. Results are saved to `outputs/evaluation/{run_id}_evaluation.json` and `.md`. Scores measure **artifact quality**, not clinical validity.

---

## Related Documentation

- External AI tool disclosure: [`docs/AI_USAGE_GUIDE.md`](AI_USAGE_GUIDE.md)
- System architecture: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- Evaluation rubric: [`docs/EVALUATION.md`](EVALUATION.md)
- Testing: [`docs/TESTING_GUIDE.md`](TESTING_GUIDE.md)
