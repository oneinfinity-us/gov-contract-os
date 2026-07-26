"""Hard eligibility gate for grant opportunities.

Runs BEFORE scoring. If the nonprofit is ineligible, we do not compute a
fit score at all - an ineligible grant with high mission alignment should
never appear in a "top matches" list.

All rules are deterministic and read from the GrantOpportunity + the
nonprofit OrganizationProfile. Missing information produces CONDITIONAL /
UNKNOWN, not silent passes.
"""

from __future__ import annotations

import datetime as dt

from gov_contract_os.grants.models import (
    EligibilityCheck,
    EligibilityResult,
    EligibilityStatus,
    EligibleApplicantType,
    GrantOpportunity,
)
from gov_contract_os.organizations import (
    OrganizationProfile,
    ensure_grant_context,
)


def _normalize_geo(values: list[str]) -> set[str]:
    return {v.strip().lower() for v in values if v and v.strip()}


_NATIONAL_TOKENS = frozenset(
    {"us", "u.s.", "usa", "united states", "national", "nationwide", "all states"}
)


def _geographic_overlap(grant_geo: list[str], org_geo: list[str]) -> bool:
    g = _normalize_geo(grant_geo)
    o = _normalize_geo(org_geo)
    if g & _NATIONAL_TOKENS:
        return True
    return bool(g & o)


def _determine_status(
    checks: list[EligibilityCheck], hard_failures: list[str]
) -> EligibilityStatus:
    if hard_failures:
        return EligibilityStatus.INELIGIBLE
    if not checks:
        return EligibilityStatus.UNKNOWN
    if any(c.passed is None for c in checks):
        return EligibilityStatus.CONDITIONAL
    return EligibilityStatus.ELIGIBLE


