# AI Usage Guide

## 1. Purpose

This document explains how external AI tools were used during the development of the **Agentic Research & Decision Intelligence Platform**. It exists to support transparent, responsible academic submission. A professor reviewing this project should be able to distinguish:

- which AI tools assisted development,
- how they were used,
- what the student reviewed and validated,
- and how those tools differ from the **internal runtime agents** implemented inside the system.

AI tools were used as engineering assistants. The student directed project requirements, reviewed generated outputs, tested the system, selected the architecture, validated deliverables, and prepared the final submission.

---

## 2. AI Tools Used

| Tool | Purpose | Usage in This Project | Human Oversight |
| --- | --- | --- | --- |
| **ChatGPT** | Planning, architecture, documentation, prompt engineering | Project scoping, multi-agent design discussions, report structure, debugging guidance, academic writing support | Student reviewed, edited, and approved all plans and text |
| **OpenAI Codex / Codex-style coding assistant** | Code generation and improvement | Source code, project structure, tests, scripts, configuration templates, documentation drafts | Student tested code, fixed issues, and validated behavior with Pytest |
| **Cursor AI** | AI-assisted IDE | Refactoring, LaTeX/PDF report polishing, consistency checks, integration fixes, deliverable improvements | Student supervised edits and verified runtime behavior |
| **NotebookLM** | Presentation support | Turning project documents and reports into presentation material and speaker notes | Student reviewed, adapted, and finalized slides |
| **Python libraries and automation scripts** | Reproducible execution | `run_demo.py`, `build_report_pdf.py`, Pytest, Docker — no live external LLM required in mock mode | Student ran verification commands and checked artifacts |

Equivalent coding assistants may substitute for the tools above. The **submitted project must remain runnable without depending on those development tools**.

---

## 3. Human Role and Responsibility

The student remained responsible for the final submission. Specifically, the student:

- Defined the project requirements and demonstration topic.
- Chose the multi-agent system direction and LangGraph-style orchestration.
- Requested critique loops, fact checking, evaluation gates, and reproducible mock mode.
- Reviewed generated code, reports, figures, and presentations.
- Ran tests (`pytest -v`), demo scripts, and PDF build verification.
- Checked references, limitations, and ethical framing.
- Prepared and submitted the final deliverables.

The student—not the development AI tools—is accountable for correctness, transparency, and submission quality.

---

## 4. AI-Assisted Development Workflow

```text
Student requirements
  → ChatGPT planning and prompt engineering
  → Codex-style implementation (code, tests, docs)
  → Cursor refinement and validation
  → NotebookLM presentation drafting
  → Student review, testing, and final submission
```

At each step, generated material was treated as a **draft** until reviewed, tested, or validated by the student.

---

## 5. Difference Between Development AI and Project AI

Two distinct categories of AI appear in this submission:

### Development AI (external tools)

External tools such as ChatGPT, Codex-style assistants, Cursor AI, and NotebookLM helped **build** the repository, documentation, and deliverables. They are not part of the runtime system.

### Project AI (internal runtime agents)

The implemented platform contains its own **internal multi-agent workflow**:

| Internal Agent | Runtime Role |
| --- | --- |
| Planner Agent | Task decomposition |
| Research Agent | Evidence retrieval |
| Analyst Agent | Metrics and tables |
| Critic Agent | Critique and revision routing |
| Fact-Checker Agent | Claim grounding |
| Visualization Agent | Diagrams and charts |
| Report Writer Agent | Report and PDF generation |
| Evaluator Agent | Rubric scoring |
| Presentation Agent | Slide generation |
| Memory Agent | SQLite persistence |

**Development tools are not the same as internal runtime agents.** The former assisted engineering; the latter are software components orchestrated by LangGraph (or the fallback runner) when `POST /run` or `python scripts/run_demo.py` is executed.

For internal agent design, see `docs/AI_GUIDE.md`.

---

## 6. Internal AI Agents

| Agent | Role | Input | Output |
| --- | --- | --- | --- |
| Planner | Decompose query into subtasks | User query | Execution plan |
| Research | Retrieve evidence | Query and plan | Ranked `Source` objects |
| Analyst | Compute metrics and tables | Sources | Analysis dict, tables |
| Critic | Review evidence quality | Analysis, sources | `needs_revision`, critique |
| Fact-Checker | Ground claims | Approved analysis | `ClaimCheck` objects |
| Visualization | Generate figures | Workflow state | PNG/SVG/Mermaid assets |
| Report Writer | Produce academic artifacts | Full state | Markdown, LaTeX, PDF |
| Evaluator | Score output quality | Report, figures, checks | `EvaluationScore` |
| Presentation | Create slide deck | Evaluated state | Markdown/PPTX |
| Memory | Persist run record | Completed state | SQLite entry |

In default **mock mode** (`USE_MOCK_LLM=true`), these agents run deterministically without calling paid external LLM APIs.

---

## 7. Responsible AI Use

This project follows these responsible-use practices:

- **No secret keys committed** — API keys belong in `.env`, not in source control.
- **Mock mode provided** — reproducible grading without paid providers.
- **Outputs evaluated** — Evaluator Agent applies a transparent rubric; artifacts are inspectable.
- **Claims require review** — Fact-checker uses retrieved sources; human review is still required.
- **Clinical demo is academic only** — not medical advice or a medical device.
- **Human review required** — especially before any real-world or clinical-adjacent use.

---

## 8. Limitations of AI Assistance

AI-assisted development has known limitations:

- **AI-generated code can contain bugs** — automated tests reduce but do not eliminate this risk.
- **AI-generated references must be checked** — DOIs and URLs were verified manually where used.
- **AI-generated reports can contain unsupported claims** — critique, fact checking, and student review mitigate this.
- **Automated tests do not replace human evaluation** — Pytest validates engineering behavior, not clinical validity.
- **Presentation content should be reviewed before delivery** — slides were adapted by the student after AI drafting support.

---

## 9. Reproducibility

The project runs without external development AI tools and without paid runtime LLM APIs in mock mode:

```bash
USE_MOCK_LLM=true python scripts/run_demo.py
python scripts/build_report_pdf.py
pytest -v
```

These commands regenerate reports, figures, evaluation files, and presentations from the implemented system.

---

## 10. Summary

> This project uses AI tools transparently as engineering assistants while maintaining human oversight, reproducibility, testing, and documentation.

External AI supported planning, implementation, documentation, and presentation drafting. The student defined requirements, supervised development, reviewed outputs, tested the system, and prepared the final submission. The submitted platform additionally implements its own internal multi-agent AI workflow, documented in `docs/AI_GUIDE.md`.
