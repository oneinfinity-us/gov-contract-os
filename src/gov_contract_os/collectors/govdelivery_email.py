"""GovDelivery email-subscription connector - the third real connector.

DES (and many other WA public agencies) publishes bid opportunities through
GovDelivery (Granicus), a first-party government notification service. Instead
of scraping govdelivery.com, this connector consumes GovDelivery *emails* the
user has voluntarily subscribed to, delivered to their own mailbox. The
project reads that mailbox via IMAP with the user's own credentials.

Why this design:
  - GovDelivery is DES's officially advertised public notification channel
    (see the "Sign up for Contracts Connection / IT Contracts Focus" links on
    https://des.wa.gov/sell/bid-opportunities). Consuming those emails is
    zero-ambiguity re: platform ToS.
  - No web scraper needed against govdelivery.com or fortress.wa.gov (the
    authenticated WEBS side). We never touch WA's authenticated systems.
  - Same connector will pick up any *other* government agency the user
    subscribes to (King County, Seattle, etc. all use GovDelivery-family
    services), by inspecting the account slug in each email.

Read-only guarantees:
  - IMAP SELECT is done readonly=True so we cannot modify remote state.
  - We never mark messages read/unread, never move, never delete.
  - Passwords never appear in logs or commit history (see SECURITY.md).

Known limitations, documented up front rather than hidden:
  - The parser was written *before* the first real email arrived, based on
    GovDelivery's public template conventions. First-real-email fields (topic
    prefix formatting, exact From address, exact solicitation-link URL patterns
    in the body) will almost certainly need refinement - see TODO markers.
  - Due dates and solicitation numbers are extracted heuristically from
    free-text bodies. Missing extraction => the field stays None; scoring
    treats that neutrally.
  - fetch_documents() is intentionally not implemented (emails only reference
    external URLs; documents live on the underlying agency portal).
"""

from __future__ import annotations

import datetime as dt
import email
import email.header
import email.message
import email.utils
import imaplib
import logging
import re
import ssl
from collections.abc import Iterable
from typing import Protocol

from gov_contract_os.collectors.base import Connector, ConnectorHealth, ConnectorHealthStatus
from gov_contract_os.config import Settings, get_settings
from gov_contract_os.models.opportunity import (
    Document,
    Opportunity,
    OpportunityStatus,
    ProcurementType,
    SourceSystemType,
)

logger = logging.getLogger(__name__)

CONNECTOR_KEY = "govdelivery_email"
DEFAULT_SOURCE_AGENCY = "GovDelivery Subscription"

# GovDelivery's IMAP search - we filter on sender being any govdelivery.com
# subdomain (subscriptions.*, subscribe.*, or public.govdelivery.com etc.). The
# actual sender domains vary per government agency, so we cast a wide net and
# post-filter by header + body signals.
_GOVDELIVERY_SENDER_RE = re.compile(
    r"(?:@|<|\.)(?:[\w-]+\.)?govdelivery\.com\b|"
    r"(?:@|<|\.)subscribe\.des\.wa\.gov\b|"
    r"(?:@|<|\.)subscriptions\.des\.wa\.gov\b",
    re.IGNORECASE,
)

# Look for the GovDelivery account slug in the visible/hidden unsubscribe URL,
# which is *always* present in GovDelivery emails. Example:
#   https://public.govdelivery.com/accounts/WADES/subscribers/...
_ACCOUNT_SLUG_RE = re.compile(
    r"govdelivery\.com/accounts/([A-Z0-9_-]{2,40})/", re.IGNORECASE
)

# Map from GovDelivery account slug -> canonical `source_agency` string. Slugs
# that aren't in this table fall back to the slug itself (uppercased); noting
# this rather than defaulting to "Washington State" avoids mis-attributing a
# King County / Seattle email.
_ACCOUNT_SLUG_TO_AGENCY = {
    "WADES": "Washington State",
    "WAGOV": "Washington State",
}

# Solicitation-number patterns commonly used by WA agencies. Extend as
# real-email evidence lands. The lookahead forces the code group to contain
# at least one digit - keeps us from mis-capturing English words like
# "POSTED" after "RFP" in a subject line.
_LABELED_CODE_RE = re.compile(
    r"\b(RFP|RFQ|RFI|IFB|ITB|IDIQ|Solicitation|Contract)[\s#:-]*"
    r"(?=[A-Z0-9\-_./]*\d)([A-Z0-9][A-Z0-9\-_./]{2,30})\b",
    re.IGNORECASE,
)

