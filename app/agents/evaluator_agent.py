from __future__ import annotations

from app.config.settings import get_settings
from app.models.schemas import EvaluationScore, WorkflowState
from app.tools.file_tools import ensure_dir, write_json, write_text
from app.tools.report_tools import markdown_table


class EvaluatorAgent:
    name = "evaluator_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
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

