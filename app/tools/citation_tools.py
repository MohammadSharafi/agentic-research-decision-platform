from __future__ import annotations

from app.models.schemas import Source


def citation_marker(source: Source) -> str:
    author = source.authors.split(",")[0].split(" and ")[0].strip() or source.title.split()[0]
    year = source.year or "n.d."
    return f"({author}, {year})"


def numbered_references(sources: list[Source]) -> str:
    lines: list[str] = []
    for idx, src in enumerate(sources, start=1):
        year = src.year or "n.d."
        lines.append(f"{idx}. {src.authors} ({year}). *{src.title}*. [{src.url}]({src.url})")
    return "\n".join(lines)
