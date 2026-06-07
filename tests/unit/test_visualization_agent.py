from pathlib import Path

from app.agents.analyst_agent import DataAnalystAgent
from app.agents.research_agent import ResearchAgent
from app.agents.visualization_agent import VisualizationAgent
from app.models.schemas import WorkflowState


def test_visualization_generates_required_figures():
    state = ResearchAgent().run(WorkflowState(query="clinical agentic AI"))
    state = DataAnalystAgent().run(state)
    state = VisualizationAgent().run(state)
    assert len(state.figures) >= 7
    assert all(Path(figure.path).exists() for figure in state.figures)

