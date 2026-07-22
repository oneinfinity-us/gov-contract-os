"""Placeholder connector for Washington State procurement.

NOT YET IMPLEMENTED. The public procurement portal (Washington's Electronic
Business Solution / WEBS, run by the Department of Enterprise Services) has
not been researched/verified for automated access in this MVP round - see
docs/data-sources.md for research status.
"""

from __future__ import annotations

import datetime as dt

from gov_contract_os.collectors.base import Connector, ConnectorHealth, ConnectorHealthStatus
from gov_contract_os.models.opportunity import Document, Opportunity

SOURCE_AGENCY = "Washington State"

_NOT_IMPLEMENTED_MSG = (
    f"{SOURCE_AGENCY} connector is not implemented yet - see docs/data-sources.md"
)


class WashingtonStateConnector(Connector):
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
                "Connector not implemented yet. Washington's public procurement portal "
                "(WEBS, https://des.wa.gov) has not been researched/verified in this round - "
                "unconfirmed whether it offers a public API, RSS, or data download."
            ),
            recommended_alternative=(
                "Check https://des.wa.gov (search 'WEBS') manually for open solicitations; "
                "confirm ToS/robots.txt before any future automation."
            ),
            manual_inbox_hint=(
                "Download public solicitation PDFs and place them in opportunities/inbox/, "
                "then run `python -m gov_contract_os rfp analyze <file>`."
            ),
            checked_at=dt.datetime.now(dt.UTC),
        )
