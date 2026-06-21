# Presentation Notes — Agentic Research & Decision Intelligence Platform

Use this as your same-day talk track. It is written for a professor or technical reviewer who wants to understand whether this is really agentic, reproducible, and professionally engineered.

---

## 30-Second Opening

Hello, today I am presenting my **Agentic Research & Decision Intelligence Platform**. The goal of this project is not to build one chatbot. The goal is to build a complete multi-agent research system that can plan a task, collect evidence, analyze the evidence, critique its own output, fact-check claims, generate figures, write a report, evaluate the quality, produce a presentation, and store the full run history.

For the demo scenario, I use **multi-agent AI systems for trustworthy clinical decision support**. I selected this domain because it is high-stakes, so the system must emphasize evidence, citations, limitations, human oversight, and auditability rather than unsupported autonomous decisions.

---

## 1-Minute Problem Statement

Many AI tools can answer a question, but in academic and professional settings that is not enough. A useful research assistant should be able to:

1. Break a complex question into subtasks.
2. Gather and rank evidence.
3. Analyze the evidence using structured tables and metrics.
4. Critique weak reasoning or missing evidence.
5. Fact-check important claims.
6. Generate visual artifacts and a final report.
7. Evaluate its own output against a rubric.
8. Preserve the workflow history for reproducibility.

This project implements that full pipeline as an inspectable multi-agent workflow.

---

## Core Architecture Explanation

The system has three main layers:

1. **Interface layer** — A Streamlit UI for live demonstration and a FastAPI backend for programmatic access.
2. **Agent orchestration layer** — A LangGraph-style workflow with fallback execution. This layer controls the sequence and conditional routing between agents.
3. **Artifact and memory layer** — Reports, figures, presentations, evaluation JSON, and SQLite run memory.

The important point is that this is not just a linear chain. The workflow includes revision loops. For example, if the Critic Agent finds weak evidence, the workflow can return to the Research Agent. If the Evaluator score is too low, the workflow can return to the Report Writer before finalizing.

---

## The 10 Agents

| Agent | Responsibility |
| --- | --- |
| Planner Agent | Converts the user topic into a structured execution plan. |
| Research Agent | Retrieves and ranks evidence from the local reproducible corpus. |
| Data Analyst Agent | Produces structured analysis, metrics, and comparison tables. |
| Critic Agent | Reviews weaknesses and can trigger a research revision loop. |
| Fact-Checker Agent | Checks claims against available sources and citation markers. |
| Visualization Agent | Generates figures and diagrams for the report. |
| Report Writer Agent | Creates the final Markdown and academic-style report artifacts. |
| Evaluator Agent | Scores the output across quality dimensions. |
| Presentation Agent | Generates presentation material from the final report. |
| Memory Agent | Saves run metadata, paths, scores, and state into SQLite. |

---

## Why This Project Is Agentic

I define the system as agentic for four reasons:

1. **Specialization:** Each agent has a distinct responsibility rather than one prompt doing everything.
2. **Shared state:** Agents communicate through a structured `WorkflowState` object.
3. **Conditional control flow:** The Critic and Evaluator can route the workflow back for revision.
4. **Observable outputs:** Every stage leaves notes, artifacts, scores, and saved run metadata.

So the value is not only the final answer. The value is the traceable decision process.

---

## Demo Flow — What To Show First

### Step 1 — Start with README / repository

Say:

> The repository is organized as a complete final project: backend, UI, agents, graph workflow, report generation, tests, Docker, screenshots, and documentation.

### Step 2 — Run the UI

```bash
streamlit run app/ui/streamlit_app.py
```

In the UI, use the default topic:

```text
Multi-agent AI systems for trustworthy clinical decision support
```

Keep **Mock mode** enabled. Explain:

> Mock mode is intentional for grading. It makes the demo deterministic and reproducible without paid API keys or unstable external search results.

### Step 3 — Click “Run Agentic Workflow”

While it runs, explain:

> Each stage updates the state. The system is producing not only a response, but also evidence, analysis tables, critiques, fact checks, figures, evaluation scores, and report artifacts.

### Step 4 — Show tabs in this order

1. **Overview** — show run ID, summary, score.
2. **Workflow** — explain the agent sequence and revision loops.
3. **Agents** — open a few agent cards: Planner, Critic, Evaluator, Memory.
4. **Results** — show evaluation metrics.
5. **Figures** — show generated diagrams/charts.
6. **Downloads** — show report, PDF, presentation, and evaluation artifacts.

---

## Strong Technical Points To Emphasize

- The project uses a **FastAPI backend** and a **Streamlit UI**, so it is not only a notebook.
- It supports **deterministic mock execution**, which makes the final project reproducible.
- It saves run history in **SQLite memory**.
- It generates multiple artifacts: Markdown report, LaTeX/PDF report, figures, evaluation files, and presentation material.
- It includes tests and Docker support.
- The workflow has revision loops, making it more agentic than a static pipeline.
- The clinical scenario is framed responsibly: it supports research and decision intelligence, not autonomous diagnosis.

