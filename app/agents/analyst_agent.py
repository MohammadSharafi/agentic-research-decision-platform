from __future__ import annotations

from collections import Counter
import re

from app.models.schemas import AnalysisTable, WorkflowState
from app.tools.llm_tools import openai_chat_json


class DataAnalystAgent:
    name = "analyst_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        if not state.use_mock_llm:
            return self._run_dynamic(state)

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
                    ["/runs/{run_id}/report.pdf", "GET", "Download the generated PDF report"],
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

    def _run_dynamic(self, state: WorkflowState) -> WorkflowState:
        tag_counts = Counter(tag for source in state.sources for tag in source.tags)
        evidence_quality = round(sum(source.credibility for source in state.sources) / max(len(state.sources), 1), 3)
        citation_coverage = min(1.0, len(state.sources) / 10)
        tag_diversity = min(1.0, len(tag_counts) / 8)
        confidence = round(((0.42 * evidence_quality) + (0.36 * citation_coverage) + (0.22 * tag_diversity)) * 100, 1)

        source_brief = "\n".join(
            f"- {idx}. {source.title} ({source.authors}, {source.year or 'n.d.'}): {source.summary[:420]}"
            for idx, source in enumerate(state.sources[:12], start=1)
        )
        payload = openai_chat_json(
            "You are a careful research analyst. Return only JSON.",
            (
                "Analyze the user research request using only the source summaries below. "
                "Return JSON with keys: executive_summary (string), key_findings (array of strings), "
                "main_claims (array of 5-8 evidence-checkable claims), and tables (array). "
                "Each table must have title, columns, rows. Prefer comparison tables when the prompt compares entities. "
                "Do not invent precise statistics unless they appear in the source summaries.\n\n"
                f"User request: {state.query}\n\nSources:\n{source_brief}"
            ),
            max_tokens=2800,
        )

        tables = self._tables_from_payload(payload)
        key_findings = self._string_list(payload.get("key_findings") if payload else None)
        main_claims = self._string_list(payload.get("main_claims") if payload else None)
        executive_summary = str(payload.get("executive_summary", "")).strip() if payload else ""

        if not tables:
            tables = self._fallback_tables(state)
        if not key_findings:
            key_findings = self._fallback_findings(state)
        if not main_claims:
            main_claims = key_findings[:5]
        if not executive_summary:
            executive_summary = (
                f"This report analyzes '{state.query}' using {len(state.sources)} retrieved sources. "
                "Findings are grounded in retrieved web or institutional evidence and are scored for traceability."
            )

        eval_placeholder = AnalysisTable(
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
        )
        state.tables = [*tables, eval_placeholder]
        state.analysis = {
            "report_mode": "research",
            "evidence_quality": evidence_quality,
            "citation_coverage": round(citation_coverage, 3),
            "confidence_score": confidence,
            "source_count": len(state.sources),
            "tag_counts": dict(tag_counts),
            "executive_summary": executive_summary,
            "key_findings": key_findings,
            "main_claims": main_claims,
            "formulas": [
                r"S(x,q)=\lambda_1 overlap+\lambda_2 credibility+\lambda_3 tag\_match",
                r"C = 100 \cdot \frac{\sum_i w_i s_i}{\sum_i w_i}",
                r"Q = \frac{F+R+M+S+K+L+V+P}{8}",
            ],
        }
        state.status = "analyzed"
        state.add_note(
            self.name,
            f"Built dynamic analysis for '{state.query}' with {len(tables)} tables and confidence {confidence}/100.",
            openai_used=bool(payload),
        )
        return state

    def _tables_from_payload(self, payload: dict | None) -> list[AnalysisTable]:
        tables: list[AnalysisTable] = []
        for item in (payload or {}).get("tables", []):
            if not isinstance(item, dict):
                continue
            columns = item.get("columns", [])
            rows = item.get("rows", [])
            title = str(item.get("title") or "Analysis Table").strip()
            if not isinstance(columns, list) or not isinstance(rows, list) or len(columns) < 2 or len(columns) > 5:
                continue
            cleaned_rows = [
                [self._clean_text(cell, 120) for cell in row]
                for row in rows
                if isinstance(row, list) and len(row) == len(columns)
            ]
            if cleaned_rows:
                tables.append(
                    AnalysisTable(
                        title=self._clean_text(title, 80),
                        columns=[self._clean_text(col, 45) for col in columns],
                        rows=cleaned_rows[:6],
                    )
                )
        return tables[:5]

    def _string_list(self, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()][:8]

    def _fallback_tables(self, state: WorkflowState) -> list[AnalysisTable]:
        source_rows = [
            [
                self._clean_text(source.title, 52),
                source.year or "n.d.",
                ", ".join(source.tags[:3]),
                self._clean_text(source.summary, 95),
            ]
            for source in state.sources[:6]
        ]
        theme_counts = Counter(tag for source in state.sources for tag in source.tags)
        theme_rows = [[theme, count, self._theme_interpretation(theme)] for theme, count in theme_counts.most_common(8)]
        if not theme_rows:
            theme_rows = [["general", len(state.sources), "General evidence coverage"]]
        return [
            AnalysisTable(
                title="Representative Evidence Sources Used for the Research Question",
                columns=["Source", "Year", "Themes", "Evidence signal"],
                rows=source_rows,
            ),
            AnalysisTable(
                title="Evidence Themes Identified from Retrieved Sources",
                columns=["Theme", "Sources", "Interpretation"],
                rows=theme_rows,
            ),
            AnalysisTable(
                title="Research Synthesis Matrix",
                columns=["Dimension", "What the sources indicate", "Confidence"],
                rows=[
                    ["Evidence base", f"{len(state.sources)} sources retrieved for the prompt.", "Medium" if len(state.sources) < 8 else "High"],
                    ["Source quality", f"Average credibility score is {round(sum(s.credibility for s in state.sources) / max(len(state.sources), 1), 2)}.", "Medium"],
                    ["Coverage", f"Top themes: {', '.join(tag for tag, _ in theme_counts.most_common(5)) or 'general'}.", "Medium"],
                ],
            ),
        ]

    def _fallback_findings(self, state: WorkflowState) -> list[str]:
        if not state.sources:
            return [f"The system could not retrieve enough evidence for '{state.query}'."]

        dimensions = {
            "economy": "Economic comparison",
            "health": "Healthcare comparison",
            "education": "Education comparison",
            "technology": "Technology and innovation comparison",
            "geopolitics": "Geopolitical risk comparison",
        }
        findings: list[str] = []
        for tag, label in dimensions.items():
            matching = [source for source in state.sources if tag in source.tags]
            if not matching:
                continue
            examples = "; ".join(self._clean_text(source.title, 70) for source in matching[:2])
            findings.append(
                f"{label}: {len(matching)} retrieved sources discuss this dimension. "
                f"Representative sources include {examples}. Treat precise statistics as source-dependent and verify them before decision use."
            )
        if findings:
            return findings[:6]
        examples = "; ".join(self._clean_text(source.title, 70) for source in state.sources[:3])
        return [
            f"The retrieved evidence base contains {len(state.sources)} sources for '{state.query}'. Representative sources include {examples}.",
            "The report should be interpreted as a sourced first draft rather than a final authoritative study.",
        ]

    def _theme_interpretation(self, theme: str) -> str:
        mapping = {
            "economy": "Economic indicators and macro conditions are central to this comparison.",
            "health": "Health-system evidence may support welfare and service-capacity comparisons.",
            "education": "Education evidence helps compare human capital and long-term capacity.",
            "technology": "Technology evidence informs innovation and digital readiness.",
            "geopolitics": "Geopolitical evidence is important for risk and policy interpretation.",
        }
        return mapping.get(theme, "Relevant source theme identified by retrieval.")

    def _clean_text(self, value: object, limit: int) -> str:
        text = str(value)
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"\[[^\]]+\]\([^)]+\)", "", text)
        text = text.replace("|", " ")
        text = " ".join(text.split())
        if len(text) <= limit:
            return text
        return text[: max(0, limit - 3)].rstrip() + "..."
