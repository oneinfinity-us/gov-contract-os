from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from gov_contract_os.collectors.city_of_seattle import RSS_URL, CityOfSeattleConnector
from gov_contract_os.collectors.http import PoliteHttpClient
from gov_contract_os.models.opportunity import (
    OpportunityStatus,
    ProcurementType,
    SourceSystemType,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _feed_xml() -> str:
    return (FIXTURES / "city_of_seattle_feed.xml").read_text(encoding="utf-8")


def _connector() -> CityOfSeattleConnector:
    return CityOfSeattleConnector(http_client=PoliteHttpClient(min_interval_seconds=0))


@pytest.fixture
def mocked_feed():
    with respx.mock(assert_all_called=False) as mock:
        mock.get(RSS_URL).mock(return_value=httpx.Response(200, text=_feed_xml()))
        yield mock


def test_discover_filters_out_announcement_only_items(mocked_feed):
    connector = _connector()
    opportunities = connector.discover()
    # The fixture has 5 items; 1 is an announcement/webinar with no solicitation
    # number and no procurement-platform link, so it must be filtered out.
    assert len(opportunities) == 4
    titles = {o.title for o in opportunities}
    assert not any("DOING BUSINESS" in t.upper() for t in titles)


def test_discover_sets_source_system_and_agency(mocked_feed):
    connector = _connector()
    opportunities = connector.discover()
    for o in opportunities:
        assert o.source_agency == "City of Seattle"
        assert o.source_system == SourceSystemType.OFFICIAL_RSS
        assert o.location == "Seattle, WA"


def test_discover_extracts_open_item_with_number_and_external_url(mocked_feed):
    connector = _connector()
    opportunities = connector.discover()
    ai_item = next(o for o in opportunities if o.solicitation_number == "AI0-7001")

    assert ai_item.status == OpportunityStatus.OPEN
    assert ai_item.procurement_type == ProcurementType.RFP
    assert ai_item.title == "AI Agent and Copilot Enablement Consulting Services; RFP#AI0-7001"
    assert ai_item.source_url == "https://procurement.opengov.com/portal/seattle/projects/900123"
    assert ai_item.due_at is not None
    assert ai_item.due_at.year == 2026
    assert ai_item.due_at.month == 8
    assert ai_item.due_at.day == 15


def test_discover_strips_status_prefix_and_maps_status(mocked_feed):
    connector = _connector()
    opportunities = connector.discover()

    closed_item = next(o for o in opportunities if o.solicitation_number == "TR0-6221")
    assert closed_item.status == OpportunityStatus.CLOSED
    assert not closed_item.title.upper().startswith("CLOSED")

    archived_item = next(o for o in opportunities if o.solicitation_number == "SU0-6265")
    assert archived_item.status == OpportunityStatus.CLOSED
    assert not archived_item.title.upper().startswith("ARCHIVED")

    canceled_item = next(o for o in opportunities if o.solicitation_number == "SP0-6173")
    assert canceled_item.status == OpportunityStatus.CANCELLED
    assert not canceled_item.title.upper().startswith("CANCELED")


def test_discover_ids_are_stable_across_calls(mocked_feed):
    connector = _connector()
    first_pass = {o.solicitation_number: o.id for o in connector.discover()}
    second_pass = {o.solicitation_number: o.id for o in connector.discover()}
    assert first_pass == second_pass


def test_fetch_details_refreshes_last_checked_at_without_new_request(mocked_feed):
    connector = _connector()
    opportunities = connector.discover()
    original = opportunities[0]

    updated = connector.fetch_details(original)

    assert updated.id == original.id
    assert updated.last_checked_at >= original.last_checked_at
    # only one route registered (the feed itself); fetch_details must not call it again
    assert mocked_feed.calls.call_count == 1


def test_fetch_documents_returns_empty_list(mocked_feed):
    connector = _connector()
    opportunities = connector.discover()
    assert connector.fetch_documents(opportunities[0]) == []


def test_health_check_ok(mocked_feed):
    connector = _connector()
    health = connector.health_check()
    assert health.status.value == "ok"


def test_health_check_reports_unavailable_without_raising():
    with respx.mock(assert_all_called=False) as mock:
        mock.get(RSS_URL).mock(return_value=httpx.Response(500))
        connector = _connector()
        health = connector.health_check()
    assert health.status.value == "unavailable"
    assert health.recommended_alternative


def test_health_check_reports_degraded_on_bad_xml():
    with respx.mock(assert_all_called=False) as mock:
        mock.get(RSS_URL).mock(return_value=httpx.Response(200, text="not xml at all <<<"))
        connector = _connector()
        health = connector.health_check()
    assert health.status.value == "degraded"
