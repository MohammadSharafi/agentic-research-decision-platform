from __future__ import annotations

from app.config.settings import get_settings
from app.models.schemas import EvaluationScore, WorkflowState
from app.tools.file_tools import ensure_dir, write_json, write_text
from app.tools.report_tools import markdown_table


class EvaluatorAgent:
    name = "evaluator_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        if not state.use_mock_llm:
            return self._run_dynamic(state)

        checks_supported = sum(1 for check in state.claim_checks if check.supported)
        checks_total = max(len(state.claim_checks), 1)
        figure_score = min(100, 55 + len(state.figures) * 5)
        scores = EvaluationScore(
            factuality=round(72 + 24 * (checks_supported / checks_total), 1),
            relevance=90,
            completeness=92 if len(state.tables) >= 5 and len(state.figures) >= 7 else 78,
            structure=88,
            citation_quality=round(70 + 25 * (checks_supported / checks_total), 1),
            clarity=89,
            visual_quality=figure_score,
            reproducibility=95,
        )
        values = [
            scores.factuality,
            scores.relevance,
            scores.completeness,
            scores.structure,
            scores.citation_quality,
            scores.clarity,
            scores.visual_quality,
            scores.reproducibility,
        ]
        scores.total = round(sum(values) / len(values), 1)
        state.evaluation = scores

        settings = get_settings()
        eval_dir = ensure_dir(settings.output_dir / "evaluation")
        payload = scores.model_dump() if hasattr(scores, "model_dump") else scores.dict()
        write_json(eval_dir / f"{state.run_id}_evaluation.json", payload)
        rows = [[key.replace("_", " ").title(), value] for key, value in payload.items()]
        write_text(eval_dir / f"{state.run_id}_evaluation.md", f"# Evaluation Results\n\n{markdown_table(['Dimension', 'Score'], rows)}\n")

        state.status = "evaluated"
        state.add_note(self.name, f"Evaluation score: {scores.total}/100.", threshold=settings.evaluation_threshold)
        return state

    def _run_dynamic(self, state: WorkflowState) -> WorkflowState:
        checks_supported = sum(1 for check in state.claim_checks if check.supported)
        checks_total = max(len(state.claim_checks), 1)
        support_ratio = checks_supported / checks_total
        source_count = len(state.sources)
        credible_sources = sum(1 for source in state.sources if source.credibility >= 0.8)
        table_count = len([table for table in state.tables if table.title.lower() != "final evaluation scores"])
        figure_count = len(state.figures)
        has_summary = bool(state.analysis.get("executive_summary"))
        has_findings = bool(state.analysis.get("key_findings"))

        scores = EvaluationScore(
            factuality=round(45 + 45 * support_ratio + min(10, credible_sources), 1),
            relevance=round(62 + min(23, source_count * 1.7) + (5 if has_summary else 0), 1),
            completeness=round(50 + min(25, table_count * 6) + min(15, figure_count * 5) + (10 if has_findings else 0), 1),
            structure=82 if table_count >= 2 and has_summary else 70,
            citation_quality=round(42 + 48 * support_ratio + min(10, source_count), 1),
            clarity=82 if has_summary and has_findings else 72,
            visual_quality=round(55 + min(35, figure_count * 12), 1),
            reproducibility=86,
        )
        values = [
            scores.factuality,
            scores.relevance,
            scores.completeness,
            scores.structure,
            scores.citation_quality,
            scores.clarity,
            scores.visual_quality,
            scores.reproducibility,
        ]
        scores.total = round(sum(values) / len(values), 1)
        state.evaluation = scores

        settings = get_settings()
        eval_dir = ensure_dir(settings.output_dir / "evaluation")
        payload = scores.model_dump() if hasattr(scores, "model_dump") else scores.dict()
        write_json(eval_dir / f"{state.run_id}_evaluation.json", payload)
        rows = [[key.replace("_", " ").title(), value] for key, value in payload.items()]
        write_text(eval_dir / f"{state.run_id}_evaluation.md", f"# Evaluation Results\n\n{markdown_table(['Dimension', 'Score'], rows)}\n")

        state.status = "evaluated"
        state.add_note(
            self.name,
            f"Dynamic evaluation score: {scores.total}/100.",
            threshold=settings.evaluation_threshold,
            supported_claims=checks_supported,
            total_claims=checks_total,
            source_count=source_count,
        )
        return state
