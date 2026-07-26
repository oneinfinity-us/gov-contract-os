"""Grant domain models.

Deliberately does NOT inherit from the existing procurement `Opportunity`
model. A grant's semantics (funder vs. procurement agency, eligibility gates,
LOI stage, cost share, ALN/CFDA codes, etc.) are different enough that
sharing fields via inheritance would leak procurement concepts into grant
logic (or vice versa). A future refactor can factor out a `BaseOpportunity`
if the shared surface grows; for now, explicit separation.

The unified layer where both live together is `OpportunityType` (see
`gov_contract_os.core.types`), used at the reporting/CLI seam.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from enum import StrEnum

from pydantic import BaseModel, Field

from gov_contract_os.core.types import GRANT_TYPES, OpportunityType
from gov_contract_os.models.opportunity import Document, SourceSystemType


class FunderType(StrEnum):
    FEDERAL_AGENCY = "federal_agency"
    STATE_AGENCY = "state_agency"
    LOCAL_GOVERNMENT = "local_government"
    TRIBAL = "tribal"
    PRIVATE_FOUNDATION = "private_foundation"
    CORPORATE_FOUNDATION = "corporate_foundation"
    CORPORATE_CSR = "corporate_csr"
    COMMUNITY_FOUNDATION = "community_foundation"
    INTERMEDIARY = "intermediary"
    OTHER = "other"


class EligibleApplicantType(StrEnum):
    NONPROFIT_501C3 = "nonprofit_501c3"
    NONPROFIT_OTHER = "nonprofit_other"
    EDUCATIONAL_INSTITUTION = "educational_institution"
    TRIBAL = "tribal"
    LOCAL_GOVERNMENT = "local_government"
    STATE_GOVERNMENT = "state_government"
    FEDERAL_AGENCY = "federal_agency"
    INDIVIDUAL = "individual"
    FOR_PROFIT_SMALL_BUSINESS = "for_profit_small_business"
    # Some programs allow non-eligible applicants to apply via a fiscal sponsor;
    # scoring treats this as CONDITIONAL, not eligible.
    FISCAL_SPONSOR_ELIGIBLE = "fiscal_sponsor_eligible"
    OTHER = "other"


class GrantStage(StrEnum):
    FORECAST = "forecast"  # announced but not yet open
    LOI_OPEN = "loi_open"  # letter of intent stage
    OPEN = "open"  # main proposal window open
    CLOSED = "closed"
    AWARDED = "awarded"
    ARCHIVED = "archived"


class GrantOpportunity(BaseModel):
    id: str
    opportunity_type: OpportunityType

    funder_name: str
    funder_type: FunderType
    program_name: str
    funding_opportunity_number: str | None = None  # FON / ALN / CFDA / grant ID
    title: str
    description: str | None = None
    stage: GrantStage = GrantStage.OPEN

    # Key dates
    posted_at: dt.datetime | None = None
    loi_due_at: dt.datetime | None = None
    full_proposal_due_at: dt.datetime | None = None
    award_notification_at: dt.datetime | None = None
    project_start_at: dt.datetime | None = None
    project_end_at: dt.datetime | None = None

    # Funding envelope
    award_ceiling: float | None = None
    award_floor: float | None = None
    total_program_funding: float | None = None
    expected_awards_count: int | None = None
    cost_share_required: bool | None = None
    cost_share_percent: float | None = None
    indirect_cost_limit_percent: float | None = None
    currency: str = "USD"

    # Matching signals
    eligible_applicants: list[EligibleApplicantType] = Field(default_factory=list)
    focus_areas: list[str] = Field(default_factory=list)
    geographic_scope: list[str] = Field(default_factory=list)
    populations_served: list[str] = Field(default_factory=list)
    cfda_or_aln_codes: list[str] = Field(default_factory=list)

    # Hard gates
    requires_501c3: bool | None = None
    requires_sam_registration: bool | None = None
    invitation_only: bool = False
    letter_of_inquiry_required: bool = False
    preapplication_required: bool = False
    mandatory_requirements: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    reporting_requirements: list[str] = Field(default_factory=list)
    evaluation_requirements: list[str] = Field(default_factory=list)

    # Metadata
    source_system: SourceSystemType
    source_url: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    documents: list[Document] = Field(default_factory=list)

    discovered_at: dt.datetime
    last_checked_at: dt.datetime
    content_hash: str | None = None
    raw_source_reference: str | None = None

    def model_post_init(self, __context) -> None:  # noqa: D401
        """Validate that opportunity_type is one of the grant types."""
        if self.opportunity_type not in GRANT_TYPES:
            raise ValueError(
                f"GrantOpportunity requires opportunity_type in "
                f"{sorted(t.value for t in GRANT_TYPES)}; got {self.opportunity_type.value!r}"
            )

    @staticmethod
    def dedupe_key(
        funder_name: str,
        funding_opportunity_number: str | None,
        source_url: str | None,
        title: str,
        full_proposal_due_at: dt.datetime | None,
    ) -> str:
        funder_key = funder_name.strip().lower()
        if funding_opportunity_number:
            return f"{funder_key}::{funding_opportunity_number.strip().lower()}"
        normalized_title = " ".join(title.strip().lower().split())
        due = full_proposal_due_at.isoformat() if full_proposal_due_at else ""
        return f"{funder_key}::{(source_url or '').strip().lower()}::{normalized_title}::{due}"

    @staticmethod
    def build_id(
        funder_name: str,
        funding_opportunity_number: str | None,
        source_url: str | None,
        title: str,
        full_proposal_due_at: dt.datetime | None,
    ) -> str:
        key = GrantOpportunity.dedupe_key(
            funder_name, funding_opportunity_number, source_url, title, full_proposal_due_at
        )
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]

    def compute_content_hash(self) -> str:
        payload = "|".join(
            [
                self.title or "",
                self.description or "",
                self.stage.value,
                str(self.full_proposal_due_at or ""),
                str(self.award_ceiling or ""),
                str(self.award_floor or ""),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Eligibility result
# ---------------------------------------------------------------------------


class EligibilityStatus(StrEnum):
    ELIGIBLE = "eligible"
    CONDITIONAL = "conditional"  # eligible if action is taken (register with SAM, partner, etc.)
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"  # not enough info in either grant or nonprofit profile to decide


class EligibilityCheck(BaseModel):
    label: str
    # True = passes, False = fails hard, None = cannot determine / needs info
    passed: bool | None
    detail: str
    source: str  # "grant" | "nonprofit_profile" | "missing" | "system"


class EligibilityResult(BaseModel):
    status: EligibilityStatus
    checks: list[EligibilityCheck] = Field(default_factory=list)
    hard_failures: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    conditional_actions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Analysis / recommendation
# ---------------------------------------------------------------------------


class GrantFitLevel(StrEnum):
    IMMEDIATE_ACTION = "immediate_action"  # 85-100
    STRONG_CANDIDATE = "strong_candidate"  # 70-84
    MONITOR = "monitor"  # 50-69
    DO_NOT_APPLY = "do_not_apply"  # 0-49


class GrantRecommendation(StrEnum):
    APPLY = "apply"
    APPLY_WITH_PARTNER = "apply_with_partner"
    SEEK_FISCAL_SPONSOR = "seek_fiscal_sponsor"
    REQUEST_CLARIFICATION = "request_clarification"
    MONITOR = "monitor"
    DO_NOT_APPLY = "do_not_apply"


class GrantAnalysis(BaseModel):
    """Level-1 analysis output for one (grant, nonprofit) pair.

    `nonprofit_slug` is required and part of the primary key: the same grant
    could be evaluated against multiple nonprofits, and the answers differ.
    """

    grant_id: str
    nonprofit_slug: str

    eligibility: EligibilityResult

    # Score is None when the grant is INELIGIBLE (per design: don't score
    # ineligible grants - they shouldn't compete against eligible ones in
    # ranked reports).
    fit_score: int | None = Field(default=None, ge=0, le=100)
    fit_level: GrantFitLevel | None = None
    recommendation: GrantRecommendation

    matched_criteria: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)

    requires_human_review: bool = True
    requires_advanced_model: bool = False
    analysis_version: str = "0.1.0"

    @staticmethod
    def fit_level_for_score(score: int) -> GrantFitLevel:
        if score >= 85:
            return GrantFitLevel.IMMEDIATE_ACTION
        if score >= 70:
            return GrantFitLevel.STRONG_CANDIDATE
        if score >= 50:
            return GrantFitLevel.MONITOR
        return GrantFitLevel.DO_NOT_APPLY
