from __future__ import annotations

import datetime as dt

import pytest

from gov_contract_os.core.types import GRANT_TYPES, OpportunityType, is_grant_type
from gov_contract_os.grants.models import (
    EligibleApplicantType,
    FunderType,
    GrantAnalysis,
    GrantFitLevel,
    GrantOpportunity,
    GrantStage,
)
from gov_contract_os.models.opportunity import SourceSystemType


def test_grant_types_excludes_contracts():
    assert OpportunityType.GOVERNMENT_CONTRACT not in GRANT_TYPES
    assert OpportunityType.GOVERNMENT_GRANT in GRANT_TYPES
    assert OpportunityType.FOUNDATION_GRANT in GRANT_TYPES
    assert OpportunityType.CORPORATE_GRANT in GRANT_TYPES


def test_is_grant_type_helper():
    assert is_grant_type(OpportunityType.GOVERNMENT_GRANT) is True
    assert is_grant_type(OpportunityType.GOVERNMENT_CONTRACT) is False


def test_grant_opportunity_rejects_contract_type(now):
    with pytest.raises(ValueError, match="opportunity_type"):
        GrantOpportunity(
            id="x",
            opportunity_type=OpportunityType.GOVERNMENT_CONTRACT,
            funder_name="F",
            funder_type=FunderType.FEDERAL_AGENCY,
            program_name="P",
            title="T",
            source_system=SourceSystemType.MANUAL_INBOX,
            discovered_at=now,
            last_checked_at=now,
        )


def test_dedupe_key_prefers_funding_opportunity_number():
    key = GrantOpportunity.dedupe_key(
        funder_name="Federal Agency",
        funding_opportunity_number="ABC-2026-001",
        source_url="https://example.gov/x",
        title="Some Grant",
        full_proposal_due_at=None,
    )
    assert key == "federal agency::abc-2026-001"


def test_dedupe_key_fallback_uses_url_title_and_deadline():
    due = dt.datetime(2026, 12, 31, tzinfo=dt.UTC)
    key = GrantOpportunity.dedupe_key(
        funder_name="Some Foundation",
        funding_opportunity_number=None,
        source_url="https://example.org/Grant/1",
        title="  Program   Name  ",
        full_proposal_due_at=due,
    )
    assert key == f"some foundation::https://example.org/grant/1::program name::{due.isoformat()}"


def test_build_id_is_deterministic():
    id1 = GrantOpportunity.build_id("Agency", "GN-1", None, "T", None)
    id2 = GrantOpportunity.build_id("Agency", "GN-1", None, "Different", None)
    id3 = GrantOpportunity.build_id("Agency", "GN-2", None, "T", None)
    assert id1 == id2
    assert id1 != id3


def test_compute_content_hash_changes_with_stage(make_grant):
    grant = make_grant()
    original = grant.compute_content_hash()
    changed = grant.model_copy(update={"stage": GrantStage.CLOSED})
    assert changed.compute_content_hash() != original


def test_fit_level_boundaries():
    assert GrantAnalysis.fit_level_for_score(85) is GrantFitLevel.IMMEDIATE_ACTION
    assert GrantAnalysis.fit_level_for_score(84) is GrantFitLevel.STRONG_CANDIDATE
    assert GrantAnalysis.fit_level_for_score(70) is GrantFitLevel.STRONG_CANDIDATE
    assert GrantAnalysis.fit_level_for_score(69) is GrantFitLevel.MONITOR
    assert GrantAnalysis.fit_level_for_score(49) is GrantFitLevel.DO_NOT_APPLY


def test_eligible_applicant_types_include_fiscal_sponsor():
    assert EligibleApplicantType.FISCAL_SPONSOR_ELIGIBLE.value == "fiscal_sponsor_eligible"
