"""City of Seattle connector - parses the official public "Bids & Proposals" RSS feed.

Data source: https://thebuyline.seattle.gov/category/bids-and-proposals/feed/ - the
City's official WordPress-hosted procurement announcement blog, "The Buy Line". This
is a standard public RSS 2.0 feed, no login/auth required. Verified interactively on
2026-07-22 (see docs/data-sources.md).

Known limitations of this source (documented honestly rather than hidden):
- The feed only lists announcement posts; the *actual* solicitation lives on a
  separate procurement platform (either https://cityofseattle.bonfirehub.com or
  https://procurement.opengov.com/portal/seattle). Neither platform's public API
  has been verified, so we only capture the outbound link to it, not structured
  detail data from it.
- Due dates are embedded in free-text HTML inside the RSS <description> and are
  extracted with a best-effort regex + fuzzy date parse. Extraction can fail or be
  wrong for descriptions that don't follow the common "Due Date: <date>" phrasing.
  When extraction fails, due_at is left as None (scoring treats that neutrally).
- Due dates in the source text are in Pacific time but carry no machine-readable
  timezone; we store them as UTC, which can be off by several hours. Acceptable for
  our day-level scoring/report use, not for precise deadline reminders.
- Announcement-only posts (webinars, general notices) are filtered out heuristically:
  an item is only treated as a real Opportunity if we can find either a recognizable
  solicitation number (e.g. "TR0-6221", "RFP#6345") or a link out to one of the two
  known procurement platforms above. This filter can both over- and under-match.
- fetch_documents() is not implemented (no verified public document listing API).
"""

from __future__ import annotations

import datetime as dt
import html
import logging
import re
import warnings
import xml.etree.ElementTree as ET  # ElementTree types only; parsing uses defusedxml below.

import defusedxml.ElementTree as DET
from dateutil import parser as dateutil_parser
from dateutil.parser import UnknownTimezoneWarning

from gov_contract_os.collectors.base import Connector, ConnectorHealth, ConnectorHealthStatus
from gov_contract_os.collectors.http import PoliteHttpClient
from gov_contract_os.models.opportunity import (
    Document,
    Opportunity,
    OpportunityStatus,
    ProcurementType,
    SourceSystemType,
)
from gov_contract_os.normalizers.dates import parse_date

logger = logging.getLogger(__name__)

SOURCE_AGENCY = "City of Seattle"
RSS_URL = "https://thebuyline.seattle.gov/category/bids-and-proposals/feed/"

_STATUS_PREFIX_RE = re.compile(
    r"^(CLOSED|ARCHIVED|CANCELED|CANCELLED)[\s\u2010-\u2015-]*", re.IGNORECASE
)
_STATUS_PREFIX_MAP = {
    "closed": OpportunityStatus.CLOSED,
    "archived": OpportunityStatus.CLOSED,
    "canceled": OpportunityStatus.CANCELLED,
    "cancelled": OpportunityStatus.CANCELLED,
}

_INTERNAL_CODE_RE = re.compile(r"\b([A-Za-z]{2}\d-\d{2,6})\b")
_LABELED_CODE_RE = re.compile(r"(RFP|ITB|RFQ|RFI)\s*#\s*([A-Za-z0-9-]{2,20})", re.IGNORECASE)
_EXTERNAL_LINK_RE = re.compile(
    r"https://(?:cityofseattle\.bonfirehub\.com|procurement\.opengov\.com)[^\s\"'<>]+"
)
_DUE_DATE_WINDOW_RE = re.compile(r"due date[^:]*:\s*(.{0,60})", re.IGNORECASE)
_DUE_DATE_STOP_RE = re.compile(
    r"Pre-Bid|Microsoft Teams|Mandatory|Addendum|Click here|Meeting", re.IGNORECASE
)
# Pacific time abbreviations that dateutil doesn't recognize and would otherwise
# warn (soon: raise) about; stripped before parsing since we always normalize the
# result to UTC anyway (see module docstring - source timezone is only approximate).
_TZ_ABBREV_RE = re.compile(r"\b(?:PST|PDT|PT)\b\.?", re.IGNORECASE)


