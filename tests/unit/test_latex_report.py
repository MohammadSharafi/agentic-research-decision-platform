from pathlib import Path

from app.graph.workflow import run_workflow


def test_latex_report_is_generated():
    state = run_workflow("Multi-agent AI systems for trustworthy clinical decision support", use_mock_llm=True)

    tex_path = Path("report/final_report.tex")
    assert tex_path.exists()
    assert Path(state.report_pdf_path).exists()
    assert Path(state.report_pdf_path).read_bytes().startswith(b"%PDF")

    tex = tex_path.read_text(encoding="utf-8")
    assert r"\begin{tabularx}" in tex
    assert r"\newcolumntype{Y}" in tex
    assert r"$Q < \tau$" in tex
    assert "Algorithm 1: Conditional multi-agent execution" in tex
    assert "Algorithm 2: Claim grounding and citation gating" in tex
    assert "keepaspectratio" in tex
