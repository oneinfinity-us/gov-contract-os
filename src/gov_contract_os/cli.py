"""Typer CLI - the deterministic commands OpenClaw (and humans) call.

    python -m gov_contract_os collect --all
    python -m gov_contract_os collect --source port_of_seattle
    python -m gov_contract_os analyze --new
    python -m gov_contract_os report daily
    python -m gov_contract_os rfp analyze opportunities/inbox/example.pdf
    python -m gov_contract_os demo

Any command that fails for one source must not crash the others - see
collect_all()'s per-connector try/except.
"""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from gov_contract_os.collectors.base import ConnectorHealthStatus
from gov_contract_os.collectors.registry import CONNECTOR_REGISTRY, get_connector
from gov_contract_os.config import REPO_ROOT, get_settings
from gov_contract_os.reports.daily import write_daily_report
from gov_contract_os.scoring.scorer import score_opportunity
from gov_contract_os.storage.db import (
    get_engine,
    init_db,
    list_opportunities,
    list_opportunities_without_analysis,
    make_session_factory,
    session_scope,
    upsert_analysis,
    upsert_opportunity,
)
from gov_contract_os.storage.export import export_opportunities_csv, export_opportunities_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("gov_contract_os.cli")

app = typer.Typer(help="gov-contract-os: government procurement opportunity automation.")
report_app = typer.Typer(help="Generate reports.")
rfp_app = typer.Typer(help="Analyze RFP/RFQ documents.")
app.add_typer(report_app, name="report")
app.add_typer(rfp_app, name="rfp")


def _session_factory():
    settings = get_settings()
    engine = get_engine(settings.db_path)
    init_db(engine)
    return make_session_factory(engine)


def _collect_one(source_name: str) -> str:
    """Collect one source. Returns one of: 'ok', 'skipped', 'partial'.

    Never re-raises: a failing single-item detail fetch is logged and skipped so
    it can't take down the rest of the source's items. If the whole source is
    unreachable, the outer collect() catches the exception.
    """
    connector = get_connector(source_name)
    health = connector.health_check()
    if health.status in (ConnectorHealthStatus.UNAVAILABLE, ConnectorHealthStatus.NOT_IMPLEMENTED):
        typer.echo(f"[{source_name}] SKIPPED ({health.status.value}): {health.reason}")
        if health.recommended_alternative:
            typer.echo(f"  alternative: {health.recommended_alternative}")
        if health.manual_inbox_hint:
            typer.echo(f"  manual inbox: {health.manual_inbox_hint}")
        return "skipped"

    session_factory = _session_factory()
    summaries = connector.discover()
    typer.echo(f"[{source_name}] discovered {len(summaries)} opportunities")

    stored = 0
    item_failures = 0
    with session_scope(session_factory) as session:
        for summary in summaries:
            try:
                detailed = connector.fetch_details(summary)
                _, created = upsert_opportunity(session, detailed)
                stored += 1
                if created:
                    typer.echo(f"  + new: {detailed.title}")
            except Exception as exc:  # noqa: BLE001 - one item's failure must not kill the source
                item_failures += 1
                logger.exception(
                    "fetch_details/upsert failed for source=%s item=%s",
                    source_name,
                    getattr(summary, "id", "<unknown>"),
                )
                typer.echo(f"  ! item failed ({exc}); continuing with remaining items")
    typer.echo(f"[{source_name}] stored/updated {stored} opportunities")
    return "partial" if item_failures else "ok"


