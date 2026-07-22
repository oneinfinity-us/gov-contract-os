"""Unified Opportunity data model.

Every connector/parser/normalizer must produce `Opportunity` objects so the rest
of the system (storage, scoring, analyzers, reports) never has to know which
agency or source system the data came from.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class OpportunityStatus(StrEnum):
    OPEN = "open"
    FUTURE = "future"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ProcurementType(StrEnum):
    RFP = "rfp"
    RFQ = "rfq"
    IFB = "ifb"
    RFI = "rfi"
    IDIQ = "idiq"
    SMALL_WORKS_ROSTER = "small_works_roster"
    GOODS_AND_SERVICES = "goods_and_services"
    CONSTRUCTION = "construction"
    CONSULTING = "consulting"
    OTHER = "other"


class SourceSystemType(StrEnum):
    """How the data was obtained - drives priority/trust and helps triage failures.

    Priority order (highest to lowest), per SECURITY.md / connector rules:
    official API > official RSS/Atom > official data download >
    official public search page > plain HTML parse > browser automation.
    """

    OFFICIAL_API = "official_api"
    OFFICIAL_RSS = "official_rss"
    OFFICIAL_DATA_DOWNLOAD = "official_data_download"
    OFFICIAL_SEARCH_PAGE = "official_search_page"
    HTML_SCRAPE = "html_scrape"
    BROWSER_AUTOMATION = "browser_automation"
    MANUAL_INBOX = "manual_inbox"


class Document(BaseModel):
    """Metadata about a solicitation document. Content is NOT downloaded here."""

    name: str
    url: str | None = None
    document_type: str | None = None
    published_at: datetime | None = None


class Opportunity(BaseModel):
    id: str
    source_agency: str
    source_system: SourceSystemType
    solicitation_number: str | None = None
    title: str
    description: str | None = None
    status: OpportunityStatus = OpportunityStatus.UNKNOWN
    procurement_type: ProcurementType = ProcurementType.OTHER
    categories: list[str] = Field(default_factory=list)

    published_at: datetime | None = None
    questions_due_at: datetime | None = None
    prebid_at: datetime | None = None
    due_at: datetime | None = None
    award_date: datetime | None = None

    estimated_value_min: float | None = None
    estimated_value_max: float | None = None
    currency: str = "USD"

    location: str | None = None
    prime_or_sub_notes: str | None = None
    small_business_goal: str | None = None
    wmbe_goal: str | None = None
    mandatory_certifications: list[str] = Field(default_factory=list)
    mandatory_requirements: list[str] = Field(default_factory=list)

    contact_name: str | None = None
    contact_email: str | None = None
    source_url: str | None = None
    documents: list[Document] = Field(default_factory=list)

    discovered_at: datetime
    last_checked_at: datetime
    content_hash: str | None = None
    raw_source_reference: str | None = None

    @staticmethod
    def dedupe_key(
        source_agency: str,
        solicitation_number: str | None,
        source_url: str | None,
        title: str,
        due_at: datetime | None,
    ) -> str:
        """Stable de-dup key.

        Prefers agency + solicitation_number; falls back to
        source_url + normalized title + due date when no solicitation number
        is available.
        """
        agency_key = source_agency.strip().lower()
        if solicitation_number:
            return f"{agency_key}::{solicitation_number.strip().lower()}"
        normalized_title = " ".join(title.strip().lower().split())
        due = due_at.isoformat() if due_at else ""
        return f"{agency_key}::{(source_url or '').strip().lower()}::{normalized_title}::{due}"

    @staticmethod
    def build_id(
        source_agency: str,
        solicitation_number: str | None,
        source_url: str | None,
        title: str,
        due_at: datetime | None,
    ) -> str:
        """Deterministic primary key derived from the dedupe key."""
        key = Opportunity.dedupe_key(source_agency, solicitation_number, source_url, title, due_at)
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]

    def compute_content_hash(self) -> str:
        """Hash of the fields that matter for "did this opportunity change" checks."""
        payload = "|".join(
            [
                self.title or "",
                self.description or "",
                self.status.value,
                str(self.due_at or ""),
                str(self.estimated_value_min or ""),
                str(self.estimated_value_max or ""),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
