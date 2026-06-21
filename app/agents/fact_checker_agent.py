from __future__ import annotations

import re

from app.models.schemas import ClaimCheck, WorkflowState
from app.tools.citation_tools import citation_marker


class FactCheckingAgent:
    name = "fact_checker_agent"

    def run(self, state: WorkflowState) -> WorkflowState:
        if not state.use_mock_llm and state.analysis.get("main_claims"):
            return self._run_dynamic(state)

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

    def _run_dynamic(self, state: WorkflowState) -> WorkflowState:
        claims = [str(claim) for claim in state.analysis.get("main_claims", []) if str(claim).strip()]
        state.claim_checks = []
        for claim in claims[:8]:
            matches = self._matching_sources(claim, state)
            citations = [citation_marker(source) for source in matches[:3]]
            state.claim_checks.append(
                ClaimCheck(
                    claim=claim,
                    supported=bool(citations),
                    citations=sorted(set(citations)),
                    note="Matched against retrieved source title, summary, or tags." if citations else "No retrieved source had enough lexical overlap.",
                )
            )
        unsupported = [check.claim for check in state.claim_checks if not check.supported]
        if unsupported:
            state.critique.append(f"Unsupported or weakly supported claims require caution: {unsupported[:3]}")
        state.status = "fact_checked"
        state.add_note(self.name, f"Dynamically checked {len(state.claim_checks)} claims; unsupported={len(unsupported)}.")
        return state

    def _matching_sources(self, claim: str, state: WorkflowState):
        claim_tokens = self._tokens(claim)
        scored = []
        for source in state.sources:
            haystack = f"{source.title} {source.summary} {' '.join(source.tags)}"
            source_tokens = self._tokens(haystack)
            overlap = len(claim_tokens & source_tokens)
            if overlap >= 2:
                scored.append((overlap + source.credibility, source))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [source for _, source in scored]

    def _tokens(self, text: str) -> set[str]:
        stopwords = {
            "this",
            "that",
            "with",
            "from",
            "into",
            "about",
            "between",
            "across",
            "their",
            "there",
            "which",
            "using",
            "should",
            "would",
            "could",
        }
        return {
            token
            for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
            if token not in stopwords
        }
