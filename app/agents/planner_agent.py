from __future__ import annotations

from app.models.schemas import PlanStep, WorkflowState


class PlannerAgent:
    name = "planner_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        focus = "clinical decision support" if "clinical" in state.query.lower() else "decision intelligence"
        steps = [
            ("plan", f"Decompose the {focus} request into evidence, analysis, risk, and deliverable workstreams.", "Planner Agent"),
            ("research", "Collect authoritative papers, framework documentation, and local evidence.", "Research Agent"),
            ("analysis", "Extract structured metrics, framework comparisons, and decision criteria.", "Data Analyst Agent"),
            ("critique", "Review evidence sufficiency, bias, uncertainty, and missing viewpoints.", "Critic Agent"),
            ("fact_check", "Ground major claims against sources and add citation markers.", "Fact-Checking Agent"),
            ("visualize", "Generate system diagrams, workflows, evaluation charts, and conceptual figures.", "Visualization Agent"),
            ("report", "Write an academic-style report with tables, formulas, figures, and references.", "Report Writer Agent"),
            ("evaluate", "Score quality with a reproducible rubric and save results.", "Evaluator Agent"),
            ("present", "Generate a final presentation for the course demo.", "Presentation Agent"),
        ]
        state.plan = [
            PlanStep(id=step_id, description=description, agent=agent, depends_on=[] if idx == 0 else [steps[idx - 1][0]])
            for idx, (step_id, description, agent) in enumerate(steps)
        ]
        state.status = "planned"
        state.add_note(self.name, f"Created {len(state.plan)}-step execution plan for: {state.query}")
        return state

