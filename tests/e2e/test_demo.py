from pathlib import Path

from app.graph.workflow import run_workflow


def test_demo_generates_report_figures_and_presentation():
    state = run_workflow("Multi-agent AI systems for trustworthy clinical decision support", use_mock_llm=True)
    assert Path(state.report_path).exists()
    assert Path(state.presentation_path).exists()
    assert state.evaluation.total > 80

