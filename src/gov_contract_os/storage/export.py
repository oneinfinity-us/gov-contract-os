"""Export helpers: dump Opportunity rows to JSON/CSV alongside the SQLite store."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from gov_contract_os.models.opportunity import Opportunity


def export_opportunities_json(opportunities: list[Opportunity], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [o.model_dump(mode="json") for o in opportunities]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


_CSV_FIELDS = [
    "id",
    "source_agency",
    "solicitation_number",
    "title",
    "status",
    "procurement_type",
    "due_at",
    "estimated_value_min",
    "estimated_value_max",
    "source_url",
]


def export_opportunities_csv(opportunities: list[Opportunity], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for o in opportunities:
            row = {field_name: getattr(o, field_name) for field_name in _CSV_FIELDS}
            row["due_at"] = o.due_at.isoformat() if o.due_at else ""
            writer.writerow(row)
