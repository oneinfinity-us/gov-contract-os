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
    # Exit non-zero so OpenClaw / CI can detect the typo, but must not raise
    # (no traceback; message must be readable).
    assert result.exit_code == 1
    assert "unknown source" in result.output.lower()
    assert "summary:" in result.output.lower()


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


def test_collect_one_item_failure_does_not_abort_remaining_items(tmp_path, monkeypatch):
    """One bad opportunity must not kill the rest of the source (per CLAUDE.md).

    Uses a fake connector with 3 summaries where the middle fetch_details raises.
    The other two must still be stored and the exit code must be 0 (not fatal).
    """
    import datetime as dt

    from gov_contract_os.collectors.base import (
        Connector,
        ConnectorHealth,
        ConnectorHealthStatus,
    )
    from gov_contract_os.collectors.registry import CONNECTOR_REGISTRY
    from gov_contract_os.models.opportunity import (
        Opportunity,
        OpportunityStatus,
        SourceSystemType,
    )

    now = dt.datetime.now(dt.UTC)

    def _mk(i: int) -> Opportunity:
        return Opportunity(
            id=f"fake-{i}",
            source_agency="Fake",
            source_system=SourceSystemType.OFFICIAL_API,
            title=f"Fake {i}",
            status=OpportunityStatus.OPEN,
            discovered_at=now,
            last_checked_at=now,
        )

    class FlakyConnector(Connector):
        source_agency = "Fake"

        def discover(self):
            return [_mk(1), _mk(2), _mk(3)]

        def fetch_details(self, opportunity):
            if opportunity.id == "fake-2":
                raise RuntimeError("simulated per-item detail-fetch failure")
            return opportunity

        def fetch_documents(self, opportunity):
            return []

        def health_check(self):
            return ConnectorHealth(
                source_agency="Fake",
                status=ConnectorHealthStatus.OK,
                reason="test",
                checked_at=now,
            )

    monkeypatch.setitem(CONNECTOR_REGISTRY, "fake", FlakyConnector)
    monkeypatch.setattr(
        "gov_contract_os.cli.get_settings", lambda: Settings(db_path=tmp_path / "flaky.sqlite3")
    )

    result = runner.invoke(app, ["collect", "--source", "fake"])

    assert result.exit_code == 0, result.output
    assert "item failed" in result.output.lower()
    # 2 of 3 items should have been stored despite the middle one failing.
    assert "stored/updated 2 opportunities" in result.output


def test_collect_source_exception_marks_failed_and_exits_nonzero(tmp_path, monkeypatch):
    """A source that raises during discover() must be reported as FAILED and
    cause `collect` to exit non-zero so OpenClaw / CI can detect the problem,
    but must NOT crash the CLI with a traceback."""
    import datetime as dt

    from gov_contract_os.collectors.base import (
        Connector,
        ConnectorHealth,
        ConnectorHealthStatus,
    )
    from gov_contract_os.collectors.registry import CONNECTOR_REGISTRY

    class BrokenConnector(Connector):
        source_agency = "Broken"

        def discover(self):
            raise RuntimeError("simulated total-source failure")

        def fetch_details(self, opportunity):
            return opportunity

        def fetch_documents(self, opportunity):
            return []

        def health_check(self):
            return ConnectorHealth(
                source_agency="Broken",
                status=ConnectorHealthStatus.OK,
                reason="test",
                checked_at=dt.datetime.now(dt.UTC),
            )

    monkeypatch.setitem(CONNECTOR_REGISTRY, "broken", BrokenConnector)
    monkeypatch.setattr(
        "gov_contract_os.cli.get_settings", lambda: Settings(db_path=tmp_path / "broken.sqlite3")
    )

    result = runner.invoke(app, ["collect", "--source", "broken"])

    assert result.exit_code == 1
    assert "failed" in result.output.lower()
    assert "summary:" in result.output.lower()
