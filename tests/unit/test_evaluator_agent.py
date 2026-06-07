from app.agents.analyst_agent import DataAnalystAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.fact_checker_agent import FactCheckingAgent
from app.agents.research_agent import ResearchAgent
from app.agents.visualization_agent import VisualizationAgent
from app.models.schemas import WorkflowState


def test_evaluator_scores_all_rubric_dimensions():
    state = WorkflowState(query="trustworthy clinical decision support", use_mock_llm=True)
    for agent in [ResearchAgent(), DataAnalystAgent(), FactCheckingAgent(), VisualizationAgent(), EvaluatorAgent()]:
        state = agent.run(state)

    assert state.evaluation.total >= 78
    assert state.evaluation.factuality > 0
    assert state.evaluation.reproducibility > 0

