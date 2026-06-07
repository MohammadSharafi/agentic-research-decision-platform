from app.agents.planner_agent import PlannerAgent
from app.models.schemas import WorkflowState


def test_planner_creates_multi_agent_plan():
    state = PlannerAgent().run(WorkflowState(query="clinical AI decision support"))
    assert len(state.plan) >= 8
    assert state.plan[0].agent == "Planner Agent"
    assert any("Fact" in step.agent for step in state.plan)

