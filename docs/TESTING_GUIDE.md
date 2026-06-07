# Testing Guide

## Unit Tests

Run:

```bash
pytest tests/unit
```

Unit tests cover planner output, mock research, analyst tables, critic revision decisions, fact checking, report writing, and visualization generation.
They also cover evaluator scoring, presentation generation, memory persistence, and LaTeX report generation.

## Integration Tests

Run:

```bash
pytest tests/integration
```

Integration tests cover the full workflow, mock-mode behavior, FastAPI health endpoint, and FastAPI run endpoint.

## End-to-End Tests

Run:

```bash
pytest tests/e2e
```

The e2e test runs the clinical decision support demo and verifies report, presentation, figures, and evaluation output.

## API Tests

Run:

```bash
pytest tests/integration/test_api.py tests/integration/test_api_run.py -v
```

The API tests use FastAPI's in-process test client and do not require a live network server.

## Test Without API Keys

Set:

```bash
export USE_MOCK_LLM=true
```

No paid API keys are required. Mock mode uses `data/mock_search_results/clinical_ai.json`.

## Mock Mode

Mock mode is deterministic. It ranks local sources, computes fixed rubric dimensions, and creates local artifacts. This makes tests reproducible and avoids network flakiness.

## Verbose Test Run

For final submission verification, run:

```bash
pytest -v
```

Interpretation:

- All tests passing means the agent classes, graph, API, report generation, presentation generation, and mock mode are operational.
- Skipped API tests usually mean FastAPI/httpx are not installed in the active environment.
- Failures should be fixed at the implementation level; do not delete failing tests.

## Expected Outputs

After tests or demo runs, expect files under:

- `outputs/reports/`
- `outputs/figures/{run_id}/`
- `outputs/evaluation/`
- `outputs/presentations/`
- `report/final_report.tex`
- `report/final_report.pdf`
