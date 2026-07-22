"""Generate the daily opportunity report (markdown) into reports/generated/.

Deterministic - just aggregates what's already in the database; any judgment
calls belong in skills/workflows, not here (see CLAUDE.md scripts/ principle).
"""

from __future__ import annotations

import datetime as dt
from collections import Counter
from pathlib import Path

from sqlalchemy.orm import Session

from gov_contract_os.models.analysis import FitLevel
from gov_contract_os.storage.db import get_analysis, list_opportunities

HIGH_FIT_LEVELS = {FitLevel.IMMEDIATE_ATTENTION, FitLevel.WORTH_ANALYZING}
UPCOMING_DUE_WINDOW_DAYS = 14


def generate_daily_report(session: Session, report_date: dt.date | None = None) -> str:
    report_date = report_date or dt.date.today()
    now = dt.datetime.now(dt.UTC)
    opportunities = list_opportunities(session)

    agency_counts = Counter(o.source_agency for o in opportunities)
    due_soon = [
        o
        for o in opportunities
        if o.due_at
        and dt.timedelta(0) <= (o.due_at - now) <= dt.timedelta(days=UPCOMING_DUE_WINDOW_DAYS)
    ]

    high_fit_rows: list[str] = []
    high_fit_count = 0
    for o in sorted(
        opportunities, key=lambda x: x.due_at or dt.datetime.max.replace(tzinfo=dt.UTC)
    ):
        analysis = get_analysis(session, o.id)
        if analysis is None:
            continue
        if FitLevel(analysis.fit_level) in HIGH_FIT_LEVELS:
            high_fit_count += 1
            due_str = o.due_at.strftime("%Y-%m-%d") if o.due_at else "unknown"
            high_fit_rows.append(
                f"| {o.source_agency} | {o.title} | {due_str} | {analysis.fit_score} | "
                f"{analysis.recommended_role} |"
            )

    lines = [
        f"# Daily Opportunity Report - {report_date.isoformat()}",
        "",
        "## Dashboard",
        "",
        f"- Total tracked opportunities: {len(opportunities)}",
        f"- High-fit opportunities (worth_analyzing / immediate_attention): {high_fit_count}",
        f"- Due within {UPCOMING_DUE_WINDOW_DAYS} days: {len(due_soon)}",
        f"- Sources represented: {', '.join(sorted(agency_counts)) or '(none)'}",
        "",
        "### By agency",
        "",
        "| Agency | Count |",
        "|---|---|",
    ]
    for agency, count in sorted(agency_counts.items()):
        lines.append(f"| {agency} | {count} |")

    lines += [
        "",
        "## High-fit opportunities",
        "",
        "| Agency | Title | Due | Fit score | Recommended role |",
        "|---|---|---|---|---|",
    ]
    lines += high_fit_rows or ["| (none) | | | | |"]

    lines += [
        "",
        "## Upcoming deadlines (next 14 days)",
        "",
        "| Agency | Title | Due |",
        "|---|---|---|",
    ]
    for o in sorted(due_soon, key=lambda x: x.due_at):
        lines.append(
            f"| {o.source_agency} | {o.title} | {o.due_at.strftime('%Y-%m-%d %H:%M %Z')} |"
        )
    if not due_soon:
        lines.append("| (none) | | |")

    lines += [
        "",
        "---",
        "_Draft only. Human review required before any go/no-bid decision or proposal action._",
    ]
    return "\n".join(lines) + "\n"


def write_daily_report(
    session: Session, output_dir: Path, report_date: dt.date | None = None
) -> Path:
    report_date = report_date or dt.date.today()
    content = generate_daily_report(session, report_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"daily-{report_date.isoformat()}.md"
    path.write_text(content, encoding="utf-8")
    return path