def check_grant_eligibility(
    grant: GrantOpportunity,
    nonprofit: OrganizationProfile,
    now: dt.datetime | None = None,
) -> EligibilityResult:
    """Return an EligibilityResult for a (grant, nonprofit) pair.

    Enforces the identity-isolation rule (SECURITY.md): the profile MUST be
    a nonprofit context or this raises before any check runs.
    """
    ensure_grant_context(nonprofit)
    now = now or dt.datetime.now(dt.UTC)

    checks: list[EligibilityCheck] = []
    hard_failures: list[str] = []
    missing_information: list[str] = []
    conditional_actions: list[str] = []

    # --- 1. 501(c)(3) requirement --------------------------------------------
    if grant.requires_501c3 is True:
        if nonprofit.is_501c3():
            checks.append(
                EligibilityCheck(
                    label="501(c)(3) status",
                    passed=True,
                    detail="Nonprofit is a 501(c)(3).",
                    source="nonprofit_profile",
                )
            )
        elif nonprofit.tax_status:
            hard_failures.append(
                f"Grant requires 501(c)(3); nonprofit tax_status is "
                f"{nonprofit.tax_status!r}."
            )
            checks.append(
                EligibilityCheck(
                    label="501(c)(3) status",
                    passed=False,
                    detail=f"Nonprofit tax_status is {nonprofit.tax_status!r}, not 501(c)(3).",
                    source="nonprofit_profile",
                )
            )
        else:
            missing_information.append("Nonprofit tax_status is not set.")
            checks.append(
                EligibilityCheck(
                    label="501(c)(3) status",
                    passed=None,
                    detail="Nonprofit tax_status missing from profile.",
                    source="missing",
                )
            )

    # --- 2. Eligible applicant type ------------------------------------------
    if grant.eligible_applicants:
        applicable: set[EligibleApplicantType] = set()
        if nonprofit.is_501c3():
            applicable.add(EligibleApplicantType.NONPROFIT_501C3)
            applicable.add(EligibleApplicantType.NONPROFIT_OTHER)
        elif nonprofit.is_nonprofit():
            applicable.add(EligibleApplicantType.NONPROFIT_OTHER)

        overlap = set(grant.eligible_applicants) & applicable
        if overlap:
            checks.append(
                EligibilityCheck(
                    label="Eligible applicant type",
                    passed=True,
                    detail=(
                        "Nonprofit type matches grant's eligible applicants: "
                        + ", ".join(sorted(t.value for t in overlap))
                    ),
                    source="grant",
                )
            )
        elif EligibleApplicantType.FISCAL_SPONSOR_ELIGIBLE in grant.eligible_applicants:
            conditional_actions.append(
                "Apply via fiscal sponsor - nonprofit's direct entity type is "
                "not listed but grant allows fiscal sponsors."
            )
            checks.append(
                EligibilityCheck(
                    label="Eligible applicant type",
                    passed=None,
                    detail="Direct entity type not eligible, but fiscal sponsor path exists.",
                    source="grant",
                )
            )
        else:
            hard_failures.append(
                "Nonprofit's entity type is not in grant's eligible_applicants: "
                + ", ".join(t.value for t in grant.eligible_applicants)
            )
            checks.append(
                EligibilityCheck(
                    label="Eligible applicant type",
                    passed=False,
                    detail=(
                        "Grant eligible applicants: "
                        + ", ".join(t.value for t in grant.eligible_applicants)
                    ),
                    source="grant",
                )
            )

    # --- 3. Geographic eligibility -------------------------------------------
    if grant.geographic_scope:
        if not nonprofit.service_geographies:
            missing_information.append(
                "Nonprofit service_geographies not specified in profile."
            )
            checks.append(
                EligibilityCheck(
                    label="Geographic eligibility",
                    passed=None,
                    detail="Cannot compare - nonprofit service_geographies is empty.",
                    source="missing",
                )
            )
        elif _geographic_overlap(grant.geographic_scope, nonprofit.service_geographies):
            checks.append(
                EligibilityCheck(
                    label="Geographic eligibility",
                    passed=True,
                    detail=(
                        "Grant scope "
                        + ", ".join(grant.geographic_scope)
                        + " overlaps with nonprofit service area."
                    ),
                    source="grant",
                )
            )
        else:
            hard_failures.append(
                "Grant geographic scope does not overlap with nonprofit's service area."
            )
            checks.append(
                EligibilityCheck(
                    label="Geographic eligibility",
                    passed=False,
                    detail=(
                        f"Grant scope: {grant.geographic_scope}; "
                        f"nonprofit service area: {nonprofit.service_geographies}."
                    ),
                    source="grant",
                )
            )

    # --- 4. Invitation-only programs -----------------------------------------
    if grant.invitation_only:
        hard_failures.append("Program is invitation-only.")
        checks.append(
            EligibilityCheck(
                label="Invitation-only",
                passed=False,
                detail="Grant is invitation-only; nonprofit must be invited.",
                source="grant",
            )
        )

    # --- 5. SAM.gov registration (federal grants) ----------------------------
    if grant.requires_sam_registration:
        if nonprofit.has_sam_registration is True:
            checks.append(
                EligibilityCheck(
                    label="SAM.gov registration",
                    passed=True,
                    detail="Nonprofit is registered on SAM.gov.",
                    source="nonprofit_profile",
                )
            )
        elif nonprofit.has_sam_registration is False:
            conditional_actions.append(
                "Register on SAM.gov (can take several weeks) before submitting."
            )
            checks.append(
                EligibilityCheck(
                    label="SAM.gov registration",
                    passed=None,
                    detail="Nonprofit is not currently registered on SAM.gov.",
                    source="nonprofit_profile",
                )
            )
        else:
            missing_information.append(
                "Nonprofit SAM.gov registration status not set in profile."
            )
            checks.append(
                EligibilityCheck(
                    label="SAM.gov registration",
                    passed=None,
                    detail="Registration status unknown.",
                    source="missing",
                )
            )

    # --- 6. Deadline feasibility ---------------------------------------------
    deadline = grant.full_proposal_due_at or grant.loi_due_at
    if deadline is not None:
        days_left = (deadline - now).days
        if days_left < 0:
            hard_failures.append(f"Deadline already passed ({deadline.date().isoformat()}).")
            checks.append(
                EligibilityCheck(
                    label="Deadline feasibility",
                    passed=False,
                    detail=f"Due {deadline.date().isoformat()} ({-days_left} days ago).",
                    source="grant",
                )
            )
        elif days_left < 7:
            conditional_actions.append(
                f"Deadline in {days_left} days - assess whether a quality application is feasible."
            )
            checks.append(
                EligibilityCheck(
                    label="Deadline feasibility",
                    passed=None,
                    detail=f"Only {days_left} days until deadline.",
                    source="grant",
                )
            )
        else:
            checks.append(
                EligibilityCheck(
                    label="Deadline feasibility",
                    passed=True,
                    detail=f"{days_left} days until deadline.",
                    source="grant",
                )
            )

    # --- 7. Cost share vs. nonprofit's stated capacity -----------------------
    if grant.cost_share_required:
        required_pct = grant.cost_share_percent
        max_capacity = nonprofit.max_cost_share_percent
        if max_capacity is None:
            missing_information.append(
                "Nonprofit max_cost_share_percent not specified in profile."
            )
            checks.append(
                EligibilityCheck(
                    label="Cost share",
                    passed=None,
                    detail=(
                        f"Grant requires cost share"
                        + (f" of {required_pct}%" if required_pct is not None else "")
                        + "; nonprofit cost share capacity unknown."
                    ),
                    source="missing",
                )
            )
        elif required_pct is not None and required_pct > max_capacity:
            hard_failures.append(
                f"Grant requires {required_pct}% cost share; nonprofit max is {max_capacity}%."
            )
            checks.append(
                EligibilityCheck(
                    label="Cost share",
                    passed=False,
                    detail=f"Required {required_pct}% exceeds capacity {max_capacity}%.",
                    source="grant",
                )
            )
        else:
            checks.append(
                EligibilityCheck(
                    label="Cost share",
                    passed=True,
                    detail=(
                        f"Cost share requirement"
                        + (f" ({required_pct}%)" if required_pct is not None else "")
                        + " within nonprofit capacity."
                    ),
                    source="grant",
                )
            )

    status = _determine_status(checks, hard_failures)
    return EligibilityResult(
        status=status,
        checks=checks,
        hard_failures=hard_failures,
        missing_information=missing_information,
        conditional_actions=conditional_actions,
    )
