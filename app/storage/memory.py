from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config.settings import get_settings
from app.models.schemas import WorkflowState


class MemoryStore:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else get_settings().database_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    report_path TEXT,
                    presentation_path TEXT,
                    evaluation_total REAL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save_state(self, state: WorkflowState) -> None:
        payload = state.model_dump_json() if hasattr(state, "model_dump_json") else str(state.model_dump())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs
                (run_id, query, status, report_path, presentation_path, evaluation_total, payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.run_id,
                    state.query,
                    state.status,
                    state.report_path,
                    state.presentation_path,
                    state.evaluation.total,
                    payload,
                    state.created_at,
                ),
            )

    def get_run(self, run_id: str) -> dict[str, object] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT run_id, query, status, report_path, presentation_path, evaluation_total, payload, created_at FROM runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "run_id": row[0],
            "query": row[1],
            "status": row[2],
            "report_path": row[3],
            "presentation_path": row[4],
            "evaluation_total": row[5],
            "payload": row[6],
            "created_at": row[7],
        }