@app.command()
def collect(
    all: bool = typer.Option(False, "--all", help="Collect from every registered source."),
    source: str = typer.Option(None, "--source", help="Collect from a single source by name."),
) -> None:
    """Discover opportunities from one or all registered sources."""
    if not all and not source:
        typer.echo("Specify --all or --source <name>.")
        raise typer.Exit(code=1)

    source_names = list(CONNECTOR_REGISTRY) if all else [source]
    outcomes: dict[str, int] = {"ok": 0, "partial": 0, "skipped": 0, "failed": 0, "unknown": 0}
    for name in source_names:
        if name not in CONNECTOR_REGISTRY:
            typer.echo(f"[{name}] unknown source. Valid: {', '.join(sorted(CONNECTOR_REGISTRY))}")
            outcomes["unknown"] += 1
            continue
        try:
            result = _collect_one(name)
            outcomes[result] += 1
        except Exception as exc:  # noqa: BLE001 - one source's failure must not stop the others
            logger.exception("collect failed for source=%s", name)
            typer.echo(f"[{name}] FAILED: {exc}")
            outcomes["failed"] += 1

    typer.echo(
        f"summary: ok={outcomes['ok']} partial={outcomes['partial']} "
        f"skipped={outcomes['skipped']} failed={outcomes['failed']} "
        f"unknown={outcomes['unknown']}"
    )
    # Non-zero exit only when the run had actual FAILURES or unknown source names.
    # NOT_IMPLEMENTED stubs and UNAVAILABLE sources are expected outcomes (they
    # report the reason and a manual inbox alternative), not errors.
    if outcomes["failed"] or outcomes["unknown"]:
        raise typer.Exit(code=1)


@app.command()
def analyze(
    new: bool = typer.Option(
        False, "--new", help="Score only opportunities without an Analysis yet."
    ),
) -> None:
    """Run Level-1 deterministic scoring and store the resulting Analysis rows."""
    if not new:
        typer.echo("Only --new is supported in this round.")
        raise typer.Exit(code=1)

    session_factory = _session_factory()
    with session_scope(session_factory) as session:
        pending = list_opportunities_without_analysis(session)
        typer.echo(f"Scoring {len(pending)} opportunities...")
        for opportunity in pending:
            analysis = score_opportunity(opportunity)
            upsert_analysis(session, analysis)
            typer.echo(
                f"  {opportunity.title}: score={analysis.fit_score} ({analysis.fit_level.value})"
            )


@report_app.command("daily")
def report_daily() -> None:
    """Generate today's daily opportunity report into reports/generated/."""
    session_factory = _session_factory()
    output_dir = REPO_ROOT / "reports" / "generated"
    with session_scope(session_factory) as session:
        path = write_daily_report(session, output_dir)
    typer.echo(f"Wrote {path}")


@app.command()
def export(
    output_dir: Path = typer.Option(
        REPO_ROOT / "runtime" / "export",
        "--output-dir",
        help="Directory to write json/csv exports to.",
    ),
) -> None:
    """Export all opportunities to JSON and CSV."""
    session_factory = _session_factory()
    with session_scope(session_factory) as session:
        opportunities = list_opportunities(session)
    json_path = output_dir / "opportunities.json"
    csv_path = output_dir / "opportunities.csv"
    export_opportunities_json(opportunities, json_path)
    export_opportunities_csv(opportunities, csv_path)
    typer.echo(f"Wrote {json_path} and {csv_path}")


@rfp_app.command("analyze")
def rfp_analyze(path: Path) -> None:
    """Analyze a single RFP/RFQ document from opportunities/inbox/. NOT IMPLEMENTED YET."""
    typer.echo(
        "rfp analyze is not implemented in this MVP round (Round 1 scope: skeleton only). "
        f"Requested file: {path}. Planned for a later round - see CLAUDE.md section 7."
    )
    raise typer.Exit(code=2)


@app.command()
def demo() -> None:
    """Launch the Government Contract Opportunity Copilot demo. NOT IMPLEMENTED YET."""
    typer.echo(
        "demo is not implemented in this MVP round (Round 1 scope: skeleton only). "
        "Planned: Streamlit or FastAPI UI - see CLAUDE.md section 9."
    )
    raise typer.Exit(code=2)


@app.callback()
def main() -> None:
    """gov-contract-os CLI entrypoint."""


if __name__ == "__main__":
    app()
