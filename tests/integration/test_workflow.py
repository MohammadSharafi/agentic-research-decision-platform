from pathlib import Path

from app.graph.workflow import run_workflow


def test_workflow_runs_end_to_end():
    state = run_workflow("Multi-agent AI systems for trustworthy clinical decision support", use_mock_llm=True)
    assert state.status == "completed"
    assert state.evaluation.total >= 78
    assert Path(state.report_path).exists()
    assert len(state.figures) >= 7