class CityOfSeattleConnector(Connector):
    source_agency = SOURCE_AGENCY

    def __init__(self, http_client: PoliteHttpClient | None = None) -> None:
        self._http = http_client or PoliteHttpClient()
        self._owns_http = http_client is None

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def discover(self) -> list[Opportunity]:
        response = self._http.get(RSS_URL)
        # Parse raw bytes (not response.text) so the XML declaration's own encoding
        # is honored instead of httpx's guessed text encoding. Use defusedxml to
        # block XXE / billion-laughs / DTD-retrieval attacks - see
        # https://docs.python.org/3/library/xml.html#xml-vulnerabilities
        root = DET.fromstring(response.content)
        now = dt.datetime.now(dt.UTC)

        opportunities = []
        skipped = 0
        for item in root.findall("./channel/item"):
            opportunity = self._item_to_opportunity(item, now)
            if opportunity is None:
                skipped += 1
                continue
            opportunities.append(opportunity)
        if skipped:
            logger.info(
                "city_of_seattle: skipped %d RSS item(s) that look like announcements, "
                "not solicitations",
                skipped,
            )
        return opportunities

    def _item_to_opportunity(self, item: ET.Element, now: dt.datetime) -> Opportunity | None:
        raw_title = (item.findtext("title") or "").strip()
        permalink = (item.findtext("link") or "").strip()
        pub_date_text = item.findtext("pubDate")
        description = html.unescape(item.findtext("description") or "").strip()
        categories = [c.text.strip() for c in item.findall("category") if c.text]

        status, title = _extract_status_and_title(raw_title)
        solicitation_number = _extract_solicitation_number(raw_title, categories)
        external_url = _extract_external_url(description)

        if not solicitation_number and not external_url:
            # No solicitation code and no link to a known procurement platform -
            # almost certainly a general announcement/webinar post, not a bid.
            return None

        due_at = _extract_due_date(description)
        source_url = external_url or permalink

        opportunity_id = Opportunity.build_id(
            source_agency=SOURCE_AGENCY,
            solicitation_number=solicitation_number,
            source_url=permalink,  # stable RSS permalink, used only when no number
            title=title,
            due_at=due_at,
        )
        opportunity = Opportunity(
            id=opportunity_id,
            source_agency=SOURCE_AGENCY,
            source_system=SourceSystemType.OFFICIAL_RSS,
            solicitation_number=solicitation_number,
            title=title,
            description=description or None,
            status=status,
            procurement_type=_infer_procurement_type(raw_title, categories),
            categories=categories,
            published_at=parse_date(pub_date_text),
            due_at=due_at,
            location="Seattle, WA",
            source_url=source_url,
            discovered_at=now,
            last_checked_at=now,
            raw_source_reference=f"thebuyline RSS guid={item.findtext('guid') or permalink}",
        )
        opportunity.content_hash = opportunity.compute_content_hash()
        return opportunity

    def fetch_details(self, opportunity: Opportunity) -> Opportunity:
        # The RSS feed already gives us everything we're going to get in one shot
        # (there is no separate, verified detail API) - just refresh the checked-at
        # timestamp rather than re-fetching the whole feed per item.
        updated = opportunity.model_copy(update={"last_checked_at": dt.datetime.now(dt.UTC)})
        updated.content_hash = updated.compute_content_hash()
        return updated

    def fetch_documents(self, opportunity: Opportunity) -> list[Document]:
        logger.info(
            "city_of_seattle: fetch_documents not implemented (no verified public "
            "document API); see source_url for the manual portal link: %s",
            opportunity.source_url,
        )
        return []

    def health_check(self) -> ConnectorHealth:
        now = dt.datetime.now(dt.UTC)
        try:
            response = self._http.get(RSS_URL)
            DET.fromstring(response.content)
        except ET.ParseError as exc:
            return ConnectorHealth(
                source_agency=SOURCE_AGENCY,
                status=ConnectorHealthStatus.DEGRADED,
                reason=f"RSS feed returned content that failed to parse as XML: {exc}",
                recommended_alternative=(
                    "Check https://thebuyline.seattle.gov/category/bids-and-proposals/feed/ "
                    "manually in a browser."
                ),
                manual_inbox_hint=(
                    "Download public solicitation PDFs and place them in "
                    "opportunities/inbox/, then run `python -m gov_contract_os rfp analyze "
                    "<file>`."
                ),
                checked_at=now,
            )
        except Exception as exc:  # noqa: BLE001 - health_check must never crash the CLI
            return ConnectorHealth(
                source_agency=SOURCE_AGENCY,
                status=ConnectorHealthStatus.UNAVAILABLE,
                reason=f"Could not reach the RSS feed: {exc}",
                recommended_alternative=(
                    "Check https://thebuyline.seattle.gov/category/bids-and-proposals/feed/ "
                    "manually, or https://procurement.opengov.com/portal/seattle."
                ),
                manual_inbox_hint=(
                    "Download public solicitation PDFs and place them in "
                    "opportunities/inbox/, then run `python -m gov_contract_os rfp analyze "
                    "<file>`."
                ),
                checked_at=now,
            )
        return ConnectorHealth(
            source_agency=SOURCE_AGENCY,
            status=ConnectorHealthStatus.OK,
            reason="RSS feed reachable and parsed successfully.",
            checked_at=now,
        )