# Best-effort "Due" phrase extractor. Kept intentionally simple; the real
# calibration happens once we see actual GovDelivery email bodies.
_DUE_DATE_WINDOW_RE = re.compile(
    r"(?:Due|Closes|Closing|Response deadline|Bid opens?)[^:]*:\s*(.{0,60})",
    re.IGNORECASE,
)

# Skip these link hosts when picking the "outbound" URL for source_url - they're
# GovDelivery infrastructure (unsubscribe/preferences pages), never the actual
# solicitation.
_INFRA_HOST_RE = re.compile(
    r"(?:^|//|@|\.)(?:public\.govdelivery\.com|subscriberhelp\.govdelivery\.com|"
    r"content\.govdelivery\.com|links\.govdelivery\.com|"
    r"subscriber\.govdelivery\.com)/",
    re.IGNORECASE,
)

_URL_RE = re.compile(r"https?://[^\s\"'<>)]+", re.IGNORECASE)


class MessageProvider(Protocol):
    """Anything that can hand out raw email bytes.

    Split from the connector itself so tests can bypass IMAP entirely by
    passing a canned in-memory provider.
    """

    def fetch_recent(self, since: dt.datetime) -> Iterable[bytes]:
        """Yield raw RFC-5322 message bytes for messages received on or after `since`."""


