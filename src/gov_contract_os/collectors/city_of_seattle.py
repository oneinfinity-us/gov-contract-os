"""Placeholder connector for City of Seattle procurement.

NOT YET IMPLEMENTED (round 1), but partially researched: the City's Purchasing
& Contracting page (https://www.seattle.gov/purchasing-and-contracting/purchasing)
points at:
  - A third-party procurement portal: OpenGov
    (https://procurement.opengov.com/portal/seattle) - the current public bid
    listing UI. Needs further research on whether OpenGov exposes a public API
    or export for this tenant.
  - A public RSS feed for solicitations: "Purchasing Solicitations RSS Feed"
    at http://thebuyline.seattle.gov/category/bids-and-proposals/feed/
    - this is likely the fastest real connector to build next (official RSS,
    highest priority per SECURITY.md), but its feed item structure has not
    been parsed/verified yet.
See docs/data-sources.md for details and next steps.
"""

from __future__ import annotations

import datetime as dt

from gov_contract_os.collectors.base import Connector, ConnectorHealth, ConnectorHealthStatus
from gov_contract_os.models.opportunity import Document, Opportunity

SOURCE_AGENCY = "City of Seattle"

_NOT_IMPLEMENTED_MSG = (
    f"{SOURCE_AGENCY} connector is not implemented yet - see docs/data-sources.md"
)


class CityOfSeattleConnector(Connector):
    source_agency = SOURCE_AGENCY

    def discover(self) -> list[Opportunity]:
        raise NotImplementedError(_NOT_IMPLEMENTED_MSG)

    def fetch_details(self, opportunity: Opportunity) -> Opportunity:
        raise NotImplementedError(_NOT_IMPLEMENTED_MSG)

    def fetch_documents(self, opportunity: Opportunity) -> list[Document]:
        raise NotImplementedError(_NOT_IMPLEMENTED_MSG)

    def health_check(self) -> ConnectorHealth:
        return ConnectorHealth(
            source_agency=SOURCE_AGENCY,
            status=ConnectorHealthStatus.NOT_IMPLEMENTED,
            reason=(
                "Connector not implemented yet. Identified two candidate public "
                "sources but neither has been parsed/verified: (1) OpenGov procurement "
                "portal at procurement.opengov.com/portal/seattle, (2) an official RSS "
                "feed at thebuyline.seattle.gov/category/bids-and-proposals/feed/."
            ),
            recommended_alternative=(
                "Check https://procurement.opengov.com/portal/seattle?departmentId=6237&"
                "status=open manually, or subscribe to the RSS feed at "
                "http://thebuyline.seattle.gov/category/bids-and-proposals/feed/."
            ),
            manual_inbox_hint=(
                "Download public solicitation PDFs and place them in opportunities/inbox/, "
                "then run `python -m gov_contract_os rfp analyze <file>`."
            ),
            checked_at=dt.datetime.now(dt.UTC),
        )
