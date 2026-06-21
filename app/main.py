from __future__ import annotations

import json
from pathlib import Path

from app.graph.workflow import run_workflow
from app.models.schemas import RunRequest, RunResponse
from app.storage.memory import MemoryStore


try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
except Exception:  # pragma: no cover - FastAPI is installed through requirements
    FastAPI = None  # type: ignore


if FastAPI is not None:
    app = FastAPI(
        title="Agentic Research & Decision Intelligence Platform",
        version="1.0.0",
        description="Multi-agent research, analysis, reporting, and presentation generation API.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "agentic-research-decision-platform"}

    @app.post("/run", response_model=RunResponse)
    def run(request: RunRequest) -> RunResponse:
        state = run_workflow(request.query, use_mock_llm=request.use_mock_llm)
        return RunResponse(
            run_id=state.run_id,
            status=state.status,
            report_path=state.report_path,
            report_pdf_path=state.report_pdf_path,
            presentation_path=state.presentation_path,
            evaluation_total=state.evaluation.total,
        )

    def _run_payload(run_data: dict[str, object]) -> dict[str, object]:
        payload = run_data.get("payload", "{}")
        if isinstance(payload, dict):
            return payload
        try:
            parsed = json.loads(str(payload))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, object]:
        run_data = MemoryStore().get_run(run_id)
        if run_data is None:
            raise HTTPException(status_code=404, detail="Run not found")
        run_data["payload"] = _run_payload(run_data)
        return run_data

    @app.get("/runs/{run_id}/report.pdf")
    def get_report_pdf(run_id: str) -> FileResponse:
        run_data = MemoryStore().get_run(run_id)
        if run_data is None:
            raise HTTPException(status_code=404, detail="Report PDF not found")
        payload = _run_payload(run_data)
        path_value = payload.get("report_pdf_path")
        if not path_value and run_data.get("report_path"):
            path_value = str(Path(str(run_data["report_path"])).with_suffix(".pdf"))
        if not path_value:
            raise HTTPException(status_code=404, detail="Report PDF not found")
        path = Path(str(path_value))
        if not path.exists():
            raise HTTPException(status_code=404, detail="Report PDF file missing")
        return FileResponse(path, media_type="application/pdf", filename=path.name)

    @app.get("/runs/{run_id}/report")
    def get_report(run_id: str) -> FileResponse:
        run_data = MemoryStore().get_run(run_id)
        if run_data is None or not run_data.get("report_path"):
            raise HTTPException(status_code=404, detail="Report not found")
        path = Path(str(run_data["report_path"]))
        if not path.exists():
            raise HTTPException(status_code=404, detail="Report file missing")
        return FileResponse(path)

    @app.get("/runs/{run_id}/presentation")
    def get_presentation(run_id: str) -> FileResponse:
        run_data = MemoryStore().get_run(run_id)
        if run_data is None or not run_data.get("presentation_path"):
            raise HTTPException(status_code=404, detail="Presentation not found")
        path = Path(str(run_data["presentation_path"]))
        if not path.exists():
            raise HTTPException(status_code=404, detail="Presentation file missing")
        return FileResponse(path)

    @app.get("/runs/{run_id}/figures")
    def get_figures(run_id: str) -> dict[str, list[str]]:
        base = Path("outputs") / "figures" / run_id
        if not base.exists():
            raise HTTPException(status_code=404, detail="Figure directory not found")
        return {"figures": [str(path) for path in sorted(base.iterdir()) if path.is_file()]}
else:
    app = None
