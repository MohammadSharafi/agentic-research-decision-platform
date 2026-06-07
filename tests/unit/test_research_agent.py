from app.agents.research_agent import ResearchAgent
from app.models.schemas import WorkflowState


def test_research_agent_uses_mock_data():
    state = ResearchAgent().run(WorkflowState(query="trustworthy clinical decision support", use_mock_llm=True))
    assert len(state.sources) >= 8
    assert any("clinical" in source.tags for source in state.sources)

