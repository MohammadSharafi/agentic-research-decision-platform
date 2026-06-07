from app.graph.workflow import run_workflow


def test_mock_mode_retrieves_full_local_corpus():
    state = run_workflow("clinical decision support hallucination risk", use_mock_llm=True)
    assert state.use_mock_llm is True
    assert len(state.sources) >= 20
    assert all(source.url.startswith("http") for source in state.sources)

