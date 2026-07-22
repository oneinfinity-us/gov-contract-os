"""Connector registry: maps a --source name to its connector class.

Central place the CLI (and OpenClaw workflows) use to discover which sources
exist and instantiate the right connector, without hardcoding imports all over.
"""

from __future__ import annotations

from gov_contract_os.collectors.base import Connector
from gov_contract_os.collectors.city_of_bellevue import CityOfBellevueConnector
from gov_contract_os.collectors.city_of_seattle import CityOfSeattleConnector
from gov_contract_os.collectors.king_county import KingCountyConnector
from gov_contract_os.collectors.port_of_seattle import PortOfSeattleConnector
from gov_contract_os.collectors.washington_state import WashingtonStateConnector

CONNECTOR_REGISTRY: dict[str, type[Connector]] = {
    "washington_state": WashingtonStateConnector,
    "king_county": KingCountyConnector,
    "city_of_seattle": CityOfSeattleConnector,
    "city_of_bellevue": CityOfBellevueConnector,
    "port_of_seattle": PortOfSeattleConnector,
}


def get_connector(source_name: str) -> Connector:
    try:
        connector_cls = CONNECTOR_REGISTRY[source_name]
    except KeyError as exc:
        valid = ", ".join(sorted(CONNECTOR_REGISTRY))
        raise ValueError(f"Unknown source '{source_name}'. Valid sources: {valid}") from exc
    return connector_cls()
