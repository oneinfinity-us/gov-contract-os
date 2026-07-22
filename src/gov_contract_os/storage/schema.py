"""SQLAlchemy ORM schema - the SQLite-backed store for Opportunity/Analysis rows.

Field-for-field mirror of gov_contract_os.models so nothing is silently dropped
on the way in/out of the database. JSON columns hold list/dict fields since
SQLite has no native array/JSON column type of its own.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class OpportunityRecord(Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_agency: Mapped[str] = mapped_column(String, index=True)
    source_system: Mapped[str] = mapped_column(String)
    solicitation_number: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, index=True)
    procurement_type: Mapped[str] = mapped_column(String)
    categories: Mapped[list] = mapped_column(JSON, default=list)

    published_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    questions_due_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    prebid_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    award_date: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    estimated_value_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_value_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="USD")

    location: Mapped[str | None] = mapped_column(String, nullable=True)
    prime_or_sub_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    small_business_goal: Mapped[str | None] = mapped_column(String, nullable=True)
    wmbe_goal: Mapped[str | None] = mapped_column(String, nullable=True)
    mandatory_certifications: Mapped[list] = mapped_column(JSON, default=list)
    mandatory_requirements: Mapped[list] = mapped_column(JSON, default=list)

    contact_name: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    documents: Mapped[list] = mapped_column(JSON, default=list)

    discovered_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    last_checked_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    content_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    opportunity_id: Mapped[str] = mapped_column(String, primary_key=True)
    fit_score: Mapped[int] = mapped_column(Integer)
    fit_level: Mapped[str] = mapped_column(String)
    recommended_role: Mapped[str] = mapped_column(String)

    matched_capabilities: Mapped[list] = mapped_column(JSON, default=list)
    capability_gaps: Mapped[list] = mapped_column(JSON, default=list)
    mandatory_requirement_risks: Mapped[list] = mapped_column(JSON, default=list)
    next_actions: Mapped[list] = mapped_column(JSON, default=list)

    requires_human_review: Mapped[bool] = mapped_column(default=True)
    requires_advanced_model: Mapped[bool] = mapped_column(default=False)
    analysis_version: Mapped[str] = mapped_column(String, default="0.1.0")
