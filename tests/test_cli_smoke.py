from __future__ import annotations

from typer.testing import CliRunner

from gov_contract_os.cli import app
from gov_contract_os.config import Settings

runner = CliRunner()


def test_collect_requires_all_or_source():
    result = runner.invoke(app, ["collect"])
    assert result.exit_code == 1


def test_collect_unknown_source_reports_and_does_not_crash():
    result = runner.invoke(app, ["collect", "--source", "not_a_real_source"])
    assert result.exit_code == 0
    assert "unknown source" in result.output.lower()


def test_rfp_analyze_stub_reports_not_implemented(tmp_path):
    target = tmp_path / "example.pdf"
    target.write_text("placeholder")
    result = runner.invoke(app, ["rfp", "analyze", str(target)])
    assert result.exit_code == 2
    assert "not implemented" in result.output.lower()


def test_demo_stub_reports_not_implemented():
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 2
    assert "not implemented" in result.output.lower()


def test_report_daily_writes_file_with_isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gov_contract_os.cli.get_settings", lambda: Settings(db_path=tmp_path / "test.sqlite3")
    )
    monkeypatch.setattr("gov_contract_os.cli.REPO_ROOT", tmp_path)

    result = runner.invoke(app, ["report", "daily"])

    assert result.exit_code == 0
    generated_dir = tmp_path / "reports" / "generated"
    assert list(generated_dir.glob("daily-*.md"))


def test_analyze_new_with_empty_db_does_not_crash(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "gov_contract_os.cli.get_settings", lambda: Settings(db_path=tmp_path / "test2.sqlite3")
    )

    result = runner.invoke(app, ["analyze", "--new"])

    assert result.exit_code == 0
    assert "Scoring 0 opportunities" in result.output
