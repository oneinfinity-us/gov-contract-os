"""Unified connector interface every agency connector implements.

Connectors must ONLY use publicly accessible endpoints/pages and must never
attempt to bypass login, CAPTCHA, access control, rate limits, or paywalls -
see SECURITY.md. Every connector reports its own ConnectorHealth so one
agency's failure never blocks or crashes the others.
"""

from __future__ import annotations

import abc
import datetime as dt
from enum import StrEnum

from pydantic import BaseModel

from gov_contract_os.models.opportunity import Document, Opportunity


class ConnectorHealthStatus(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    NOT_IMPLEMENTED = "not_implemented"


class ConnectorHealth(BaseModel):
    source_agency: str
    status: ConnectorHealthStatus
    reason: str
    recommended_alternative: str | None = None
    manual_inbox_hint: str | None = None
    checked_at: dt.datetime


class Connector(abc.ABC):
    """Interface every agency connector must implement."""

    source_agency: str

    @abc.abstractmethod
    def discover(self) -> list[Opportunity]:
        """Return currently listed opportunities (summary-level fields only)."""

    @abc.abstractmethod
    def fetch_details(self, opportunity: Opportunity) -> Opportunity:
        """Return a copy of `opportunity` enriched with full detail fields."""

    @abc.abstractmethod
    def fetch_documents(self, opportunity: Opportunity) -> list[Document]:
        """Return document metadata (name/url) for an opportunity.

        Must NOT download unrelated/arbitrary attachments - metadata only.
        """

    @abc.abstractmethod
    def health_check(self) -> ConnectorHealth:
        """Report whether this connector currently works and, if not, why."""
