"""Shared fixtures for grants tests."""

from __future__ import annotations

import datetime as dt

import pytest

from gov_contract_os.core.types import OpportunityType
from gov_contract_os.grants.models import (
    EligibleApplicantType,
    FunderType,
    GrantOpportunity,
    GrantStage,
)
from gov_contract_os.models.opportunity import SourceSystemType
from gov_contract_os.organizations import OrganizationProfile, OrganizationType


@pytest.fixture
def now() -> dt.datetime:
    return dt.datetime(2026, 7, 25, 12, 0, tzinfo=dt.UTC)


@pytest.fixture
def make_grant(now):
    def _make(**overrides) -> GrantOpportunity:
        defaults = dict(
            id="test-grant-id",
            opportunity_type=OpportunityType.GOVERNMENT_GRANT,
            funder_name="Test Agency",
            funder_type=FunderType.FEDERAL_AGENCY,
            program_name="Community Health Innovation",
            funding_opportunity_number="TEST-2026-001",
            title="Community Health Technology Grant",
            description="Supports nonprofits improving community health via technology.",
            stage=GrantStage.OPEN,
            full_proposal_due_at=now + dt.timedelta(days=45),
            award_ceiling=250_000.0,
            award_floor=50_000.0,
            eligible_applicants=[EligibleApplicantType.NONPROFIT_501C3],
            focus_areas=["community health", "technology access"],
            geographic_scope=["Washington State", "King County"],
            populations_served=["underrepresented youth"],
            requires_501c3=True,
            requires_sam_registration=False,
            source_system=SourceSystemType.MANUAL_INBOX,
            source_url="https://example.gov/grants/test",
            discovered_at=now,
            last_checked_at=now,
        )
        defaults.update(overrides)
        return GrantOpportunity(**defaults)

    return _make


@pytest.fixture
def nonprofit_profile() -> OrganizationProfile:
    return OrganizationProfile(
        slug="test-nonprofit",
        type=OrganizationType.NONPROFIT,
        legal_name="Test Nonprofit",
        tax_status="501(c)(3)",
        focus_areas=["technology access", "workforce development"],
        populations_served=["underrepresented youth"],
        service_geographies=["King County", "Washington State"],
        has_501c3_determination_letter=True,
        has_sam_registration=True,
        has_uei=True,
        has_audited_financials=True,
        has_board_list=True,
        has_nondiscrimination_policy=True,
        has_conflict_of_interest_policy=True,
        minimum_award=5_000,
        maximum_award=500_000,
        max_cost_share_percent=20.0,
    )


@pytest.fixture
def consulting_profile() -> OrganizationProfile:
    return OrganizationProfile(
        slug="consulting-business",
        type=OrganizationType.CONSULTING_BUSINESS,
        legal_name="Test Consulting LLC",
    )
