from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

import requests

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


def search_sources(query: str, limit: int = 12, use_mock_llm: bool | None = None) -> list[Source]:
    settings = get_settings()
    use_mock = settings.use_mock_llm if use_mock_llm is None else use_mock_llm
    mock_sources = load_mock_sources()
    ranked_mock = sorted(mock_sources, key=lambda src: (keyword_score(query, src), src.credibility), reverse=True)
    if use_mock:
        return ranked_mock[:limit]

    real_sources: list[Source] = []
    if settings.tavily_api_key:
        real_sources.extend(_search_tavily(query, settings.tavily_api_key, limit))
    if len(real_sources) < limit and settings.serpapi_api_key:
        real_sources.extend(_search_serpapi(query, settings.serpapi_api_key, limit))

    deduped = _dedupe_sources(real_sources)
    if deduped:
        return deduped[:limit]
    return ranked_mock[:limit]


def _search_tavily(query: str, api_key: str, limit: int) -> list[Source]:
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": min(max(limit, 3), 10),
        "include_answer": False,
        "include_raw_content": False,
    }
    try:
        response = requests.post("https://api.tavily.com/search", json=payload, timeout=35)
        response.raise_for_status()
        results = response.json().get("results", [])
    except Exception:
        return []

    sources: list[Source] = []
    for idx, item in enumerate(results, start=1):
        title = str(item.get("title") or "Untitled result").strip()
        url = str(item.get("url") or "").strip()
        summary = str(item.get("content") or item.get("snippet") or "").strip()
        if not url or not summary or _is_low_quality_domain(url):
            continue
        sources.append(_source_from_result("tavily", idx, title, url, summary, query, item.get("score")))
    return sources


def _search_serpapi(query: str, api_key: str, limit: int) -> list[Source]:
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": min(max(limit, 3), 10),
    }
    try:
        response = requests.get("https://serpapi.com/search.json", params=params, timeout=35)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
    except Exception:
        return []

    sources: list[Source] = []
    for idx, item in enumerate(results, start=1):
        title = str(item.get("title") or "Untitled result").strip()
        url = str(item.get("link") or "").strip()
        summary = str(item.get("snippet") or "").strip()
        if not url or not summary or _is_low_quality_domain(url):
            continue
        sources.append(_source_from_result("serpapi", idx, title, url, summary, query, None))
    return sources


def _source_from_result(
    provider: str,
    idx: int,
    title: str,
    url: str,
    summary: str,
    query: str,
    provider_score: object | None,
) -> Source:
    domain = urlparse(url).netloc.lower().replace("www.", "")
    credibility = _credibility_for_domain(domain, provider_score)
    source_id = f"{provider}-{idx}-{_slug(title or domain)}"
    return Source(
        id=source_id,
        title=title,
        authors=domain or provider,
        year=_infer_year(f"{title} {summary}"),
        url=url,
        source_type=_source_type_for_domain(domain),
        summary=summary[:900],
        credibility=credibility,
        tags=_infer_tags(query, title, summary, domain),
    )


def _dedupe_sources(sources: list[Source]) -> list[Source]:
    seen: set[str] = set()
    deduped: list[Source] = []
    for source in sources:
        key = source.url.rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(source)
    return deduped


def _is_low_quality_domain(url: str) -> bool:
    domain = urlparse(url).netloc.lower().replace("www.", "")
    blocked = [
        "facebook.com",
        "quora.com",
        "pinterest.",
        "instagram.com",
        "tiktok.com",
        "x.com",
        "twitter.com",
    ]
    return any(token in domain for token in blocked)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "source"


def _infer_year(text: str) -> int | None:
    years = [int(match) for match in re.findall(r"\b(20[0-2][0-9]|19[8-9][0-9])\b", text)]
    return max(years) if years else None


def _source_type_for_domain(domain: str) -> str:
    if domain.endswith(".gov") or ".gov." in domain:
        return "government"
    if domain.endswith(".edu") or ".edu." in domain:
        return "academic"
    if "worldbank" in domain or "oecd" in domain or "imf" in domain or "who.int" in domain:
        return "institutional"
    if "wikipedia" in domain:
        return "encyclopedia"
    return "web"


def _credibility_for_domain(domain: str, provider_score: object | None) -> float:
    base = 0.72
    if domain.endswith(".gov") or domain.endswith(".edu"):
        base = 0.88
    if any(token in domain for token in ["worldbank", "imf", "oecd", "who.int", "un.org", "data.tuik.gov.tr"]):
        base = 0.91
    if any(token in domain for token in ["wikipedia", "britannica"]):
        base = 0.78
    try:
        if provider_score is not None:
            base = max(base, min(0.95, 0.70 + (float(provider_score) * 0.20)))
    except Exception:
        pass
    return round(base, 2)


def _infer_tags(query: str, title: str, summary: str, domain: str) -> list[str]:
    text = f"{title} {summary} {domain}".lower()
    tag_map = {
        "economy": ["economy", "economic", "gdp", "inflation", "trade", "unemployment"],
        "health": ["health", "healthcare", "hospital", "life expectancy"],
        "education": ["education", "school", "university", "literacy"],
        "technology": ["technology", "digital", "innovation", "startup", "internet"],
        "geopolitics": ["geopolitical", "foreign policy", "security", "risk", "sanction"],
        "energy": ["energy", "oil", "gas", "electricity"],
        "demographics": ["population", "demographic", "migration"],
        "governance": ["governance", "policy", "government", "regulation"],
    }
    tags = [tag for tag, needles in tag_map.items() if any(needle in text for needle in needles)]
    query_tokens = [
        token
        for token in re.findall(r"[A-Za-z][A-Za-z]{3,}", query.lower())[:6]
        if token not in {"compare", "across", "economy", "healthcare", "education", "technology", "geopolitical", "risk"}
    ]
    for token in query_tokens:
        if token not in tags:
            tags.append(token)
    return tags[:8] or ["general"]
