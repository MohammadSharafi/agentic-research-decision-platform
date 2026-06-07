from app.agents.analyst_agent import DataAnalystAgent
from app.agents.research_agent import ResearchAgent
from app.models.schemas import WorkflowState


def test_analyst_produces_tables_and_metrics():
    state = ResearchAgent().run(WorkflowState(query="multi-agent clinical AI"))
    state = DataAnalystAgent().run(state)
    assert state.analysis["confidence_score"] > 50
    assert len(state.tables) >= 5