class ImapMessageProvider:
    """Real IMAP4_SSL-backed provider. Read-only. TLS with hostname verification."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        user: str,
        password: str,
        mailbox: str = "INBOX",
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._mailbox = mailbox

    def fetch_recent(self, since: dt.datetime) -> Iterable[bytes]:
        # Python's default context validates certs and hostnames; we do not
        # relax it. See https://docs.python.org/3/library/ssl.html
        context = ssl.create_default_context()
        # Cast the since date to IMAP's "d-Mon-yyyy" form (SEARCH SINCE
        # semantics are date-based, ignoring the time component).
        since_token = since.strftime("%d-%b-%Y")
        conn = imaplib.IMAP4_SSL(self._host, self._port, ssl_context=context)
        try:
            conn.login(self._user, self._password)
            typ, _ = conn.select(self._mailbox, readonly=True)
            if typ != "OK":
                raise RuntimeError(f"IMAP SELECT failed for mailbox={self._mailbox!r}")
            typ, data = conn.search(None, "SINCE", since_token)
            if typ != "OK":
                raise RuntimeError(f"IMAP SEARCH failed: {data!r}")
            id_blob = data[0] if data else b""
            message_ids = id_blob.split() if id_blob else []
            logger.info(
                "govdelivery_email: IMAP search returned %d message id(s) since %s",
                len(message_ids),
                since_token,
            )
            for msg_id in message_ids:
                typ, msg_data = conn.fetch(msg_id, "(BODY.PEEK[])")
                if typ != "OK" or not msg_data:
                    logger.warning(
                        "govdelivery_email: FETCH failed for id=%r; skipping", msg_id
                    )
                    continue
                for part in msg_data:
                    if isinstance(part, tuple) and len(part) >= 2 and isinstance(part[1], bytes):
                        yield part[1]
                        break
        finally:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 - close-time errors must not mask real ones
                pass
            try:
                conn.logout()
            except Exception:  # noqa: BLE001
                pass


class GovDeliveryEmailConnector(Connector):
    """Connector that reads bid-notification emails delivered by GovDelivery.

    The `source_agency` string on this connector is a placeholder; each
    parsed opportunity carries its own per-message agency derived from the
    GovDelivery account slug in the email body (WADES -> Washington State,
    KING_COUNTY -> King County, etc.).
    """

    source_agency = DEFAULT_SOURCE_AGENCY

    def __init__(
        self,
        settings: Settings | None = None,
        message_provider: MessageProvider | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._provider = message_provider

    def _credentials_ready(self) -> bool:
        s = self._settings
        return bool(s.govdelivery_imap_host and s.govdelivery_imap_user and s.govdelivery_imap_password)

    def _resolve_provider(self) -> MessageProvider:
        if self._provider is not None:
            return self._provider
        s = self._settings
        if not self._credentials_ready():
            raise RuntimeError(
                "govdelivery_email: IMAP credentials not configured. Set "
                "GCO_GOVDELIVERY_IMAP_HOST, GCO_GOVDELIVERY_IMAP_USER, and "
                "GCO_GOVDELIVERY_IMAP_PASSWORD in .env (see .env.example)."
            )
        assert s.govdelivery_imap_host is not None
        assert s.govdelivery_imap_user is not None
        assert s.govdelivery_imap_password is not None
        return ImapMessageProvider(
            host=s.govdelivery_imap_host,
            port=s.govdelivery_imap_port,
            user=s.govdelivery_imap_user,
            password=s.govdelivery_imap_password,
            mailbox=s.govdelivery_imap_mailbox,
        )

    def discover(self) -> list[Opportunity]:
        provider = self._resolve_provider()
        now = dt.datetime.now(dt.UTC)
        since = now - dt.timedelta(days=self._settings.govdelivery_lookback_days)

        opportunities: list[Opportunity] = []
        seen_ids: set[str] = set()
        skipped_non_govdelivery = 0
        skipped_unparseable = 0
        for raw in provider.fetch_recent(since):
            try:
                message = email.message_from_bytes(raw)
            except Exception:  # noqa: BLE001 - one malformed email must not kill the batch
                logger.exception("govdelivery_email: failed to parse RFC-5322 bytes; skipping")
                skipped_unparseable += 1
                continue
            if not _looks_like_govdelivery(message):
                skipped_non_govdelivery += 1
                continue
            opportunity = _parse_message(message, discovered_at=now)
            if opportunity is None:
                skipped_unparseable += 1
                continue
            if opportunity.id in seen_ids:
                continue
            seen_ids.add(opportunity.id)
            opportunities.append(opportunity)

        if skipped_non_govdelivery:
            logger.info(
                "govdelivery_email: skipped %d non-GovDelivery message(s) in mailbox",
                skipped_non_govdelivery,
            )
        if skipped_unparseable:
            logger.info(
                "govdelivery_email: skipped %d unparseable message(s)",
                skipped_unparseable,
            )
        return opportunities

    def fetch_details(self, opportunity: Opportunity) -> Opportunity:
        # Everything we're going to get is already in the email. The underlying
        # agency portal (WEBS, OpenGov, etc.) is a different connector's job.
        updated = opportunity.model_copy(update={"last_checked_at": dt.datetime.now(dt.UTC)})
        updated.content_hash = updated.compute_content_hash()
        return updated

    def fetch_documents(self, opportunity: Opportunity) -> list[Document]:
        logger.info(
            "govdelivery_email: fetch_documents not implemented (emails only cite "
            "portal URLs); see source_url for the manual link: %s",
            opportunity.source_url,
        )
        return []

    def health_check(self) -> ConnectorHealth:
        now = dt.datetime.now(dt.UTC)
        # An injected provider (test path) means health is defined as "the
        # provider is reachable"; skip credential checks in that case.
        if self._provider is None and not self._credentials_ready():
            return ConnectorHealth(
                source_agency=DEFAULT_SOURCE_AGENCY,
                status=ConnectorHealthStatus.NOT_IMPLEMENTED,
                reason=(
                    "IMAP credentials not configured. Set GCO_GOVDELIVERY_IMAP_HOST, "
                    "GCO_GOVDELIVERY_IMAP_USER, and GCO_GOVDELIVERY_IMAP_PASSWORD "
                    "in .env (see .env.example) after subscribing to the desired "
                    "GovDelivery topics."
                ),
                recommended_alternative=(
                    "Subscribe to at least one GovDelivery topic and forward those "
                    "emails to a dedicated mailbox this project can read. See "
                    "docs/data-sources.md for the recommended WA DES topics "
                    "(WADES_109 = Contracts Connection, WADES_4 = IT Contracts Focus)."
                ),
                manual_inbox_hint=(
                    "Until this is configured, forward or download GovDelivery "
                    "notices manually and drop them under opportunities/inbox/."
                ),
                checked_at=now,
            )
        try:
            # Any exception here (including IMAP auth failures / network errors)
            # is caught below and mapped to a health status - never re-raised.
            provider = self._resolve_provider()
            # A cheap probe: fetch the last day only. The provider iterator is
            # lazy, so consuming zero items is nearly free.
            iterator = iter(provider.fetch_recent(now - dt.timedelta(days=1)))
            next(iterator, None)  # actually pull once to force network connect
        except Exception as exc:  # noqa: BLE001 - health_check must not crash the CLI
            return ConnectorHealth(
                source_agency=DEFAULT_SOURCE_AGENCY,
                status=ConnectorHealthStatus.UNAVAILABLE,
                reason=f"Could not reach the IMAP mailbox: {exc}",
                recommended_alternative=(
                    "Verify the IMAP host/port/user/password in .env and that the "
                    "mailbox account permits app-specific passwords / third-party "
                    "IMAP access (e.g. Gmail requires an app password)."
                ),
                manual_inbox_hint=(
                    "Forward GovDelivery notices manually to opportunities/inbox/ "
                    "until the IMAP connection is fixed."
                ),
                checked_at=now,
            )
        return ConnectorHealth(
            source_agency=DEFAULT_SOURCE_AGENCY,
            status=ConnectorHealthStatus.OK,
            reason="IMAP mailbox reachable and searchable.",
            checked_at=now,
        )


def _looks_like_govdelivery(message: email.message.Message) -> bool:
    """Return True iff the message's headers or body clearly identify GovDelivery.

    We intentionally accept messages that only *match on body content* because
    some agencies rewrite the visible From/Sender header even when GovDelivery
    is the actual sender. False positives here are cheap: they'll just fail to
    parse into a real solicitation and be skipped downstream.
    """
    header_haystack = " ".join(
        [
            _decode_header(message.get("From")),
            _decode_header(message.get("Sender")),
            _decode_header(message.get("Return-Path")),
            _decode_header(message.get("List-Unsubscribe")),
            _decode_header(message.get("List-ID")),
        ]
    )
    if _GOVDELIVERY_SENDER_RE.search(header_haystack):
        return True
    body_preview = _extract_text_body(message)[:4000]
    return bool(_ACCOUNT_SLUG_RE.search(body_preview))


def _parse_message(
    message: email.message.Message, *, discovered_at: dt.datetime
) -> Opportunity | None:
    """Parse a single GovDelivery email into an Opportunity, or None if too thin.

    Returns None if the message lacks BOTH a subject and any body content - we
    don't want to store placeholder rows.
    """
    subject = _decode_header(message.get("Subject")).strip()
    body_text = _extract_text_body(message).strip()
    if not subject and not body_text:
        return None

    account_slug = _extract_account_slug(message, body_text)
    source_agency = _ACCOUNT_SLUG_TO_AGENCY.get(
        (account_slug or "").upper(), (account_slug or DEFAULT_SOURCE_AGENCY).upper()
    )

    solicitation_number = _extract_solicitation_number(f"{subject}\n{body_text}")
    external_url = _extract_outbound_url(body_text)
    due_at = _extract_due_date(body_text)
    published_at = _parse_email_date(message.get("Date"))

    title = _strip_topic_prefix(subject) or "(untitled GovDelivery notice)"
    message_id = (message.get("Message-ID") or message.get("Message-Id") or "").strip() or None

    opportunity_id = Opportunity.build_id(
        source_agency=source_agency,
        solicitation_number=solicitation_number,
        source_url=external_url,
        title=title,
        due_at=due_at,
    )
    opportunity = Opportunity(
        id=opportunity_id,
        source_agency=source_agency,
        source_system=SourceSystemType.OFFICIAL_EMAIL_SUBSCRIPTION,
        solicitation_number=solicitation_number,
        title=title,
        description=body_text or None,
        status=OpportunityStatus.UNKNOWN,
        procurement_type=_infer_procurement_type(f"{subject} {body_text}"),
        categories=[account_slug] if account_slug else [],
        published_at=published_at,
        due_at=due_at,
        location=_infer_location(source_agency),
        source_url=external_url,
        discovered_at=discovered_at,
        last_checked_at=discovered_at,
        raw_source_reference=(
            f"govdelivery message-id={message_id}" if message_id else "govdelivery email"
        ),
    )
    opportunity.content_hash = opportunity.compute_content_hash()
    return opportunity


def _decode_header(value: str | None) -> str:
    if not value:
        return ""
    try:
        parts = email.header.decode_header(value)
    except Exception:  # noqa: BLE001 - malformed headers must not raise
        return value
    decoded: list[str] = []
    for chunk, charset in parts:
        if isinstance(chunk, bytes):
            try:
                decoded.append(chunk.decode(charset or "utf-8", errors="replace"))
            except (LookupError, TypeError):
                decoded.append(chunk.decode("utf-8", errors="replace"))
        else:
            decoded.append(chunk)
    return "".join(decoded).strip()


def _extract_text_body(message: email.message.Message) -> str:
    """Prefer the text/plain part; fall back to a naive HTML strip.

    Not a full HTML parser - GovDelivery's HTML is templated but not
    complex; we just need enough plain text to extract URLs, ref numbers,
    and phrases like "Due:". A more accurate HTML parse would require
    beautifulsoup4 as a new dep, which we're avoiding until we've seen
    real emails and know we need it.
    """
    text_plain: list[str] = []
    text_html: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                continue
            content_type = part.get_content_type()
            payload = _decode_part(part)
            if content_type == "text/plain":
                text_plain.append(payload)
            elif content_type == "text/html":
                text_html.append(payload)
    else:
        content_type = message.get_content_type()
        payload = _decode_part(message)
        if content_type == "text/plain":
            text_plain.append(payload)
        elif content_type == "text/html":
            text_html.append(payload)
        else:
            text_plain.append(payload)

    if any(t.strip() for t in text_plain):
        return "\n\n".join(text_plain)
    combined_html = "\n\n".join(text_html)
    return _strip_html_tags(combined_html)


def _decode_part(part: email.message.Message) -> str:
    try:
        raw = part.get_payload(decode=True)
    except Exception:  # noqa: BLE001
        raw = None
    if raw is None:
        payload = part.get_payload()
        return payload if isinstance(payload, str) else ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return raw.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return raw.decode("utf-8", errors="replace")


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_HTML_WHITESPACE_RE = re.compile(r"[\t\r ]+")
# Pull href values out of anchor tags before we destroy tag structure -
# otherwise the URL disappears with the tag.
_HREF_RE = re.compile(
    r"<a\s+[^>]*href\s*=\s*['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE
)


def _strip_html_tags(html_text: str) -> str:
    if not html_text:
        return ""
    # Very intentionally naive; enough to expose URLs and phrases for later
    # regex extraction. Not safe for rendering.
    exposed = _HREF_RE.sub(r" \1 ", html_text)
    without_tags = _HTML_TAG_RE.sub(" ", exposed)
    return _HTML_WHITESPACE_RE.sub(" ", without_tags).strip()


def _extract_account_slug(message: email.message.Message, body_text: str) -> str | None:
    for header_name in ("List-Unsubscribe", "List-ID", "From", "Sender"):
        match = _ACCOUNT_SLUG_RE.search(_decode_header(message.get(header_name)))
        if match:
            return match.group(1).upper()
    match = _ACCOUNT_SLUG_RE.search(body_text)
    if match:
        return match.group(1).upper()
    return None


def _extract_solicitation_number(text: str) -> str | None:
    match = _LABELED_CODE_RE.search(text)
    if not match:
        return None
    number = match.group(2).strip(".,;:").upper()
    if len(number) < 3:
        return None
    return number


def _extract_outbound_url(body_text: str) -> str | None:
    for url in _URL_RE.findall(body_text):
        cleaned = url.rstrip(").,;\"'")
        if _INFRA_HOST_RE.search(cleaned):
            continue
        return cleaned
    return None


def _extract_due_date(body_text: str) -> dt.datetime | None:
    match = _DUE_DATE_WINDOW_RE.search(body_text)
    if not match:
        return None
    window = match.group(1).strip()
    # Local import: dateutil is already a project dep via other collectors,
    # but keeping the import narrow makes this file's dep surface visible.
    import warnings

    from dateutil import parser as dateutil_parser
    from dateutil.parser import UnknownTimezoneWarning

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UnknownTimezoneWarning)
            parsed = dateutil_parser.parse(window, fuzzy=True)
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed


def _parse_email_date(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    parsed = email.utils.parsedate_to_datetime(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed


def _strip_topic_prefix(subject: str) -> str:
    # GovDelivery subjects often lead with a topic name and a separator, e.g.
    #   "IT Contracts Focus - New solicitation posted"
    # We drop the first "<prefix> - " if that prefix looks like a topic label
    # (letters/spaces/&), keeping the substantive title.
    match = re.match(r"^([A-Za-z0-9&' ]{3,50})\s+[-\u2013\u2014:]\s+(.+)$", subject)
    if not match:
        return subject
    return match.group(2).strip()


def _infer_procurement_type(text: str) -> ProcurementType:
    upper = text.upper()
    if "IDIQ" in upper:
        return ProcurementType.IDIQ
    if "RFP" in upper:
        return ProcurementType.RFP
    if "RFQ" in upper:
        return ProcurementType.RFQ
    if "RFI" in upper:
        return ProcurementType.RFI
    if "IFB" in upper or "ITB" in upper:
        return ProcurementType.IFB
    return ProcurementType.OTHER


def _infer_location(source_agency: str) -> str | None:
    # Deliberately conservative: only fill in a state when we're sure.
    if source_agency == "Washington State":
        return "Washington, USA"
    if source_agency == "King County":
        return "King County, WA"
    if source_agency == "City of Seattle":
        return "Seattle, WA"
    if source_agency == "City of Bellevue":
        return "Bellevue, WA"
    return None
