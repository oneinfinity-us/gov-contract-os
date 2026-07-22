"""Port of Seattle connector - the first REAL, working connector for this MVP round.

Data source: the Port of Seattle "VendorConnect" procurement portal
(https://hosting.portseattle.org/sops/) exposes a public, unauthenticated OData
API that backs its own guest "Search Current/Past Solicitations" feature. This
connector calls that same public JSON API directly - no login, CAPTCHA, or rate
limit is bypassed; this is the documented public guest search surfaced as JSON.
Verified interactively on 2026-07-21 (see docs/data-sources.md for the request
shapes and field mapping notes).
"""

from __future__ import annotations

import datetime as dt
import logging

from gov_contract_os.collectors.base import Connector, ConnectorHealth, ConnectorHealthStatus
from gov_contract_os.collectors.http import PoliteHttpClient
from gov_contract_os.models.opportunity import (
    Document,
    Opportunity,
    OpportunityStatus,
    ProcurementType,
    SourceSystemType,
)

logger = logging.getLogger(__name__)

SOURCE_AGENCY = "Port of Seattle"
API_BASE = "https://hosting.portseattle.org/sopsapi"
DETAIL_URL_TEMPLATE = "https://hosting.portseattle.org/sops/#/Solicitations/Detail/{id}"

_STATUS_MAP = {
    "open": OpportunityStatus.OPEN,
    "future": OpportunityStatus.FUTURE,
    "closed": OpportunityStatus.CLOSED,
    "awarded": OpportunityStatus.AWARDED,
    "cancelled": OpportunityStatus.CANCELLED,
}

_LIST_FILTER = (
    "DisplayFutureList eq false and "
    "(SolicitationStatus/Name eq 'Open' or SolicitationStatus/Name eq 'Future')"
)
_LIST_SELECT = "Id,ProcurementNumber,ProcurementTitle,BidDueDateTime"
_LIST_EXPAND = "SolicitationCategory($select=Name,Id),SolicitationStatus($select=Name,Id)"

_DETAIL_SELECT = (
    "BidDueDateTime,BidDueDateQuestionCutOffDateTime,CreatedOn,LastUpdatedOn,"
    "ProcurementNumber,ProcurementTitle,Description,EstimateQuarter,EstimateYear,"
    "EngineerEstimate,PortContact,PortContactPhone,PortContactEmail,AdvertisementDate,"
    "ShouldPubliclyDisplayPlanHolders,ShouldPubliclyDisplayDocuments,DisplayFutureList"
)
_DETAIL_EXPAND = "SolicitationStatus($select=Name),Department($select=Name)"


