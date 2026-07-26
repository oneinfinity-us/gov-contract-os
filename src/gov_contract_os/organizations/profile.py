"""Organization profile schema + loader.

An organization profile is loaded from a YAML file under `organizations/<slug>/`
and drives all matching/eligibility logic. Sensitive fields (EIN, banking, etc.)
MUST NOT be committed - the schema deliberately uses `..._recorded` booleans
so the profile can attest "we have this on file elsewhere" without storing
the actual value in the repo.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class OrganizationType(StrEnum):
    CONSULTING_BUSINESS = "consulting_business"
    NONPROFIT = "nonprofit"


class InvalidOrganizationContextError(RuntimeError):
    """Raised when a grant operation is attempted under a non-nonprofit context,
    or a procurement operation under a non-business context (per SECURITY.md's
    identity isolation rule).
    """


class ProgramSummary(BaseModel):
    name: str
    description: str | None = None
    annual_participants: int | None = None
    annual_budget: float | None = None
    outcomes: list[str] = Field(default_factory=list)


class OrganizationProfile(BaseModel):
    """A single legal entity's public-facing profile.

    Nonprofit-specific fields are optional so the same schema can hold either
    a consulting business or a nonprofit. Grants code will only accept a
    profile whose `type == NONPROFIT`.
    """

    slug: str
    type: OrganizationType
    legal_name: str
    dba_name: str | None = None
    incorporation_state: str | None = None
    year_founded: int | None = None

    # Nonprofit-specific descriptive fields (unused for consulting business).
    tax_status: str | None = None  # e.g. "501(c)(3)"
    mission_statement: str | None = None
    focus_areas: list[str] = Field(default_factory=list)
    populations_served: list[str] = Field(default_factory=list)
    service_geographies: list[str] = Field(default_factory=list)
    programs: list[ProgramSummary] = Field(default_factory=list)

    # Attestations: "we have this on file", NOT the sensitive value itself.
    # See SECURITY.md - EINs, banking info, board member PII stay out of git.
    has_501c3_determination_letter: bool | None = None
    has_sam_registration: bool | None = None
    has_uei: bool | None = None
    has_grants_gov_registration: bool | None = None
    has_audited_financials: bool | None = None
    has_board_list: bool | None = None
    has_nondiscrimination_policy: bool | None = None
    has_conflict_of_interest_policy: bool | None = None

    # Funding preferences (what the org will/won't chase).
    minimum_award: float | None = None
    maximum_award: float | None = None
    accepts_reimbursement_grants: bool | None = None
    accepts_matching_grants: bool | None = None
    max_cost_share_percent: float | None = None

    # Where the org's public-facing docs live (relative to repo root).
    documents_dir: str | None = None

    def is_nonprofit(self) -> bool:
        return self.type is OrganizationType.NONPROFIT

    def is_501c3(self) -> bool:
        return self.is_nonprofit() and (self.tax_status or "").strip().lower() in (
            "501(c)(3)",
            "501c3",
        )


def load_organization_profile(path: Path) -> OrganizationProfile:
    """Load an OrganizationProfile from a YAML file.

    Missing/empty files raise. This is a boundary function; callers rely on
    a valid profile being present before running downstream logic.
    """
    if not path.exists():
        raise FileNotFoundError(f"Organization profile not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Organization profile must be a mapping: {path}")
    return OrganizationProfile.model_validate(raw)


def ensure_grant_context(profile: OrganizationProfile) -> None:
    """Enforce the SECURITY.md identity-isolation rule for grant operations.

    Raises InvalidOrganizationContextError if the caller tries to run grant
    logic under a consulting-business (or otherwise non-nonprofit) context.
    """
    if not profile.is_nonprofit():
        raise InvalidOrganizationContextError(
            f"Grant operations require a nonprofit organization context, but "
            f"got type={profile.type.value!r} (slug={profile.slug!r}). "
            f"See SECURITY.md - grant applications must not reuse consulting-"
            f"business past performance, certifications, or credentials."
        )
