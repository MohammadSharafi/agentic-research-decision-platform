from pathlib import Path

from app.agents.analyst_agent import DataAnalystAgent
from app.agents.fact_checker_agent import FactCheckingAgent
from app.agents.report_writer_agent import ReportWriterAgent
from app.agents.research_agent import ResearchAgent
from app.agents.visualization_agent import VisualizationAgent
from app.models.schemas import WorkflowState


def test_report_writer_creates_markdown_report():
    state = WorkflowState(query="clinical AI")
    for agent in [ResearchAgent(), DataAnalystAgent(), FactCheckingAgent(), VisualizationAgent(), ReportWriterAgent()]:
        state = agent.run(state)
    assert Path(state.report_path).exists()
    assert "References" in Path(state.report_path).read_text(encoding="utf-8")