class PortOfSeattleConnector(Connector):
    source_agency = SOURCE_AGENCY

    def __init__(self, http_client: PoliteHttpClient | None = None) -> None:
        self._http = http_client or PoliteHttpClient()
        self._owns_http = http_client is None

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def discover(self) -> list[Opportunity]:
        now = dt.datetime.now(dt.UTC)
        params = {
            "$orderby": "SolicitationStatus/Name desc,BidDueDateTime desc",
            "$count": "true",
            "$filter": _LIST_FILTER,
            "$expand": _LIST_EXPAND,
            "$select": _LIST_SELECT,
        }
        response = self._http.get(f"{API_BASE}/Solicitations", params=params)
        payload = response.json()
        return [self._summary_to_opportunity(item, now) for item in payload.get("value", [])]

    def _summary_to_opportunity(self, item: dict, now: dt.datetime) -> Opportunity:
        solicitation_id = item.get("Id", "")
        solicitation_number = item.get("ProcurementNumber") or None
        title = item.get("ProcurementTitle") or "(untitled)"
        due_at = _parse_datetime(item.get("BidDueDateTime"))
        status_name = ((item.get("SolicitationStatus") or {}).get("Name") or "").lower()
        source_url = DETAIL_URL_TEMPLATE.format(id=solicitation_id)

        opportunity_id = Opportunity.build_id(
            source_agency=SOURCE_AGENCY,
            solicitation_number=solicitation_number,
            source_url=source_url,
            title=title,
            due_at=due_at,
        )
        opportunity = Opportunity(
            id=opportunity_id,
            source_agency=SOURCE_AGENCY,
            source_system=SourceSystemType.OFFICIAL_API,
            solicitation_number=solicitation_number,
            title=title,
            status=_STATUS_MAP.get(status_name, OpportunityStatus.UNKNOWN),
            due_at=due_at,
            source_url=source_url,
            discovered_at=now,
            last_checked_at=now,
            raw_source_reference=f"sopsapi/Solicitations Id={solicitation_id}",
        )
        opportunity.content_hash = opportunity.compute_content_hash()
        return opportunity

    def fetch_details(self, opportunity: Opportunity) -> Opportunity:
        solicitation_id = _extract_id_from_source_url(opportunity.source_url)
        if not solicitation_id:
            logger.warning("Cannot fetch details without a solicitation id: %s", opportunity.title)
            return opportunity

        params = {
            "$filter": f"Id eq {solicitation_id}",
            "$select": _DETAIL_SELECT,
            "$expand": _DETAIL_EXPAND,
        }
        response = self._http.get(f"{API_BASE}/Solicitations", params=params)
        payload = response.json().get("value", [])
        if not payload:
            logger.warning("No detail record found for solicitation id %s", solicitation_id)
            return opportunity
        detail = payload[0]

        now = dt.datetime.now(dt.UTC)
        status_name = ((detail.get("SolicitationStatus") or {}).get("Name") or "").lower()
        department = (detail.get("Department") or {}).get("Name")

        updated = opportunity.model_copy(
            update={
                "title": detail.get("ProcurementTitle") or opportunity.title,
                "description": detail.get("Description") or None,
                "status": _STATUS_MAP.get(status_name, opportunity.status),
                "procurement_type": ProcurementType.OTHER,
                "categories": [department] if department else opportunity.categories,
                "published_at": _parse_datetime(detail.get("AdvertisementDate")),
                "questions_due_at": _parse_datetime(detail.get("BidDueDateQuestionCutOffDateTime")),
                "due_at": _parse_datetime(detail.get("BidDueDateTime")) or opportunity.due_at,
                "contact_name": detail.get("PortContact") or None,
                "contact_email": detail.get("PortContactEmail") or None,
                "location": "Seattle, WA",
                "last_checked_at": now,
            }
        )
        updated.content_hash = updated.compute_content_hash()
        return updated

    def fetch_documents(self, opportunity: Opportunity) -> list[Document]:
        # VendorConnect's detail view exposes a "ShouldPubliclyDisplayDocuments" flag,
        # but this MVP round has not identified/verified the public documents API
        # endpoint yet, so document metadata is not fetched automatically.
        # Manual workaround: download public documents from opportunity.source_url
        # and drop them into opportunities/inbox/ for `rfp analyze`.
        logger.info(
            "fetch_documents not yet implemented for Port of Seattle connector (opportunity=%s)",
            opportunity.id,
        )
        return []

    def health_check(self) -> ConnectorHealth:
        now = dt.datetime.now(dt.UTC)
        try:
            response = self._http.get(
                f"{API_BASE}/Solicitations", params={"$top": "1", "$count": "true"}
            )
            response.json()
        except Exception as exc:  # noqa: BLE001 - report any failure, don't crash the run
            return ConnectorHealth(
                source_agency=SOURCE_AGENCY,
                status=ConnectorHealthStatus.UNAVAILABLE,
                reason=f"Request to VendorConnect OData API failed: {exc}",
                recommended_alternative=(
                    "Check https://hosting.portseattle.org/sops/ manually as a guest."
                ),
                manual_inbox_hint=(
                    "Drop relevant public solicitation PDFs into opportunities/inbox/."
                ),
                checked_at=now,
            )
        return ConnectorHealth(
            source_agency=SOURCE_AGENCY,
            status=ConnectorHealthStatus.OK,
            reason="VendorConnect public Solicitations OData endpoint responded successfully.",
            checked_at=now,
        )


def _parse_datetime(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError:
        return None


def _extract_id_from_source_url(source_url: str | None) -> str | None:
    if not source_url or "/Detail/" not in source_url:
        return None
    return source_url.rsplit("/Detail/", 1)[-1]
