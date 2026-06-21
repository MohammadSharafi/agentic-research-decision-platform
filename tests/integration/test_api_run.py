import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from app.main import app


def test_api_run_endpoint_completes_mock_workflow():
    client = TestClient(app)
    response = client.post(
        "/run",
        json={"query": "Multi-agent AI systems for trustworthy clinical decision support", "use_mock_llm": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["evaluation_total"] >= 78
    assert payload["report_path"]
    assert payload["report_pdf_path"]

    pdf_response = client.get(f"/runs/{payload['run_id']}/report.pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF")
