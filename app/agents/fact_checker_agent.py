from __future__ import annotations

from app.models.schemas import ClaimCheck, WorkflowState
from app.tools.citation_tools import citation_marker


class FactCheckingAgent:
    name = "fact_checker_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        by_tag: dict[str, list[str]] = {}
        for source in state.sources:
            for tag in source.tags:
                by_tag.setdefault(tag, []).append(citation_marker(source))

        checks = [
            ("Retrieval grounding can reduce unsupported generation by forcing reports to cite external evidence.", "rag"),
            ("Clinical decision support requires human oversight and careful workflow integration.", "clinical"),
            ("Conditional multi-agent graphs make critique and revision loops explicit.", "agentic"),
            ("Evaluation should include factuality, relevance, structure, citation quality, and reproducibility.", "evaluation"),
            ("The prototype is not a medical device and should not produce patient-specific diagnosis.", "ethics"),
        ]
        state.claim_checks = []
        for claim, tag in checks:
            citations = sorted(set(by_tag.get(tag, [])[:3]))
            state.claim_checks.append(
                ClaimCheck(
                    claim=claim,
                    supported=bool(citations),
                    citations=citations,
                    note="Supported by tagged source evidence." if citations else "No supporting source tag found.",
                )
            )
        unsupported = [check.claim for check in state.claim_checks if not check.supported]
        if unsupported:
            state.critique.append(f"Unsupported claims require revision: {unsupported}")
        state.status = "fact_checked"
        state.add_note(self.name, f"Checked {len(state.claim_checks)} major claims; unsupported={len(unsupported)}.")
        return state
