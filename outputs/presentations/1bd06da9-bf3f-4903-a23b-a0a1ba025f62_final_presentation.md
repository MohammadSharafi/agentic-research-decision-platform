---
title: Agentic Research & Decision Intelligence Platform
subtitle: Final Course Project
---

# 1. Title

Agentic Research & Decision Intelligence Platform  
Topic: Multi-agent AI systems for trustworthy clinical decision support

Speaker notes: Introduce the platform as a reproducible, agentic research system rather than a chatbot.

---

# 2. Motivation

- Complex decisions need planning, evidence, critique, synthesis, and transparent uncertainty.
- Clinical decision support is a high-stakes use case where hallucinations matter.
- A single model response does not provide enough auditability for academic or clinical-adjacent work.

Speaker notes: Emphasize why multi-step, evidence-grounded workflows are needed.

---

# 3. Problem Statement

Build a system that turns a broad research topic into a professional report and presentation while preserving evidence traceability, uncertainty, and reproducibility.

Speaker notes: The problem is both engineering and research quality control.

---

# 4. Proposed System

Ten specialized agents coordinate through typed workflow state, conditional graph edges, local memory, and deterministic mock evidence.

Speaker notes: Explain structured state as the backbone.

---

# 5. Multi-Agent Architecture

Streamlit and FastAPI feed a LangGraph-style workflow. Agents call retrieval, citation, visualization, report, presentation, and memory tools.

Speaker notes: The architecture separates interface, orchestration, agents, tools, and persistence.

---

# 6. LangGraph Workflow

Planner -> Research -> Analyst -> Critic -> Fact-Check -> Visualization -> Report -> Evaluation -> Presentation -> Memory.

Speaker notes: The critic can return to research; the evaluator can return to report writing.

---

# 7. Agent Roles

Planner decomposes, Research retrieves, Analyst structures, Critic challenges, Fact-Checker grounds, Visualization explains, Writer synthesizes, Evaluator scores, Presentation communicates, Memory persists.

Speaker notes: This division of labor is what makes the workflow inspectable.

---

# 8. Implementation Stack

Python, LangGraph-compatible orchestration, FastAPI, Streamlit, SQLite, Pydantic-compatible schemas, Matplotlib, LaTeX, Pytest, Docker.

Speaker notes: Mock mode and compatibility shims make the project runnable without paid API keys.

---

# 9. Report Generation Pipeline

Sources -> claims -> checks -> tables -> figures -> Markdown -> LaTeX -> PDF -> slides.

Speaker notes: The LaTeX report is the primary final deliverable.

---

# 10. Evaluation Methodology

Rubric dimensions: factuality, relevance, completeness, structure, citation quality, clarity, visual quality, and reproducibility.

Speaker notes: The score measures project artifact quality, not clinical validity.

---

# 11. Results

Final quality score: **93.1/100**.

The final mock run retrieves the local evidence corpus, generates figures, compiles a LaTeX PDF, creates a presentation, and saves evaluation files.

Speaker notes: Emphasize generated artifacts and reproducibility.

---

# 12. Limitations and Risks

Static mock corpus, shallow claim verification, no clinical validation, no PHI workflow.

Speaker notes: Make clear this is a research prototype, not a medical device.

---

# 13. Future Work

Live retrieval, vector stores, stronger natural-language inference fact checking, human review checkpoints, security hardening, and formal clinical evaluation.

Speaker notes: Connect future work to production readiness.

---

# 14. Conclusion

The platform demonstrates a complete, inspectable, multi-agent workflow for evidence-grounded research and decision intelligence.

Speaker notes: Close with reproducibility and educational value.
