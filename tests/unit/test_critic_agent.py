from app.agents.critic_agent import CriticAgent
from app.models.schemas import WorkflowState


def test_critic_requests_revision_for_thin_evidence():
    state = CriticAgent().run(WorkflowState(query="clinical AI"))
    assert state.needs_revision is True
    assert state.revision_count == 1

