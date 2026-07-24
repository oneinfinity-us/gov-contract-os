"""Tests for the GovDelivery email connector.

Tests inject a fake MessageProvider so no real IMAP connection is needed.
Every raw email is a synthetic RFC-5322 blob constructed from public
GovDelivery template conventions - the parser is deliberately defensive so
these fixtures exercise the extraction paths without pretending to be a
byte-for-byte replay of a real WADES email.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from email.message import EmailMessage

import pytest

from gov_contract_os.collectors.govdelivery_email import (
    DEFAULT_SOURCE_AGENCY,
    GovDeliveryEmailConnector,
    MessageProvider,
)
from gov_contract_os.config import Settings
from gov_contract_os.models.opportunity import (
    OpportunityStatus,
    ProcurementType,
    SourceSystemType,
)


class _FakeProvider:
    """Handed to the connector so IMAP is never touched in tests."""

    def __init__(self, messages: list[bytes]) -> None:
        self._messages = messages
        self.since_calls: list[dt.datetime] = []

    def fetch_recent(self, since: dt.datetime) -> Iterable[bytes]:
        self.since_calls.append(since)
        return list(self._messages)


class _RaisingProvider:
    def fetch_recent(self, since: dt.datetime) -> Iterable[bytes]:  # noqa: ARG002
        raise RuntimeError("simulated IMAP failure")


def _make_email(
    *,
    subject: str,
    from_addr: str = "WA DES <no-reply@subscribe.des.wa.gov>",
    body: str,
    date_header: str = "Fri, 24 Jul 2026 15:30:00 -0700",
    list_unsubscribe: str | None = (
        "<https://public.govdelivery.com/accounts/WADES/subscribers/"
        "abcd1234/preferences>"
    ),
    include_html_part: bool = False,
    message_id: str = "<sample-1@subscribe.des.wa.gov>",
) -> bytes:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = "vendor@example.com"
    msg["Date"] = date_header
    msg["Message-ID"] = message_id
    if list_unsubscribe:
        msg["List-Unsubscribe"] = list_unsubscribe
    msg.set_content(body)
    if include_html_part:
        msg.add_alternative(f"<html><body><pre>{body}</pre></body></html>", subtype="html")
    return bytes(msg)


def _connector(messages: list[bytes]) -> tuple[GovDeliveryEmailConnector, _FakeProvider]:
    provider = _FakeProvider(messages)
    connector = GovDeliveryEmailConnector(
        settings=Settings(),  # empty settings; injected provider bypasses cred check
        message_provider=provider,
    )
    return connector, provider


# ---------------------------------------------------------------------------
# Happy path: a well-formed GovDelivery email produces a full Opportunity.
# ---------------------------------------------------------------------------


def test_discover_parses_wa_des_email_into_opportunity():
    body = (
        "IT Contracts Focus\n"
        "\n"
        "A new solicitation has been posted by Washington Technology Solutions.\n"
        "\n"
        "Title: AI Agent Enablement Consulting Services\n"
        "Solicitation: RFP AI-2026-101\n"
        "Due: August 15, 2026 5:00 PM PT\n"
        "\n"
        "Details: https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=57432\n"
        "\n"
        "Manage your subscriptions: "
        "https://public.govdelivery.com/accounts/WADES/subscribers/abcd/preferences\n"
    )
    raw = _make_email(subject="IT Contracts Focus - New RFP posted", body=body)
    connector, provider = _connector([raw])

    opportunities = connector.discover()

    assert len(opportunities) == 1
    op = opportunities[0]
    assert op.source_agency == "Washington State"
    assert op.source_system == SourceSystemType.OFFICIAL_EMAIL_SUBSCRIPTION
    assert op.solicitation_number == "AI-2026-101"
    assert op.procurement_type == ProcurementType.RFP
    assert op.title == "New RFP posted"  # topic prefix "IT Contracts Focus -" stripped
    assert op.source_url == (
        "https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=57432"
    )
    assert op.due_at is not None and op.due_at.year == 2026 and op.due_at.month == 8
    assert op.published_at is not None and op.published_at.year == 2026
    assert op.location == "Washington, USA"
    assert op.categories == ["WADES"]
    assert op.status == OpportunityStatus.UNKNOWN  # deliberately not inferred
    assert provider.since_calls, "provider must be asked for messages since a cutoff"


# ---------------------------------------------------------------------------
# Filtering: non-GovDelivery messages are silently skipped, not misparsed.
# ---------------------------------------------------------------------------


def test_discover_skips_non_govdelivery_messages():
    raw = _make_email(
        subject="Newsletter",
        from_addr="Random Sender <noreply@example.com>",
        body="Just some marketing content, no unsubscribe URL that looks like govdelivery.",
        list_unsubscribe=None,
    )
    connector, _ = _connector([raw])
    assert connector.discover() == []


def test_discover_accepts_message_with_govdelivery_slug_in_body_only():
    # Some agencies rewrite From: to their own address but keep the
    # GovDelivery unsubscribe URL in the body. Parser must still recognize it.
    body = (
        "New solicitation.\n"
        "Details: https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=1\n"
        "https://public.govdelivery.com/accounts/WADES/subscribers/x/preferences\n"
    )
    raw = _make_email(
        subject="New Bid",
        from_addr="Custom Sender <notify@des.wa.gov>",
        body=body,
        list_unsubscribe=None,
    )
    connector, _ = _connector([raw])
    opportunities = connector.discover()
    assert len(opportunities) == 1
    assert opportunities[0].source_agency == "Washington State"


# ---------------------------------------------------------------------------
# Robustness: malformed / thin messages don't crash the batch.
# ---------------------------------------------------------------------------


def test_discover_skips_message_without_subject_or_body():
    raw = _make_email(subject="", body="")
    connector, _ = _connector([raw])
    assert connector.discover() == []


def test_discover_survives_a_completely_malformed_email():
    malformed = b"\x00\x01not an rfc5322 message at all\r\n"
    good = _make_email(
        subject="IT Contracts Focus - Another",
        body=(
            "Body https://pr-webs-vendor.des.wa.gov/x "
            "https://public.govdelivery.com/accounts/WADES/subscribers/a/b"
        ),
    )
    connector, _ = _connector([malformed, good])
    # The malformed one is skipped; the good one still parses.
    opportunities = connector.discover()
    assert len(opportunities) == 1


def test_discover_dedupes_by_opportunity_id():
    body = (
        "RFP AI-2026-101 details here.\n"
        "https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=99\n"
        "https://public.govdelivery.com/accounts/WADES/subscribers/x/preferences\n"
    )
    raw_a = _make_email(subject="Title one", body=body, message_id="<a@x>")
    raw_b = _make_email(subject="Title two", body=body, message_id="<b@x>")
    connector, _ = _connector([raw_a, raw_b])
    opportunities = connector.discover()
    # Same solicitation number -> same Opportunity.id -> deduped to 1.
    assert len(opportunities) == 1
    assert opportunities[0].solicitation_number == "AI-2026-101"


# ---------------------------------------------------------------------------
# URL selection: GovDelivery infrastructure URLs are never used as source_url.
# ---------------------------------------------------------------------------


def test_source_url_prefers_agency_link_over_govdelivery_infrastructure():
    body = (
        "https://public.govdelivery.com/accounts/WADES/subscribers/x/preferences\n"
        "https://links.govdelivery.com/track?u=abc\n"
        "https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=222\n"
    )
    raw = _make_email(subject="Notice", body=body)
    connector, _ = _connector([raw])
    op = connector.discover()[0]
    assert op.source_url == "https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=222"


def test_source_url_falls_back_to_none_when_only_infra_links_present():
    body = (
        "https://public.govdelivery.com/accounts/WADES/subscribers/x/preferences\n"
        "https://subscriberhelp.govdelivery.com/hc/en-us\n"
    )
    raw = _make_email(subject="Notice", body=body)
    connector, _ = _connector([raw])
    op = connector.discover()[0]
    assert op.source_url is None


# ---------------------------------------------------------------------------
# HTML-only bodies: no plain-text part means the naive HTML strip must still
# expose URLs and enough text for downstream extraction.
# ---------------------------------------------------------------------------


def test_html_only_body_is_stripped_enough_to_extract_url_and_number():
    msg = EmailMessage()
    msg["Subject"] = "IT Contracts Focus - HTML notice"
    msg["From"] = "WA DES <no-reply@subscribe.des.wa.gov>"
    msg["Date"] = "Fri, 24 Jul 2026 12:00:00 -0700"
    msg["Message-ID"] = "<html-only@x>"
    msg["List-Unsubscribe"] = (
        "<https://public.govdelivery.com/accounts/WADES/subscribers/x/preferences>"
    )
    html_body = (
        "<html><body>"
        "<p>New <b>RFP HTML-42</b> posted.</p>"
        '<a href="https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=42">'
        "Learn more</a>"
        '<a href="https://public.govdelivery.com/accounts/WADES/subscribers/x/preferences">'
        "Unsubscribe</a>"
        "</body></html>"
    )
    msg.set_content(html_body, subtype="html")
    raw = bytes(msg)

    connector, _ = _connector([raw])
    opportunities = connector.discover()
    assert len(opportunities) == 1
    op = opportunities[0]
    assert op.solicitation_number == "HTML-42"
    assert op.source_url == "https://pr-webs-vendor.des.wa.gov/Search_BidDetails.aspx?ID=42"


# ---------------------------------------------------------------------------
# Health check: reports the three meaningful states honestly.
# ---------------------------------------------------------------------------


def test_health_check_reports_not_implemented_without_credentials():
    # No credentials in settings + no injected provider = NOT_IMPLEMENTED.
    connector = GovDeliveryEmailConnector(settings=Settings())
    health = connector.health_check()
    assert health.status.value == "not_implemented"
    assert "GCO_GOVDELIVERY_IMAP_HOST" in health.reason
    assert health.manual_inbox_hint


def test_health_check_reports_ok_when_provider_is_reachable():
    connector, _ = _connector([])
    health = connector.health_check()
    assert health.status.value == "ok"
    assert health.source_agency == DEFAULT_SOURCE_AGENCY


def test_health_check_reports_unavailable_when_provider_raises():
    connector = GovDeliveryEmailConnector(
        settings=Settings(), message_provider=_RaisingProvider()
    )
    health = connector.health_check()
    assert health.status.value == "unavailable"
    assert "simulated IMAP failure" in health.reason


# ---------------------------------------------------------------------------
# fetch_details / fetch_documents: contract behaviour.
# ---------------------------------------------------------------------------


def test_fetch_details_refreshes_timestamp_only():
    raw = _make_email(
        subject="Notice",
        body="https://pr-webs-vendor.des.wa.gov/x https://public.govdelivery.com/accounts/WADES/y",
    )
    connector, _ = _connector([raw])
    op = connector.discover()[0]
    updated = connector.fetch_details(op)
    assert updated.id == op.id
    assert updated.last_checked_at >= op.last_checked_at


def test_fetch_documents_returns_empty_list():
    raw = _make_email(
        subject="Notice",
        body="https://pr-webs-vendor.des.wa.gov/x https://public.govdelivery.com/accounts/WADES/y",
    )
    connector, _ = _connector([raw])
    op = connector.discover()[0]
    assert connector.fetch_documents(op) == []


# ---------------------------------------------------------------------------
# Registry integration: the CLI can look this connector up by name.
# ---------------------------------------------------------------------------


def test_connector_is_registered_and_importable():
    from gov_contract_os.collectors.registry import CONNECTOR_REGISTRY, get_connector

    assert "govdelivery_email" in CONNECTOR_REGISTRY
    connector = get_connector("govdelivery_email")
    assert isinstance(connector, GovDeliveryEmailConnector)


# ---------------------------------------------------------------------------
# Interface: MessageProvider is a runtime-friendly protocol.
# ---------------------------------------------------------------------------


def test_fake_provider_satisfies_message_provider_protocol():
    # This test guards against future signature drift on MessageProvider that
    # would silently break the injectable-test pattern the whole suite relies on.
    provider: MessageProvider = _FakeProvider([])
    assert list(provider.fetch_recent(dt.datetime.now(dt.UTC))) == []


if __name__ == "__main__":  # pragma: no cover - convenience runner
    pytest.main([__file__, "-v"])
