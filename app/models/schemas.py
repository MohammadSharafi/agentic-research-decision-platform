from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.compat import BaseModel, Field


class Source(BaseModel):
    id: str
    title: str
    authors: str = ""
    year: int | None = None
    url: str
    source_type: str = "paper"
    summary: str
    credibility: float = 0.8
    tags: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    id: str
    description: str
    agent: str
    status: str = "pending"
    depends_on: list[str] = Field(default_factory=list)


class AgentMessage(BaseModel):
    agent: str
    content: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisTable(BaseModel):
    title: str
    columns: list[str]
    rows: list[list[Any]]


class ClaimCheck(BaseModel):
    claim: str
    supported: bool
    citations: list[str] = Field(default_factory=list)
    note: str = ""


class GeneratedFigure(BaseModel):
    id: str
    title: str
    path: str
    figure_type: str
    description: str


class EvaluationScore(BaseModel):
    factuality: float = 0
    relevance: float = 0
    completeness: float = 0
    structure: float = 0
    citation_quality: float = 0
    clarity: float = 0
    visual_quality: float = 0
    reproducibility: float = 0
    total: float = 0


class WorkflowState(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    query: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    use_mock_llm: bool = True
    revision_count: int = 0
    max_revisions: int = 2
    plan: list[PlanStep] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    notes: list[AgentMessage] = Field(default_factory=list)
    analysis: dict[str, Any] = Field(default_factory=dict)
    tables: list[AnalysisTable] = Field(default_factory=list)
    critique: list[str] = Field(default_factory=list)
    needs_revision: bool = False
    claim_checks: list[ClaimCheck] = Field(default_factory=list)
    figures: list[GeneratedFigure] = Field(default_factory=list)
    report_path: str = ""
    report_pdf_path: str = ""
    presentation_path: str = ""
    evaluation: EvaluationScore = Field(default_factory=EvaluationScore)
    status: str = "initialized"
    errors: list[str] = Field(default_factory=list)

    def add_note(self, agent: str, content: str, **metadata: Any) -> None:
        self.notes.append(AgentMessage(agent=agent, content=content, metadata=metadata))


class RunRequest(BaseModel):
    query: str
    use_mock_llm: bool = True


class RunResponse(BaseModel):
    run_id: str
    status: str
    report_path: str = ""
    presentation_path: str = ""
    evaluation_total: float = 0


def path_for_display(path: str | Path) -> str:
    return str(Path(path).resolve())

