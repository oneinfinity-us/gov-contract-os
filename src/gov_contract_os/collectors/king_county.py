"""Placeholder connector for King County procurement.

NOT YET IMPLEMENTED. King County's public procurement portal/platform has not
been researched/verified for automated access in this MVP round - see
docs/data-sources.md for research status.
"""

from __future__ import annotations

import datetime as dt

from gov_contract_os.collectors.base import Connector, ConnectorHealth, ConnectorHealthStatus
from gov_contract_os.models.opportunity import Document, Opportunity

SOURCE_AGENCY = "King County"

_NOT_IMPLEMENTED_MSG = (
    f"{SOURCE_AGENCY} connector is not implemented yet - see docs/data-sources.md"
)


class KingCountyConnector(Connector):
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
                "Connector not implemented yet. King County's public procurement "
                "portal/platform has not been researched/verified in this round."
            ),
            recommended_alternative=(
                "Check King County's official procurement pages (e.g. "
                "kingcounty.gov procurement/contracts section) manually; confirm the "
                "actual platform, ToS, and robots.txt before any future automation."
            ),
            manual_inbox_hint=(
                "Download public solicitation PDFs and place them in opportunities/inbox/, "
                "then run `python -m gov_contract_os rfp analyze <file>`."
            ),
            checked_at=dt.datetime.now(dt.UTC),
        )
