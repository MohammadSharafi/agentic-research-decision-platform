from __future__ import annotations

import json
from pathlib import Path

from app.config.settings import PROJECT_DIR, get_settings
from app.models.schemas import Source


def load_mock_sources() -> list[Source]:
    path = PROJECT_DIR / "data" / "mock_search_results" / "clinical_ai.json"
    items = json.loads(path.read_text(encoding="utf-8"))
    return [Source(**item) for item in items]


def keyword_score(query: str, source: Source) -> int:
    haystack = f"{source.title} {source.summary} {' '.join(source.tags)}".lower()
    tokens = {token.strip(".,:;()[]").lower() for token in query.split() if len(token) > 3}
    return sum(1 for token in tokens if token in haystack)


def search_sources(query: str, limit: int = 12) -> list[Source]:
    settings = get_settings()
    sources = load_mock_sources()
    ranked = sorted(sources, key=lambda src: (keyword_score(query, src), src.credibility), reverse=True)
    if settings.use_mock_llm or not (settings.tavily_api_key or settings.serpapi_api_key):
        return ranked[:limit]
    # The production extension point is explicit: external search can be added here
    # without changing agent contracts. Offline mock search remains deterministic.
    return ranked[:limit]

