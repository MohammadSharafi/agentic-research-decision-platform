# Limitations

This is a serious engineering prototype, not a deployed clinical AI system.

| Limitation | Mitigation |
| --- | --- |
| Mock corpus is static | Add live search and freshness checks behind `search_sources` |
| Claim verification uses tags, not entailment | Add NLI or citation-span verification |
| Simple PDF renderer | Replace with Pandoc or LaTeX in production |
| No patient data governance | Add PHI controls, access logs, encryption, and institutional review |
| No clinical validation | Run prospective studies and follow CONSORT-AI, SPIRIT-AI, and DECIDE-AI |
| Basic UI | Add job queues, streaming status, authentication, and artifact browser |
| No real LLM adapter enabled by default | Add provider adapters while preserving mock mode |

The generated clinical decision support report must not be used for patient-specific diagnosis or treatment recommendations.

