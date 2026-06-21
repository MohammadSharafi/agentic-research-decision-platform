from __future__ import annotations

from app.models.schemas import PlanStep, WorkflowState
from app.tools.llm_tools import openai_chat_json


class PlannerAgent:
    name = "planner_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        if not state.use_mock_llm:
            dynamic_steps = self._real_mode_plan(state.query)
            if dynamic_steps:
                state.plan = dynamic_steps
                state.status = "planned"
                state.add_note(self.name, f"Created dynamic execution plan for: {state.query}")
                return state

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

    def _real_mode_plan(self, query: str) -> list[PlanStep]:
        payload = openai_chat_json(
            "You are a research workflow planner. Return only JSON.",
            (
                "Create a concise agent workflow plan for this research request. "
                "Return JSON with key 'steps', an array of 7-9 objects. Each object must have "
                "'id', 'description', and 'agent'. Use agents from: Planner Agent, Research Agent, "
                "Data Analyst Agent, Critic Agent, Fact-Checking Agent, Visualization Agent, "
                "Report Writer Agent, Evaluator Agent, Presentation Agent.\n\n"
                f"Research request: {query}"
            ),
            max_tokens=1200,
        )
        raw_steps = payload.get("steps", []) if payload else []
        steps: list[PlanStep] = []
        for idx, item in enumerate(raw_steps):
            if not isinstance(item, dict):
                continue
            step_id = str(item.get("id") or f"step_{idx + 1}").lower().replace(" ", "_")
            description = str(item.get("description") or "").strip()
            agent = str(item.get("agent") or "Research Agent").strip()
            if not description:
                continue
            steps.append(
                PlanStep(
                    id=step_id,
                    description=description,
                    agent=agent,
                    depends_on=[] if idx == 0 else [steps[-1].id] if steps else [],
                )
            )
        if len(steps) >= 5:
            return steps

        fallback = [
            ("scope", f"Define the research scope and comparison dimensions for: {query}", "Planner Agent"),
            ("research", "Retrieve current authoritative web sources and institutional references.", "Research Agent"),
            ("analysis", "Extract evidence-backed findings, comparisons, risks, and data gaps.", "Data Analyst Agent"),
            ("critique", "Identify weak evidence, unsupported claims, and missing perspectives.", "Critic Agent"),
            ("fact_check", "Verify major claims against retrieved sources.", "Fact-Checking Agent"),
            ("visualize", "Generate charts that summarize evidence themes and quality.", "Visualization Agent"),
            ("report", "Write a topic-specific research paper with citations and tables.", "Report Writer Agent"),
            ("evaluate", "Score the artifact based on relevance, evidence, citations, and completeness.", "Evaluator Agent"),
        ]
        return [
            PlanStep(id=step_id, description=description, agent=agent, depends_on=[] if idx == 0 else [fallback[idx - 1][0]])
            for idx, (step_id, description, agent) in enumerate(fallback)
        ]
