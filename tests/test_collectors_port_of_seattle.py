from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from gov_contract_os.collectors.http import PoliteHttpClient
from gov_contract_os.collectors.port_of_seattle import API_BASE, PortOfSeattleConnector
from gov_contract_os.models.opportunity import OpportunityStatus, SourceSystemType

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _connector() -> PortOfSeattleConnector:
    # min_interval_seconds=0 - these are mocked, unit-level tests, no need to
    # actually rate-limit against a fake host.
    return PortOfSeattleConnector(http_client=PoliteHttpClient(min_interval_seconds=0))


@pytest.fixture
def mocked_api():
    list_payload = _load("port_of_seattle_list.json")
    detail_payload = _load("port_of_seattle_detail.json")

    def handler(request: httpx.Request) -> httpx.Response:
        filter_value = request.url.params.get("$filter", "")
        if filter_value.startswith("Id eq"):
            return httpx.Response(200, json=detail_payload)
        return httpx.Response(200, json=list_payload)

    with respx.mock(assert_all_called=False) as mock:
        mock.get(f"{API_BASE}/Solicitations").mock(side_effect=handler)
        yield mock


def test_discover_returns_opportunities(mocked_api):
    connector = _connector()
    opportunities = connector.discover()
    assert len(opportunities) == 2
    titles = {o.title for o in opportunities}
    assert "26-36 Emergency Elevator Communication System (EECS)" in titles
    for o in opportunities:
        assert o.source_agency == "Port of Seattle"
        assert o.source_system == SourceSystemType.OFFICIAL_API
        assert o.status == OpportunityStatus.OPEN


def test_discover_ids_are_stable_across_calls(mocked_api):
    connector = _connector()
    first_pass = {o.solicitation_number: o.id for o in connector.discover()}
    second_pass = {o.solicitation_number: o.id for o in connector.discover()}
    assert first_pass == second_pass


def test_fetch_details_enriches_description_and_contact(mocked_api):
    connector = _connector()
    summaries = connector.discover()
    eecs = next(o for o in summaries if o.solicitation_number == "26-36")

    detailed = connector.fetch_details(eecs)

    assert detailed.id == eecs.id  # id must not change after enrichment
    assert detailed.description and "Emergency Elevator" in detailed.description
    assert detailed.contact_email == "Marbet.A@portseattle.org"
    assert detailed.contact_name == "Marbet, Andrea"
    assert detailed.categories == ["ICT Enterprise Infrastructure Services"]


def test_fetch_documents_returns_empty_list_and_does_not_raise(mocked_api):
    connector = _connector()
    summaries = connector.discover()
    documents = connector.fetch_documents(summaries[0])
    assert documents == []


def test_health_check_ok(mocked_api):
    connector = _connector()
    health = connector.health_check()
    assert health.status.value == "ok"


def test_health_check_reports_failure_without_raising():
    with respx.mock(assert_all_called=False) as mock:
        mock.get(f"{API_BASE}/Solicitations").mock(return_value=httpx.Response(500))
        connector = _connector()
        health = connector.health_check()
    assert health.status.value == "unavailable"
    assert health.recommended_alternative
    assert health.manual_inbox_hint
