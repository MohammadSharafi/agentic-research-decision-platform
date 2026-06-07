from __future__ import annotations

from app.models.schemas import WorkflowState


class CriticAgent:
    name = "critic_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        critique: list[str] = []
        if len(state.sources) < 10:
            critique.append("Evidence base is thin for an academic final report; request another research pass.")
        if state.analysis.get("evidence_quality", 0) < 0.75:
            critique.append("Average source credibility is below the desired threshold.")
        if "clinical" in state.query.lower() and not any("clinical" in source.tags for source in state.sources):
            critique.append("Clinical evidence is underrepresented for the selected topic.")
        if not critique:
            critique.extend(
                [
                    "Evidence coverage is adequate for a prototype, but deployment claims must remain bounded.",
                    "The system should emphasize clinician oversight, auditability, and uncertainty rather than autonomous diagnosis.",
                    "The mock corpus is suitable for reproducible testing but must be refreshed for real clinical use.",
                ]
            )
            state.needs_revision = False
        else:
            state.needs_revision = state.revision_count < state.max_revisions
            state.revision_count += 1
        state.critique = critique
        state.status = "critiqued"
        state.add_note(self.name, "Critique completed.", needs_revision=state.needs_revision, critique=critique)
        return state