def _extract_status_and_title(raw_title: str) -> tuple[OpportunityStatus, str]:
    match = _STATUS_PREFIX_RE.match(raw_title)
    if not match:
        return OpportunityStatus.OPEN, raw_title.strip()
    status = _STATUS_PREFIX_MAP.get(match.group(1).lower(), OpportunityStatus.UNKNOWN)
    remaining = raw_title[match.end() :].strip()
    return status, remaining or raw_title.strip()


def _extract_solicitation_number(raw_title: str, categories: list[str]) -> str | None:
    haystack = " ".join([raw_title, *categories])
    match = _INTERNAL_CODE_RE.search(haystack)
    if match:
        return match.group(1).upper()
    match = _LABELED_CODE_RE.search(haystack)
    if match:
        return f"{match.group(1).upper()}-{match.group(2).upper()}"
    return None


def _extract_external_url(description: str) -> str | None:
    match = _EXTERNAL_LINK_RE.search(description)
    if not match:
        return None
    return match.group(0).rstrip(").,;")


def _extract_due_date(description: str) -> dt.datetime | None:
    match = _DUE_DATE_WINDOW_RE.search(description)
    if not match:
        return None
    window = _DUE_DATE_STOP_RE.split(match.group(1))[0]
    window = _TZ_ABBREV_RE.sub("", window)
    try:
        with warnings.catch_warnings():
            # We force UTC below regardless of what dateutil infers, so an
            # unrecognized tzname token (e.g. "PST", or noise picked up by fuzzy
            # parsing) is expected and not worth surfacing as a runtime warning.
            warnings.simplefilter("ignore", category=UnknownTimezoneWarning)
            parsed = dateutil_parser.parse(window, fuzzy=True)
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed


def _infer_procurement_type(raw_title: str, categories: list[str]) -> ProcurementType:
    haystack = " ".join([raw_title, *categories]).upper()
    if "RFP" in haystack:
        return ProcurementType.RFP
    if "RFQ" in haystack:
        return ProcurementType.RFQ
    if "RFI" in haystack:
        return ProcurementType.RFI
    if "ITB" in haystack or "IFB" in haystack:
        return ProcurementType.IFB
    return ProcurementType.OTHER
