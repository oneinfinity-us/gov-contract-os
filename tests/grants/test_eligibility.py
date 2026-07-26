from __future__ import annotations

import datetime as dt

import pytest

from gov_contract_os.grants.eligibility import check_grant_eligibility
from gov_contract_os.grants.models import EligibilityStatus, EligibleApplicantType
from gov_contract_os.organizations import InvalidOrganizationContextError


def test_eligible_when_all_gates_pass(make_grant, nonprofit_profile, now):
    grant = make_grant()
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.ELIGIBLE
    assert result.hard_failures == []


def test_ineligible_when_grant_requires_501c3_but_nonprofit_is_not(
    make_grant, nonprofit_profile, now
):
    grant = make_grant(requires_501c3=True)
    other = nonprofit_profile.model_copy(update={"tax_status": "501(c)(6)"})
    result = check_grant_eligibility(grant, other, now=now)
    assert result.status is EligibilityStatus.INELIGIBLE
    assert any("501(c)(3)" in f for f in result.hard_failures)


def test_ineligible_when_geographic_scope_does_not_overlap(
    make_grant, nonprofit_profile, now
):
    grant = make_grant(geographic_scope=["California", "Oregon"])
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.INELIGIBLE
    assert any("geographic" in f.lower() for f in result.hard_failures)


def test_eligible_when_grant_national_scope(make_grant, nonprofit_profile, now):
    grant = make_grant(geographic_scope=["National"])
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.ELIGIBLE


def test_ineligible_when_invitation_only(make_grant, nonprofit_profile, now):
    grant = make_grant(invitation_only=True)
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.INELIGIBLE


def test_ineligible_when_deadline_passed(make_grant, nonprofit_profile, now):
    grant = make_grant(full_proposal_due_at=now - dt.timedelta(days=1))
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.INELIGIBLE


def test_conditional_when_deadline_too_close(make_grant, nonprofit_profile, now):
    grant = make_grant(full_proposal_due_at=now + dt.timedelta(days=3))
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.CONDITIONAL
    assert any("3 days" in a for a in result.conditional_actions)


def test_conditional_when_fiscal_sponsor_path_exists(make_grant, nonprofit_profile, now):
    # Grant requires an entity type our nonprofit is not, but fiscal-sponsor is allowed.
    grant = make_grant(
        eligible_applicants=[
            EligibleApplicantType.EDUCATIONAL_INSTITUTION,
            EligibleApplicantType.FISCAL_SPONSOR_ELIGIBLE,
        ]
    )
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.CONDITIONAL
    assert any("fiscal sponsor" in a.lower() for a in result.conditional_actions)


def test_conditional_when_sam_registration_missing(make_grant, nonprofit_profile, now):
    grant = make_grant(requires_sam_registration=True)
    nonprofit = nonprofit_profile.model_copy(update={"has_sam_registration": False})
    result = check_grant_eligibility(grant, nonprofit, now=now)
    assert result.status is EligibilityStatus.CONDITIONAL
    assert any("SAM.gov" in a for a in result.conditional_actions)


def test_ineligible_when_cost_share_exceeds_capacity(make_grant, nonprofit_profile, now):
    grant = make_grant(cost_share_required=True, cost_share_percent=50.0)
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.INELIGIBLE


def test_ineligible_when_entity_type_not_listed(make_grant, nonprofit_profile, now):
    grant = make_grant(
        eligible_applicants=[
            EligibleApplicantType.EDUCATIONAL_INSTITUTION,
            EligibleApplicantType.STATE_GOVERNMENT,
        ]
    )
    result = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert result.status is EligibilityStatus.INELIGIBLE


def test_identity_isolation_rejects_consulting_business(
    make_grant, consulting_profile, now
):
    grant = make_grant()
    with pytest.raises(InvalidOrganizationContextError):
        check_grant_eligibility(grant, consulting_profile, now=now)
