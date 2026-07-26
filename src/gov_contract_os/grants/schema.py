"""SQLAlchemy ORM tables for grants.

Grant rows live in separate tables from procurement `opportunities` /
`analyses`. Same SQLite file, distinct namespaces. `grant_analyses` uses a
composite (grant_id, nonprofit_slug) primary key because the same grant may
be evaluated against multiple nonprofits in the future.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from gov_contract_os.storage.schema import Base


class GrantOpportunityRecord(Base):
    __tablename__ = "grant_opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    opportunity_type: Mapped[str] = mapped_column(String, index=True)

    funder_name: Mapped[str] = mapped_column(String, index=True)
    funder_type: Mapped[str] = mapped_column(String)
    program_name: Mapped[str] = mapped_column(String)
    funding_opportunity_number: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage: Mapped[str] = mapped_column(String, index=True)

    posted_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    loi_due_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    full_proposal_due_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    award_notification_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    project_start_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    project_end_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    award_ceiling: Mapped[float | None] = mapped_column(Float, nullable=True)
    award_floor: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_program_funding: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_awards_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_share_required: Mapped[bool | None] = mapped_column(nullable=True)
    cost_share_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    indirect_cost_limit_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")

    eligible_applicants: Mapped[list] = mapped_column(JSON, default=list)
    focus_areas: Mapped[list] = mapped_column(JSON, default=list)
    geographic_scope: Mapped[list] = mapped_column(JSON, default=list)
    populations_served: Mapped[list] = mapped_column(JSON, default=list)
    cfda_or_aln_codes: Mapped[list] = mapped_column(JSON, default=list)

    requires_501c3: Mapped[bool | None] = mapped_column(nullable=True)
    requires_sam_registration: Mapped[bool | None] = mapped_column(nullable=True)
    invitation_only: Mapped[bool] = mapped_column(default=False)
    letter_of_inquiry_required: Mapped[bool] = mapped_column(default=False)
    preapplication_required: Mapped[bool] = mapped_column(default=False)
    mandatory_requirements: Mapped[list] = mapped_column(JSON, default=list)
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    reporting_requirements: Mapped[list] = mapped_column(JSON, default=list)
    evaluation_requirements: Mapped[list] = mapped_column(JSON, default=list)

    source_system: Mapped[str] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String, nullable=True)
    documents: Mapped[list] = mapped_column(JSON, default=list)

    discovered_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    last_checked_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)


class GrantAnalysisRecord(Base):
    __tablename__ = "grant_analyses"

    grant_id: Mapped[str] = mapped_column(String, primary_key=True)
    nonprofit_slug: Mapped[str] = mapped_column(String, primary_key=True)

    eligibility_status: Mapped[str] = mapped_column(String, index=True)
    eligibility_checks: Mapped[list] = mapped_column(JSON, default=list)
    eligibility_hard_failures: Mapped[list] = mapped_column(JSON, default=list)
    eligibility_missing_information: Mapped[list] = mapped_column(JSON, default=list)
    eligibility_conditional_actions: Mapped[list] = mapped_column(JSON, default=list)

    fit_score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    fit_level: Mapped[str | None] = mapped_column(String, nullable=True)
    recommendation: Mapped[str] = mapped_column(String, index=True)

    matched_criteria: Mapped[list] = mapped_column(JSON, default=list)
    gaps: Mapped[list] = mapped_column(JSON, default=list)
    risks: Mapped[list] = mapped_column(JSON, default=list)
    next_actions: Mapped[list] = mapped_column(JSON, default=list)

    requires_human_review: Mapped[bool] = mapped_column(default=True)
    requires_advanced_model: Mapped[bool] = mapped_column(default=False)
    analysis_version: Mapped[str] = mapped_column(String, default="0.1.0")
