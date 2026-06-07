from pathlib import Path

from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.presentation_agent import PresentationAgent
from app.models.schemas import WorkflowState


def test_presentation_agent_generates_markdown_and_pptx():
    state = WorkflowState(query="multi-agent clinical AI", use_mock_llm=True)
    state.evaluation.total = 90
    state = EvaluatorAgent().run(state)
    state = PresentationAgent().run(state)

    presentation_path = Path(state.presentation_path)
    assert presentation_path.exists()
    assert Path("presentation/final_presentation.md").exists()
    assert presentation_path.suffix in {".pptx", ".md"}