---

## Honest Limitations To Mention

Do not hide limitations. Present them professionally:

1. The current demo uses a local mock corpus for reproducibility.
2. External real-time web search and real LLM adapters are optional future extensions.
3. The clinical domain is academic-only; it is not validated for real patient-care decisions.
4. The current system demonstrates workflow architecture and artifact generation, not regulatory-grade clinical deployment.
5. More advanced future work would add real retrieval pipelines, model adapters, human review gates, and stronger evaluation benchmarks.

Good sentence:

> I intentionally kept the demo deterministic because for a final project, reproducibility is more important than depending on unstable external APIs during grading.

---

## 5-Minute Presentation Script

Hello, today I am presenting my Agentic Research and Decision Intelligence Platform.

The motivation is that many AI systems generate a direct answer, but real research work needs more than that. We need planning, evidence collection, analysis, critique, fact-checking, visualization, reporting, evaluation, and memory. My project implements this as a complete multi-agent workflow.

The demo scenario is multi-agent AI systems for trustworthy clinical decision support. I chose this topic because clinical decision support is a high-stakes domain, so the system must be careful about evidence, limitations, citations, and human oversight.

The architecture has a Streamlit UI, a FastAPI backend, a LangGraph-style workflow, specialized agents, local evidence tools, report-generation tools, and SQLite memory. The system can run fully offline in deterministic mock mode, which makes the demo reproducible without external API keys.

The main difference from a normal chatbot is the agentic workflow. There are ten agents: Planner, Research, Data Analyst, Critic, Fact-Checker, Visualization, Report Writer, Evaluator, Presentation, and Memory. Each agent has a specific role and writes its output into shared workflow state.

The workflow is also conditional. If the Critic Agent finds weak evidence, the system can route back to Research. If the Evaluator score is below the threshold, the system can route back to Report Writer. This makes it an inspectable decision process, not only a fixed prompt chain.

In the demo, I start the Streamlit UI, keep mock mode enabled, enter the topic, and run the workflow. Then I can inspect the Overview, Workflow, Agent Outputs, Results, Figures, and Downloads tabs. The system generates the final report, figures, evaluation score, and presentation artifacts.

The most important engineering point is reproducibility. The project includes deterministic mock mode, stored run memory, generated artifacts, tests, Docker support, documentation, and screenshots. This means the professor can run it again and get a stable demonstration.

The limitation is that this is a research prototype, not a production clinical system. The current evidence source is a controlled local corpus. For future work, I would add real search adapters, stronger retrieval, human approval gates, external model adapters, and clinical validation.

In summary, this project shows how agentic AI can be used not only to answer questions, but to manage a complete research workflow with planning, evidence, critique, fact-checking, reporting, evaluation, and memory.

---

## 1-Minute Backup Script

This project is a multi-agent AI research platform. Instead of one chatbot response, it runs a full workflow with ten agents: planning, research, analysis, critique, fact-checking, visualization, report writing, evaluation, presentation, and memory. The demo topic is trustworthy clinical decision support. The system runs in deterministic mock mode, so it is reproducible without API keys. It has a Streamlit UI, FastAPI backend, SQLite memory, generated reports, figures, evaluation scores, and presentation artifacts. The most important point is that the workflow has conditional revision loops, so weak evidence or low scores can trigger another pass. This makes it more agentic, transparent, and academically defensible than a simple prompt chain.

---

## Questions You May Get — Strong Answers

### Q: Why is this agentic and not just automation?

Because the system uses specialized agents, shared structured state, conditional routing, critique loops, evaluation loops, and persistent run memory. The final output is the result of multiple decisions, not one fixed prompt.

### Q: Why use mock mode?

Mock mode makes the demo reproducible. For grading, I do not want the result to change because an external API is slow, unavailable, or returns different search results.

### Q: Can it work with real LLMs or real search?

Yes. The architecture separates agent contracts from model/search adapters. The current version prioritizes deterministic execution, but external adapters can be added without changing the core workflow design.

### Q: Is this safe for clinical use?

No, not as-is. It is an academic research prototype. For real clinical use, it would require validated data pipelines, human review, regulatory review, privacy controls, audit logs, and clinical evaluation.

### Q: What is the strongest part of the project?

The strongest part is the complete end-to-end workflow: UI, API, multiple agents, conditional loops, generated artifacts, evaluation, memory, tests, and reproducibility.

### Q: What would you improve next?

I would add real retrieval over academic papers, better human-in-the-loop review, stronger benchmarking, real model adapters, and a more advanced dashboard for tracing agent decisions.

---

## Final Closing Sentence

The main contribution of this project is showing a complete, reproducible, and inspectable agentic research workflow — from a user question to evidence, analysis, critique, fact-checking, visualization, final report, presentation, evaluation, and stored memory.
