---
title: Agentic Research & Decision Intelligence Platform
subtitle: Final Course Project
---

# 1. Title

Agentic Research & Decision Intelligence Platform
Topic: multi-agent clinical AI

Speaker notes: See final report for full technical detail.

---

# 2. Motivation

Complex decisions require planning, evidence, critique, synthesis, and transparent uncertainty—especially in clinical-adjacent settings.

Speaker notes: See final report for full technical detail.

---

# 3. Problem Statement

Transform a broad research topic into a professional evidence-grounded report and presentation with traceability and reproducibility.

Speaker notes: See final report for full technical detail.

---

# 4. Proposed System

Ten specialized agents coordinate through typed WorkflowState, conditional graph edges, SQLite memory, and deterministic mock evidence.

Speaker notes: See final report for full technical detail.

---

# 5. Multi-Agent Architecture

Streamlit UI and FastAPI backend feed a LangGraph-style workflow. Agents call search, citation, visualization, report, presentation, and memory tools.

Speaker notes: See final report for full technical detail.

---

# 6. LangGraph Workflow

Planner → Research → Analyst → Critic → Fact-Check → Visualization → Report → Evaluator → Presentation → Memory.

Speaker notes: See final report for full technical detail.

---

# 7. Conditional Routing

Critic loops back to Research when evidence is weak. Evaluator loops back to Report Writer when quality score Q is below threshold τ = 78.

Speaker notes: See final report for full technical detail.

---

# 8. Agent Roles

Planner decomposes; Research retrieves; Analyst structures; Critic challenges; Fact-Checker grounds; Visualization explains; Writer synthesizes; Evaluator scores.

Speaker notes: See final report for full technical detail.

---

# 9. Implementation Stack

Python, LangGraph-compatible orchestration, FastAPI, Streamlit, SQLite, Matplotlib, LaTeX, Pytest, Docker.

Speaker notes: See final report for full technical detail.

---

# 10. Mock Mode Design

USE_MOCK_LLM=true runs without paid API keys. A local corpus of 21 verified references keeps outputs deterministic for grading.

Speaker notes: See final report for full technical detail.

---

# 11. Report Generation Pipeline

Sources → claim checks → tables → figures → Markdown → LaTeX → PDF → presentation artifacts.

Speaker notes: See final report for full technical detail.

---

# 12. Mathematical Formulation

Task decomposition T = {t₁,…,tₙ}; confidence C = Σwᵢsᵢ/Σwᵢ; quality Q = αF+βR+γS+δC_q; revision when Q < τ.

Speaker notes: See final report for full technical detail.

---

# 13. API Endpoints

GET /health; POST /run; GET /runs/{run_id}; GET /runs/{run_id}/report; GET /runs/{run_id}/presentation; GET /runs/{run_id}/figures.

Speaker notes: See final report for full technical detail.

---

# 14. Evaluation Methodology

Rubric: factuality, relevance, completeness, structure, citation quality, clarity, visual quality, reproducibility (artifact quality, not clinical validity).

Speaker notes: See final report for full technical detail.

---

# 15. Results

Final score: 79.6/100. Confidence: 0/100. Sources: 0. Figures: 0. LaTeX PDF and PPTX generated.

Speaker notes: See final report for full technical detail.

---

# 16. Testing and Reproducibility

pytest -v; python scripts/run_demo.py; python scripts/build_report_pdf.py; Docker Compose for containerized runs.

Speaker notes: See final report for full technical detail.

---

# 17. Limitations

Static mock corpus; metadata-level fact checking; no clinical validation; human review required; not a medical device.

Speaker notes: See final report for full technical detail.

---

# 18. AI Usage and Development Transparency

External AI tools (ChatGPT, Codex-style assistant, Cursor AI, NotebookLM) supported planning, implementation, documentation, and presentation drafting. The implemented system itself contains separate internal runtime agents. The student defined requirements, supervised development, reviewed outputs, tested the system, and prepared final submission. Mock mode and tests support reproducibility.

Speaker notes: See final report for full technical detail.

---

# 19. Future Work

Live retrieval, vector stores, entailment-based fact checking, human-in-the-loop approval, security hardening, formal clinical evaluation.

Speaker notes: See final report for full technical detail.

---

# 20. Conclusion

A reproducible multi-agent prototype that produces inspectable, evidence-grounded academic deliverables suitable for university evaluation.

Speaker notes: See final report for full technical detail.

---
