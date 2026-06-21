from __future__ import annotations

from pathlib import Path

from app.config.settings import PROJECT_DIR, get_settings
from app.models.schemas import GeneratedFigure, WorkflowState
from app.tools.file_tools import copy_file, ensure_dir
from app.tools.visualization_tools import save_bar_chart, save_box_diagram, save_conceptual_pipeline, save_mermaid, save_radar_chart


class VisualizationAgent:
    name = "visualization_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        settings = get_settings()
        figure_dir = ensure_dir(settings.output_dir / "figures" / state.run_id)
        asset_dir = ensure_dir(PROJECT_DIR / "report" / "assets")
        if not state.use_mock_llm:
            return self._run_dynamic(state, figure_dir, asset_dir)
        figures: list[GeneratedFigure] = []

        diagrams = [
            (
                "system_architecture",
                "Overall System Architecture",
                """
                flowchart LR
                  UI[Streamlit UI] --> API[FastAPI Backend]
                  API --> Graph[LangGraph Workflow]
                  Graph --> Agents[Specialized Agent Layer]
                  Agents --> Tools[Search, Citation, Report, Visualization Tools]
                  Agents --> Memory[(SQLite Memory)]
                  Tools --> Data[(Mock Sources / Optional Web APIs)]
                  Graph --> Outputs[Reports, Figures, Presentations, Evaluation]
                """,
            ),
            (
                "workflow",
                "LangGraph Multi-Agent Workflow",
                """
                flowchart TD
                  Q[User Query] --> P[Planner]
                  P --> R[Research]
                  R --> A[Data Analyst]
                  A --> C[Critic]
                  C -->|insufficient evidence| R
                  C -->|acceptable| F[Fact Checker]
                  F --> V[Visualization]
                  V --> W[Report Writer]
                  W --> E[Evaluator]
                  E -->|score below threshold| W
                  E -->|score acceptable| S[Presentation]
                  S --> O[Final Outputs]
                """,
            ),
            (
                "agent_communication",
                "Agent Communication Protocol",
                """
                sequenceDiagram
                  participant Planner
                  participant Research
                  participant Analyst
                  participant Critic
                  participant FactChecker
                  participant Writer
                  Planner->>Research: PlanStep list + query
                  Research->>Analyst: Source objects
                  Analyst->>Critic: Metrics, tables, formulas
                  Critic-->>Research: Revision request if evidence is weak
                  Critic->>FactChecker: Approved analysis
                  FactChecker->>Writer: ClaimCheck objects + citation markers
                  Writer->>Planner: Final report paths
                """,
            ),
            (
                "report_pipeline",
                "Report Generation Pipeline",
                """
                flowchart LR
                  Sources --> Claims
                  Claims --> Checks[Claim Checks]
                  Checks --> Tables
                  Tables --> Figures
                  Figures --> Markdown
                  Markdown --> PDF
                  Markdown --> Slides
                """,
            ),
            (
                "evaluation_pipeline",
                "Evaluation Pipeline",
                """
                flowchart LR
                  Report --> Rubric
                  Figures --> Rubric
                  Citations --> Rubric
                  Rubric --> JSON
                  Rubric --> Markdown
                  JSON --> Threshold{Pass?}
                  Threshold -->|No| Revision
                  Threshold -->|Yes| Presentation
                """,
            ),
        ]
        for figure_id, title, code in diagrams:
            path = save_mermaid(figure_dir / f"{figure_id}.md", title, code)
            copy_file(path, asset_dir / path.name)
            figures.append(GeneratedFigure(id=figure_id, title=title, path=str(path), figure_type="mermaid", description=title))

        image_diagrams = [
            (
                "overall_system_architecture",
                "Overall System Architecture",
                [
                    ("ui", "Streamlit UI", 0.12, 0.70),
                    ("api", "FastAPI", 0.30, 0.70),
                    ("graph", "LangGraph", 0.50, 0.70),
                    ("agents", "Agent Layer", 0.70, 0.70),
                    ("tools", "Tool Layer", 0.88, 0.70),
                    ("memory", "SQLite Memory", 0.50, 0.35),
                    ("outputs", "Reports & Slides", 0.75, 0.35),
                ],
                [
                    ("ui", "api", ""),
                    ("api", "graph", ""),
                    ("graph", "agents", ""),
                    ("agents", "tools", ""),
                    ("graph", "memory", "state"),
                    ("agents", "outputs", "artifacts"),
                ],
            ),
            (
                "multi_agent_workflow_diagram",
                "Conditional Multi-Agent Workflow",
                [
                    ("plan", "Planner", 0.10, 0.72),
                    ("research", "Research", 0.25, 0.72),
                    ("analysis", "Analyst", 0.40, 0.72),
                    ("critic", "Critic", 0.55, 0.72),
                    ("fact", "Fact Check", 0.70, 0.72),
                    ("viz", "Visualize", 0.85, 0.72),
                    ("report", "Report", 0.35, 0.35),
                    ("eval", "Evaluator", 0.55, 0.35),
                    ("slides", "Presentation", 0.75, 0.35),
                    ("memory", "Memory", 0.90, 0.35),
                ],
                [
                    ("plan", "research", ""),
                    ("research", "analysis", ""),
                    ("analysis", "critic", ""),
                    ("critic", "research", "revise"),
                    ("critic", "fact", "accept"),
                    ("fact", "viz", ""),
                    ("viz", "report", ""),
                    ("report", "eval", ""),
                    ("eval", "report", "low score"),
                    ("eval", "slides", "pass"),
                    ("slides", "memory", ""),
                ],
            ),
            (
                "langgraph_state_transition_diagram",
                "LangGraph State Transition Diagram",
                [
                    ("init", "initialized", 0.12, 0.72),
                    ("planned", "planned", 0.28, 0.72),
                    ("researched", "researched", 0.44, 0.72),
                    ("analyzed", "analyzed", 0.60, 0.72),
                    ("critiqued", "critiqued", 0.76, 0.72),
                    ("checked", "fact_checked", 0.28, 0.35),
                    ("visualized", "visualized", 0.44, 0.35),
                    ("reported", "reported", 0.60, 0.35),
                    ("done", "completed", 0.78, 0.35),
                ],
                [
                    ("init", "planned", ""),
                    ("planned", "researched", ""),
                    ("researched", "analyzed", ""),
                    ("analyzed", "critiqued", ""),
                    ("critiqued", "researched", "needs_revision"),
                    ("critiqued", "checked", "acceptable"),
                    ("checked", "visualized", ""),
                    ("visualized", "reported", ""),
                    ("reported", "done", "score pass"),
                ],
            ),
            (
                "agent_communication_diagram",
                "Agent Communication Diagram",
                [
                    ("state", "WorkflowState", 0.50, 0.50),
                    ("planner", "Planner", 0.20, 0.78),
                    ("research", "Research", 0.50, 0.82),
                    ("analyst", "Analyst", 0.80, 0.78),
                    ("critic", "Critic", 0.20, 0.25),
                    ("fact", "Fact Checker", 0.50, 0.18),
                    ("writer", "Writer", 0.80, 0.25),
                ],
                [
                    ("planner", "state", "plan"),
                    ("research", "state", "sources"),
                    ("analyst", "state", "tables"),
                    ("critic", "state", "critique"),
                    ("fact", "state", "checks"),
                    ("writer", "state", "report"),
                ],
            ),
            (
                "report_generation_pipeline_diagram",
                "Report Generation Pipeline",
                [
                    ("sources", "Sources", 0.12, 0.60),
                    ("claims", "Claims", 0.28, 0.60),
                    ("checks", "Checks", 0.44, 0.60),
                    ("tables", "Tables", 0.60, 0.60),
                    ("figures", "Figures", 0.76, 0.60),
                    ("latex", "LaTeX/PDF", 0.92, 0.60),
                ],
                [("sources", "claims", ""), ("claims", "checks", ""), ("checks", "tables", ""), ("tables", "figures", ""), ("figures", "latex", "")],
            ),
            (
                "evaluation_pipeline_diagram",
                "Evaluation Pipeline",
                [
                    ("report", "Report", 0.15, 0.65),
                    ("rubric", "Rubric", 0.38, 0.65),
                    ("score", "Score", 0.60, 0.65),
                    ("threshold", "Threshold", 0.80, 0.65),
                    ("revise", "Revise", 0.48, 0.30),
                    ("release", "Release", 0.90, 0.30),
                ],
                [
                    ("report", "rubric", ""),
                    ("rubric", "score", ""),
                    ("score", "threshold", ""),
                    ("threshold", "revise", "fail"),
                    ("threshold", "release", "pass"),
                    ("revise", "report", ""),
                ],
            ),
        ]
        for figure_id, title, nodes, edges in image_diagrams:
            path = save_box_diagram(figure_dir / f"{figure_id}.png", title, nodes, edges)
            copy_file(path, asset_dir / path.name)
            figures.append(
                GeneratedFigure(
                    id=figure_id,
                    title=title,
                    path=str(path),
                    figure_type="diagram",
                    description=f"Publication-ready diagram: {title}.",
                )
            )

        tag_counts = state.analysis.get("tag_counts", {})
        labels = list(tag_counts.keys())[:8] or ["rag", "clinical", "agentic"]
        values = [float(tag_counts[label]) for label in labels]
        chart1 = save_bar_chart(figure_dir / "evidence_by_theme.png", "Evidence Sources by Theme", labels, values, "Sources")
        copy_file(chart1, asset_dir / chart1.name)
        figures.append(GeneratedFigure(id="evidence_by_theme", title="Evidence Sources by Theme", path=str(chart1), figure_type="chart", description="Theme distribution in the mock evidence base."))

        radar_labels = ["Fact", "Rel", "Comp", "Struct", "Cite", "Clear"]
        radar_values = [86, 90, 88, 87, 84, 89]
        chart2 = save_radar_chart(figure_dir / "quality_radar.png", radar_labels, radar_values, "Prototype Quality Profile")
        copy_file(chart2, asset_dir / chart2.name)
        figures.append(GeneratedFigure(id="quality_radar", title="Prototype Quality Profile", path=str(chart2), figure_type="chart", description="Radar chart for evaluation dimensions."))

        conceptual = save_conceptual_pipeline(figure_dir / "conceptual_grounding_pipeline.png")
        copy_file(conceptual, asset_dir / conceptual.name)
        figures.append(GeneratedFigure(id="conceptual_grounding_pipeline", title="Conceptual Grounding Pipeline", path=str(conceptual), figure_type="conceptual", description="Conceptual figure showing evidence-grounded synthesis."))

        state.figures = figures
        state.status = "visualized"
        state.add_note(self.name, f"Generated {len(figures)} figures and copied them to report/assets.")
        return state

    def _run_dynamic(self, state: WorkflowState, figure_dir: Path, asset_dir: Path) -> WorkflowState:
        figures: list[GeneratedFigure] = []
        tag_counts = state.analysis.get("tag_counts", {})
        labels = list(tag_counts.keys())[:8] or ["sources"]
        values = [float(tag_counts.get(label, 0)) for label in labels] or [len(state.sources)]
        evidence = save_bar_chart(figure_dir / "evidence_by_theme.png", "Evidence Themes for Research Query", labels, values, "Sources")
        copy_file(evidence, asset_dir / evidence.name)
        figures.append(
            GeneratedFigure(
                id="evidence_by_theme",
                title="Evidence Themes for Research Query",
                path=str(evidence),
                figure_type="chart",
                description="Topic-specific distribution of retrieved evidence themes.",
            )
        )

        type_counts: dict[str, int] = {}
        for source in state.sources:
            type_counts[source.source_type] = type_counts.get(source.source_type, 0) + 1
        type_labels = list(type_counts.keys()) or ["sources"]
        type_values = [float(type_counts[label]) for label in type_labels] or [0.0]
        type_chart = save_bar_chart(figure_dir / "source_types.png", "Retrieved Source Types", type_labels, type_values, "Sources")
        copy_file(type_chart, asset_dir / type_chart.name)
        figures.append(
            GeneratedFigure(
                id="source_types",
                title="Retrieved Source Types",
                path=str(type_chart),
                figure_type="chart",
                description="Types of sources used in the dynamic research report.",
            )
        )

        supported = sum(1 for check in state.claim_checks if check.supported)
        unsupported = max(len(state.claim_checks) - supported, 0)
        claim_chart = save_bar_chart(
            figure_dir / "claim_support.png",
            "Claim Support Summary",
            ["Supported", "Unsupported"],
            [float(supported), float(unsupported)],
            "Claims",
        )
        copy_file(claim_chart, asset_dir / claim_chart.name)
        figures.append(
            GeneratedFigure(
                id="claim_support",
                title="Claim Support Summary",
                path=str(claim_chart),
                figure_type="chart",
                description="How many extracted claims were supported by retrieved sources.",
            )
        )

        state.figures = figures
        state.status = "visualized"
        state.add_note(self.name, f"Generated {len(figures)} topic-specific figures and copied them to report/assets.")
        return state
