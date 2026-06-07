from __future__ import annotations

from app.models.schemas import WorkflowState
from app.storage.memory import MemoryStore


class MemoryAgent:
    name = "memory_agent"

    def __init__(self, store: MemoryStore | None = None) -> None:
        self.store = store or MemoryStore()

    def run(self, state: WorkflowState) -> WorkflowState:
        self.store.save_state(state)
        state.add_note(self.name, "Persisted run state and artifact metadata to SQLite.")
        return state

