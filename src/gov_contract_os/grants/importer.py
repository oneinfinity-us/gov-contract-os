"""Manual grant import from `opportunities/grants/inbox/<slug>/manifest.yaml`.

Phase 1: no LLM extraction. A human (or an LLM-assisted human) drops a folder
containing:
    inbox/<slug>/manifest.yaml    # required - the structured metadata
    inbox/<slug>/*.pdf            # optional source document(s)
and runs `python -m gov_contract_os grants import <folder>`. The manifest is
validated against the GrantOpportunity schema and upserted.

Phase 2 will add an LLM-assisted extractor that reads the PDF and writes an
initial manifest.yaml for a human to review/correct.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml

from gov_contract_os.core.types import GRANT_TYPES, OpportunityType
from gov_contract_os.grants.models import (
    EligibleApplicantType,
    FunderType,
    GrantOpportunity,
    GrantStage,
)
from gov_contract_os.models.opportunity import Document, SourceSystemType


class GrantImportError(RuntimeError):
    pass


def _parse_datetime(value) -> dt.datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.UTC)
    if isinstance(value, dt.date):
        return dt.datetime(value.year, value.month, value.day, tzinfo=dt.UTC)
    if isinstance(value, str):
        # Accept ISO 8601. Anything else is a manifest bug the human should fix.
        try:
            parsed = dt.datetime.fromisoformat(value)
        except ValueError as exc:
            raise GrantImportError(f"Cannot parse datetime {value!r}: {exc}") from exc
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.UTC)
    raise GrantImportError(f"Unsupported datetime value: {value!r}")


def import_grant_from_manifest(
    manifest_path: Path,
    now: dt.datetime | None = None,
) -> GrantOpportunity:
    """Load a manifest.yaml, build a GrantOpportunity, and return it.

    Does not touch the database - the CLI layer is responsible for calling
    `upsert_grant` after any additional validation/logging.
    """
    if not manifest_path.exists():
        raise GrantImportError(f"Manifest not found: {manifest_path}")
    now = now or dt.datetime.now(dt.UTC)

    with manifest_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        raise GrantImportError(f"Manifest must be a mapping: {manifest_path}")

    required = {"funder_name", "funder_type", "program_name", "title", "opportunity_type"}
    missing = required - raw.keys()
    if missing:
        raise GrantImportError(
            f"Manifest {manifest_path} missing required fields: {sorted(missing)}"
        )

    try:
        opportunity_type = OpportunityType(raw["opportunity_type"])
    except ValueError as exc:
        raise GrantImportError(
            f"Unknown opportunity_type {raw['opportunity_type']!r} in {manifest_path}"
        ) from exc
    if opportunity_type not in GRANT_TYPES:
        raise GrantImportError(
            f"opportunity_type must be a grant type, got {opportunity_type.value!r}"
        )

    try:
        funder_type = FunderType(raw["funder_type"])
    except ValueError as exc:
        raise GrantImportError(
            f"Unknown funder_type {raw['funder_type']!r} in {manifest_path}"
        ) from exc

    stage_raw = raw.get("stage", "open")
    try:
        stage = GrantStage(stage_raw)
    except ValueError as exc:
        raise GrantImportError(f"Unknown stage {stage_raw!r} in {manifest_path}") from exc

    eligible_applicants: list[EligibleApplicantType] = []
    for entry in raw.get("eligible_applicants", []) or []:
        try:
            eligible_applicants.append(EligibleApplicantType(entry))
        except ValueError as exc:
            raise GrantImportError(
                f"Unknown eligible_applicants entry {entry!r} in {manifest_path}"
            ) from exc

    documents: list[Document] = []
    for doc in raw.get("documents", []) or []:
        if not isinstance(doc, dict) or not doc.get("name"):
            raise GrantImportError(
                f"documents[] entries must be mappings with a 'name': got {doc!r}"
            )
        documents.append(Document(**doc))

    # Also treat any local files sitting next to manifest.yaml as documents
    # (best-effort; the manifest can override or add URLs).
    manifest_dir = manifest_path.parent
    for local_file in sorted(manifest_dir.iterdir()):
        if local_file.name == manifest_path.name or local_file.is_dir():
            continue
        # Skip if already listed by name
        if any(d.name == local_file.name for d in documents):
            continue
        documents.append(
            Document(name=local_file.name, url=None, document_type="local")
        )

    full_due = _parse_datetime(raw.get("full_proposal_due_at"))
    loi_due = _parse_datetime(raw.get("loi_due_at"))

    grant_id = raw.get("id") or GrantOpportunity.build_id(
        funder_name=raw["funder_name"],
        funding_opportunity_number=raw.get("funding_opportunity_number"),
        source_url=raw.get("source_url"),
        title=raw["title"],
        full_proposal_due_at=full_due,
    )

    source_system_raw = raw.get("source_system", SourceSystemType.MANUAL_INBOX.value)
    try:
        source_system = SourceSystemType(source_system_raw)
    except ValueError as exc:
        raise GrantImportError(
            f"Unknown source_system {source_system_raw!r} in {manifest_path}"
        ) from exc

    return GrantOpportunity(
        id=grant_id,
        opportunity_type=opportunity_type,
        funder_name=raw["funder_name"],
        funder_type=funder_type,
        program_name=raw["program_name"],
        funding_opportunity_number=raw.get("funding_opportunity_number"),
        title=raw["title"],
        description=raw.get("description"),
        stage=stage,
        posted_at=_parse_datetime(raw.get("posted_at")),
        loi_due_at=loi_due,
        full_proposal_due_at=full_due,
        award_notification_at=_parse_datetime(raw.get("award_notification_at")),
        project_start_at=_parse_datetime(raw.get("project_start_at")),
        project_end_at=_parse_datetime(raw.get("project_end_at")),
        award_ceiling=raw.get("award_ceiling"),
        award_floor=raw.get("award_floor"),
        total_program_funding=raw.get("total_program_funding"),
        expected_awards_count=raw.get("expected_awards_count"),
        cost_share_required=raw.get("cost_share_required"),
        cost_share_percent=raw.get("cost_share_percent"),
        indirect_cost_limit_percent=raw.get("indirect_cost_limit_percent"),
        currency=raw.get("currency", "USD"),
        eligible_applicants=eligible_applicants,
        focus_areas=list(raw.get("focus_areas", []) or []),
        geographic_scope=list(raw.get("geographic_scope", []) or []),
        populations_served=list(raw.get("populations_served", []) or []),
        cfda_or_aln_codes=list(raw.get("cfda_or_aln_codes", []) or []),
        requires_501c3=raw.get("requires_501c3"),
        requires_sam_registration=raw.get("requires_sam_registration"),
        invitation_only=bool(raw.get("invitation_only", False)),
        letter_of_inquiry_required=bool(raw.get("letter_of_inquiry_required", False)),
        preapplication_required=bool(raw.get("preapplication_required", False)),
        mandatory_requirements=list(raw.get("mandatory_requirements", []) or []),
        required_documents=list(raw.get("required_documents", []) or []),
        reporting_requirements=list(raw.get("reporting_requirements", []) or []),
        evaluation_requirements=list(raw.get("evaluation_requirements", []) or []),
        source_system=source_system,
        source_url=raw.get("source_url"),
        contact_name=raw.get("contact_name"),
        contact_email=raw.get("contact_email"),
        documents=documents,
        discovered_at=_parse_datetime(raw.get("discovered_at")) or now,
        last_checked_at=now,
        content_hash=None,
        raw_source_reference=str(manifest_path),
    )
