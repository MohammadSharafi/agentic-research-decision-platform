import compileall
from pathlib import Path

from app.ui.ui_helpers import (
    DEMO_TOPICS,
    REQUIRED_RESULT_IMAGES,
    REQUIRED_UI_SCREENSHOTS,
    TAB_NAMES,
    WORKFLOW_STAGES,
    contains_hardcoded_user_path,
    evaluation_rows,
    get_output_dir,
    resolve_report_path,
    screenshot_seed_enabled,
)
from app.models.schemas import WorkflowState


def test_streamlit_app_compiles():
    assert compileall.compile_file("app/ui/streamlit_app.py", quiet=1)


def test_ui_helpers_exist():
    assert len(DEMO_TOPICS) >= 3
    assert len(WORKFLOW_STAGES) >= 10
    assert len(TAB_NAMES) == 7
    assert "ui_home.png" in REQUIRED_UI_SCREENSHOTS
    assert "demo_evaluation_score.png" in REQUIRED_RESULT_IMAGES


def test_evaluation_rows_and_paths():
    state = WorkflowState(query="test", use_mock_llm=True)
    state.evaluation.total = 90
    rows = evaluation_rows(state)
    assert any(row[0] == "Total" for row in rows)
    assert get_output_dir().name == "outputs" or get_output_dir().exists()
    assert resolve_report_path(state) is None


def test_mock_mode_flag_on_state():
    state = WorkflowState(query="clinical AI", use_mock_llm=True)
    assert state.use_mock_llm is True


def test_no_hardcoded_absolute_user_paths_in_ui_code():
    ui_files = [Path("app/ui/streamlit_app.py"), Path("app/ui/ui_helpers.py")]
    for path in ui_files:
        text = path.read_text(encoding="utf-8")
        assert not contains_hardcoded_user_path(text)


def test_screenshot_seed_helper_reads_env(monkeypatch):
    monkeypatch.delenv("STREAMLIT_SCREENSHOT_SEED", raising=False)
    assert screenshot_seed_enabled() is False
    monkeypatch.setenv("STREAMLIT_SCREENSHOT_SEED", "1")
    assert screenshot_seed_enabled() is True
