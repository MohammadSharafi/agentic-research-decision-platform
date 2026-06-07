from app.agents.fact_checker_agent import FactCheckingAgent
from app.agents.research_agent import ResearchAgent
from app.models.schemas import WorkflowState


def test_fact_checker_marks_supported_claims():
    state = ResearchAgent().run(WorkflowState(query="clinical RAG agentic evaluation ethics"))
    state = FactCheckingAgent().run(state)
    assert len(state.claim_checks) >= 5
    assert sum(check.supported for check in state.claim_checks) >= 4

