from __future__ import annotations

import datetime as dt

import pytest

from gov_contract_os.collectors.base import Connector, ConnectorHealthStatus
from gov_contract_os.collectors.city_of_bellevue import CityOfBellevueConnector
from gov_contract_os.collectors.king_county import KingCountyConnector
from gov_contract_os.collectors.registry import CONNECTOR_REGISTRY, get_connector
from gov_contract_os.collectors.washington_state import WashingtonStateConnector

# City of Seattle is a real, implemented connector (RSS-based) - covered by
# tests/test_collectors_city_of_seattle.py, not the generic stub tests below.
STUB_CONNECTORS = [
    WashingtonStateConnector,
    KingCountyConnector,
    CityOfBellevueConnector,
]


def test_connector_is_abstract():
    with pytest.raises(TypeError):
        Connector()  # type: ignore[abstract]


@pytest.mark.parametrize("connector_cls", STUB_CONNECTORS)
def test_stub_connectors_report_not_implemented_health(connector_cls):
    connector = connector_cls()
    health = connector.health_check()
    assert health.status == ConnectorHealthStatus.NOT_IMPLEMENTED
    assert health.reason
    assert health.recommended_alternative
    assert health.manual_inbox_hint
    assert isinstance(health.checked_at, dt.datetime)


@pytest.mark.parametrize("connector_cls", STUB_CONNECTORS)
def test_stub_connectors_raise_not_implemented_on_discover(connector_cls):
    connector = connector_cls()
    with pytest.raises(NotImplementedError):
        connector.discover()


def test_registry_contains_all_five_sources():
    assert set(CONNECTOR_REGISTRY) == {
        "washington_state",
        "king_county",
        "city_of_seattle",
        "city_of_bellevue",
        "port_of_seattle",
    }


def test_get_connector_unknown_source_raises_value_error():
    with pytest.raises(ValueError, match="Unknown source"):
        get_connector("not_a_real_source")
