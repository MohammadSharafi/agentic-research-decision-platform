from app.agents.memory_agent import MemoryAgent
from app.models.schemas import WorkflowState
from app.storage.memory import MemoryStore


def test_memory_agent_persists_run(tmp_path):
    store = MemoryStore(tmp_path / "memory.db")
    agent = MemoryAgent(store=store)
    state = WorkflowState(query="memory persistence test", use_mock_llm=True)
    state.status = "completed"

    agent.run(state)
    saved = store.get_run(state.run_id)

    assert saved is not None
    assert saved["run_id"] == state.run_id
    assert saved["query"] == "memory persistence test"

