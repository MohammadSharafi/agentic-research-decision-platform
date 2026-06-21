from __future__ import annotations

from app.models.schemas import WorkflowState
from app.tools.search_tools import search_sources


class ResearchAgent:
    name = "research_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        limit = 24 if state.use_mock_llm else (16 if state.revision_count else 12)
        sources = search_sources(state.query, limit=limit, use_mock_llm=state.use_mock_llm)
        existing = {source.id for source in state.sources}
        for source in sources:
            if source.id not in existing:
                state.sources.append(source)
        state.status = "researched"
        mode = "mock corpus" if state.use_mock_llm else "real retrieval adapters"
        state.add_note(
            self.name,
            f"Retrieved {len(sources)} ranked sources using {mode}; cumulative evidence base has {len(state.sources)} items.",
            source_ids=[source.id for source in sources],
        )
        return state
