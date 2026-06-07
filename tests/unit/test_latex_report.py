from pathlib import Path

from app.graph.workflow import run_workflow


def test_latex_report_is_generated():
    state = run_workflow("Multi-agent AI systems for trustworthy clinical decision support", use_mock_llm=True)

    assert Path("report/final_report.tex").exists()
    assert Path(state.report_pdf_path).exists()
    assert Path(state.report_pdf_path).read_bytes().startswith(b"%PDF")

