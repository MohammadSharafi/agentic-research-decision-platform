from __future__ import annotations

from app.agents.analyst_agent import DataAnalystAgent
from app.agents.critic_agent import CriticAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.fact_checker_agent import FactCheckingAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.presentation_agent import PresentationAgent
from app.agents.report_writer_agent import ReportWriterAgent
from app.agents.research_agent import ResearchAgent
from app.agents.visualization_agent import VisualizationAgent
from app.models.schemas import WorkflowState


planner = PlannerAgent()
researcher = ResearchAgent()
analyst = DataAnalystAgent()
critic = CriticAgent()
fact_checker = FactCheckingAgent()
visualizer = VisualizationAgent()
writer = ReportWriterAgent()
evaluator = EvaluatorAgent()
presenter = PresentationAgent()
memory = MemoryAgent()


def planner_node(state: WorkflowState) -> WorkflowState:
    return planner.run(state)


def research_node(state: WorkflowState) -> WorkflowState:
    return researcher.run(state)


def analyst_node(state: WorkflowState) -> WorkflowState:
    return analyst.run(state)


def critic_node(state: WorkflowState) -> WorkflowState:
    return critic.run(state)


def fact_checker_node(state: WorkflowState) -> WorkflowState:
    return fact_checker.run(state)


def visualization_node(state: WorkflowState) -> WorkflowState:
    return visualizer.run(state)


def report_writer_node(state: WorkflowState) -> WorkflowState:
    return writer.run(state)


def finalize_report_node(state: WorkflowState) -> WorkflowState:
    """Regenerate canonical report artifacts with final evaluation scores."""
    return writer.run(state)


def evaluator_node(state: WorkflowState) -> WorkflowState:
    return evaluator.run(state)


def presentation_node(state: WorkflowState) -> WorkflowState:
    return presenter.run(state)


def memory_node(state: WorkflowState) -> WorkflowState:
    return memory.run(state)


def route_after_critic(state: WorkflowState) -> str:
    if state.needs_revision and state.revision_count <= state.max_revisions:
        return "research"
    return "fact_check"


def route_after_evaluator(state: WorkflowState) -> str:
    if state.evaluation.total < 78 and state.revision_count < state.max_revisions:
        state.revision_count += 1
        return "report"
    return "finalize_report"

