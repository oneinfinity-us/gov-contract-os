from __future__ import annotations

from textwrap import dedent

import pytest

from gov_contract_os.core.types import OpportunityType
from gov_contract_os.grants.importer import GrantImportError, import_grant_from_manifest
from gov_contract_os.grants.models import EligibleApplicantType, FunderType, GrantStage
from gov_contract_os.models.opportunity import SourceSystemType


def _write_manifest(path, content: str) -> None:
    path.write_text(dedent(content), encoding="utf-8")


def test_import_minimal_manifest(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest,
        """
        opportunity_type: government_grant
        funder_name: Test Agency
        funder_type: federal_agency
        program_name: Community Health
        title: Community Health Technology Grant
        funding_opportunity_number: TEST-2026-001
        full_proposal_due_at: 2026-09-01T17:00:00+00:00
        award_ceiling: 250000
        award_floor: 50000
        eligible_applicants:
          - nonprofit_501c3
        focus_areas:
          - community health
          - technology access
        geographic_scope:
          - Washington State
        populations_served:
          - youth
        requires_501c3: true
        source_system: manual_inbox
        source_url: https://example.gov/x
        """,
    )
    grant = import_grant_from_manifest(manifest)
    assert grant.opportunity_type is OpportunityType.GOVERNMENT_GRANT
    assert grant.funder_type is FunderType.FEDERAL_AGENCY
    assert grant.title == "Community Health Technology Grant"
    assert grant.eligible_applicants == [EligibleApplicantType.NONPROFIT_501C3]
    assert grant.award_ceiling == 250_000
    assert grant.stage is GrantStage.OPEN  # default
    assert grant.source_system is SourceSystemType.MANUAL_INBOX
    # id derived from funder + FON
    assert grant.id
    assert grant.raw_source_reference == str(manifest)


def test_import_missing_required_field_raises(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest,
        """
        opportunity_type: government_grant
        funder_type: federal_agency
        program_name: X
        title: Y
        """,
    )
    with pytest.raises(GrantImportError, match="funder_name"):
        import_grant_from_manifest(manifest)


def test_import_rejects_contract_opportunity_type(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest,
        """
        opportunity_type: government_contract
        funder_name: X
        funder_type: state_agency
        program_name: X
        title: Y
        """,
    )
    with pytest.raises(GrantImportError, match="grant type"):
        import_grant_from_manifest(manifest)


def test_import_picks_up_local_files_as_documents(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest,
        """
        opportunity_type: foundation_grant
        funder_name: Test Foundation
        funder_type: private_foundation
        program_name: Program
        title: Title
        """,
    )
    # Simulated PDF alongside the manifest.
    (tmp_path / "nofo.pdf").write_bytes(b"%PDF-1.4 fake")
    grant = import_grant_from_manifest(manifest)
    names = {d.name for d in grant.documents}
    assert "nofo.pdf" in names


def test_import_datetime_string_parses_to_utc(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest,
        """
        opportunity_type: government_grant
        funder_name: A
        funder_type: federal_agency
        program_name: P
        title: T
        full_proposal_due_at: "2026-12-31T23:59:00"
        """,
    )
    grant = import_grant_from_manifest(manifest)
    assert grant.full_proposal_due_at is not None
    assert grant.full_proposal_due_at.tzinfo is not None


def test_import_rejects_missing_file(tmp_path):
    with pytest.raises(GrantImportError, match="Manifest not found"):
        import_grant_from_manifest(tmp_path / "does-not-exist.yaml")
