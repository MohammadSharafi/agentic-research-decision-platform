from __future__ import annotations

from collections import Counter

from app.models.schemas import AnalysisTable, WorkflowState


class DataAnalystAgent:
    name = "analyst_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        tag_counts = Counter(tag for source in state.sources for tag in source.tags)
        evidence_quality = round(sum(source.credibility for source in state.sources) / max(len(state.sources), 1), 3)
        citation_coverage = min(1.0, len(state.sources) / 12)
        confidence = round(((0.45 * evidence_quality) + (0.35 * citation_coverage) + (0.20 * min(1.0, len(tag_counts) / 8))) * 100, 1)
        hallucination_controls = ["retrieval grounding", "fact checking", "critic loop", "citation gating", "human review"]

        state.analysis = {
            "evidence_quality": evidence_quality,
            "citation_coverage": round(citation_coverage, 3),
            "confidence_score": confidence,
            "source_count": len(state.sources),
            "tag_counts": dict(tag_counts),
            "hallucination_controls": hallucination_controls,
            "formulas": [
                r"T = \{t_1, t_2, ..., t_n\}",
                r"C = \frac{\sum_{i=1}^{n} w_i s_i}{\sum_{i=1}^{n} w_i}",
                r"Q = \alpha F + \beta R + \gamma S + \delta C",
            ],
        }

        state.tables = [
            AnalysisTable(
                title="Agent Roles",
                columns=["Agent", "Responsibility", "Input", "Output"],
                rows=[
                    ["Planner", "Task decomposition and routing", "User query", "Execution plan (PlanStep list)"],
                    ["Research", "Evidence retrieval", "Query and plan", "Ranked Source objects"],
                    ["Analyst", "Metrics, comparisons, formulas", "Retrieved sources", "Analysis tables and metrics"],
                    ["Critic", "Weakness and risk review", "Analysis and sources", "needs_revision flag and critique"],
                    ["Fact-Checker", "Claim grounding", "Approved analysis", "ClaimCheck objects with citations"],
                    ["Visualization", "Figures and diagrams", "Workflow state snapshot", "PNG, SVG, and Mermaid assets"],
                    ["Report Writer", "Academic synthesis", "Full workflow state", "Markdown, LaTeX, and PDF reports"],
                    ["Evaluator", "Rubric scoring", "Report and figures", "EvaluationScore JSON/Markdown"],
                    ["Presentation", "Stakeholder communication", "Evaluated state", "Markdown and PPTX slides"],
                    ["Memory", "Persistence", "Completed workflow state", "SQLite run record"],
                ],
            ),
            AnalysisTable(
                title="Framework Comparison",
                columns=["Framework", "Strengths", "Limitations", "Suitability for This Project"],
                rows=[
                    ["LangGraph", "Typed graph orchestration with conditional edges", "Requires explicit state design", "Best fit: mirrors critique and evaluation loops"],
                    ["Google ADK", "Code-first agent toolkit with Google ecosystem deployment", "Younger ecosystem and vendor coupling", "Useful for Gemini/Vertex deployments, not required here"],
                    ["AutoGen", "Conversational multi-agent patterns", "Can become chat-loop centric", "Good for research prototypes; less explicit graph control"],
                    ["CrewAI", "Role/task abstraction is easy to teach", "Less explicit low-level routing", "Suitable for sequential crews, not revision gates"],
                    ["Semantic Kernel", "Enterprise-friendly plugins and planners", "Broad SDK surface area", "Strong for Microsoft stacks; heavier than needed"],
                ],
            ),
            AnalysisTable(
                title="API Endpoints",
                columns=["Endpoint", "Method", "Purpose"],
                rows=[
                    ["/health", "GET", "Service readiness check"],
                    ["/run", "POST", "Execute the full agentic workflow"],
                    ["/runs/{run_id}", "GET", "Retrieve stored run metadata and serialized state"],
                    ["/runs/{run_id}/report", "GET", "Download the generated Markdown report"],
                    ["/runs/{run_id}/presentation", "GET", "Download the presentation artifact"],
                    ["/runs/{run_id}/figures", "GET", "List paths to generated figure files"],
                ],
            ),
            AnalysisTable(
                title="Evaluation Rubric",
                columns=["Criterion", "Description", "Weight"],
                rows=[
                    ["Factuality", "Share of claims supported by retrieved sources", "15%"],
                    ["Relevance", "Alignment between query, plan, and final report", "12%"],
                    ["Completeness", "Presence of required sections, tables, figures, and formulas", "12%"],
                    ["Structure", "Logical organization and academic readability", "10%"],
                    ["Citation quality", "Traceable references and citation markers", "15%"],
                    ["Clarity", "Plain-language explanations of technical decisions", "10%"],
                    ["Visual quality", "Architecture diagrams, charts, and labeled figures", "13%"],
                    ["Reproducibility", "Mock mode, tests, scripts, Docker, and saved artifacts", "13%"],
                ],
            ),
            AnalysisTable(
                title="Limitations and Mitigations",
                columns=["Limitation", "Impact", "Mitigation"],
                rows=[
                    ["Static mock corpus", "Evidence may be stale or incomplete", "Deterministic grading; optional live search adapters"],
                    ["Real LLM dependency in production", "Non-deterministic outputs without keys", "USE_MOCK_LLM=true default; provider adapters behind tools"],
                    ["Citation verification limits", "Tag-level checks miss entailment errors", "Fact-checker gates claims; human review required"],
                    ["Clinical prototype scope", "Not validated for patient-specific decisions", "Explicit limitations, ethics section, no diagnosis claims"],
                    ["Human review requirement", "Automation bias if outputs are trusted blindly", "Critic mandates limitations; evaluator threshold gate"],
                ],
            ),
            AnalysisTable(
                title="Final Evaluation Scores",
                columns=["Dimension", "Score"],
                rows=[
                    ["Factuality", "pending"],
                    ["Relevance", "pending"],
                    ["Completeness", "pending"],
                    ["Structure", "pending"],
                    ["Citation quality", "pending"],
                    ["Clarity", "pending"],
                    ["Visual quality", "pending"],
                    ["Reproducibility", "pending"],
                    ["Total", "pending"],
                ],
            ),
        ]
        state.status = "analyzed"
        state.add_note(self.name, f"Computed confidence score {confidence}/100 from evidence quality, coverage, and diversity.")
        return state

