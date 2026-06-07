from __future__ import annotations

import logging
from typing import Callable

from app.config.settings import get_settings
from app.graph.nodes import (
    analyst_node,
    critic_node,
    evaluator_node,
    fact_checker_node,
    finalize_report_node,
    memory_node,
    planner_node,
    presentation_node,
    report_writer_node,
    research_node,
    route_after_critic,
    route_after_evaluator,
    visualization_node,
)
from app.models.schemas import WorkflowState


LOGGER = logging.getLogger(__name__)


class AgenticWorkflow:
    """LangGraph-first workflow with a deterministic fallback runner."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._compiled = self._try_compile_langgraph()

    def run(self, query: str, use_mock_llm: bool = True) -> WorkflowState:
        state = WorkflowState(query=query, use_mock_llm=use_mock_llm)
        if self._compiled is not None:
            try:
                result = self._compiled.invoke(state)
                if isinstance(result, WorkflowState):
                    return result
                if isinstance(result, dict):
                    return WorkflowState(**result)
                raise TypeError(f"Unexpected LangGraph result type: {type(result)!r}")
            except Exception as exc:  # pragma: no cover - defensive production fallback
                LOGGER.warning("LangGraph execution failed; using fallback runner: %s", exc)
        return self._run_fallback(state)

    def _run_fallback(self, state: WorkflowState) -> WorkflowState:
        state = planner_node(state)
        state = research_node(state)
        state = analyst_node(state)
        state = critic_node(state)
        while route_after_critic(state) == "research":
            state = research_node(state)
            state = analyst_node(state)
            state = critic_node(state)
        state = fact_checker_node(state)
        state = visualization_node(state)
        state = report_writer_node(state)
        state = evaluator_node(state)
        while route_after_evaluator(state) == "report":
            state = report_writer_node(state)
            state = evaluator_node(state)
        state = finalize_report_node(state)
        state = presentation_node(state)
        state = memory_node(state)
        return state

    def _try_compile_langgraph(self) -> object | None:
        try:
            from langgraph.graph import END, StateGraph
        except Exception:
            return None

        graph = StateGraph(WorkflowState)
        graph.add_node("planner", planner_node)
        graph.add_node("research", research_node)
        graph.add_node("analysis", analyst_node)
        graph.add_node("critic", critic_node)
        graph.add_node("fact_check", fact_checker_node)
        graph.add_node("visualization", visualization_node)
        graph.add_node("report", report_writer_node)
        graph.add_node("evaluation", evaluator_node)
        graph.add_node("finalize_report", finalize_report_node)
        graph.add_node("presentation", presentation_node)
        graph.add_node("memory", memory_node)
        graph.set_entry_point("planner")
        graph.add_edge("planner", "research")
        graph.add_edge("research", "analysis")
        graph.add_edge("analysis", "critic")
        graph.add_conditional_edges("critic", route_after_critic, {"research": "research", "fact_check": "fact_check"})
        graph.add_edge("fact_check", "visualization")
        graph.add_edge("visualization", "report")
        graph.add_edge("report", "evaluation")
        graph.add_conditional_edges(
            "evaluation",
            route_after_evaluator,
            {"report": "report", "finalize_report": "finalize_report"},
        )
        graph.add_edge("finalize_report", "presentation")
        graph.add_edge("presentation", "memory")
        graph.add_edge("memory", END)
        return graph.compile()


def run_workflow(query: str, use_mock_llm: bool = True) -> WorkflowState:
    return AgenticWorkflow().run(query=query, use_mock_llm=use_mock_llm)
