from __future__ import annotations

import datetime as dt

import pytest

from gov_contract_os.models.opportunity import Opportunity, OpportunityStatus, SourceSystemType


@pytest.fixture
def now() -> dt.datetime:
    return dt.datetime(2026, 7, 21, 12, 0, tzinfo=dt.UTC)


@pytest.fixture
def make_opportunity(now):
    def _make(**overrides) -> Opportunity:
        defaults = dict(
            id="test-id",
            source_agency="Port of Seattle",
            source_system=SourceSystemType.OFFICIAL_API,
            solicitation_number="26-36",
            title="Emergency Elevator Communication System",
            description="Procurement for an AI-enabled Azure-based elevator communication system.",
            status=OpportunityStatus.OPEN,
            due_at=now + dt.timedelta(days=30),
            discovered_at=now,
            last_checked_at=now,
        )
        defaults.update(overrides)
        return Opportunity(**defaults)

    return _make
