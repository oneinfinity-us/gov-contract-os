from __future__ import annotations

import datetime as dt

from gov_contract_os.models.analysis import Analysis, FitLevel
from gov_contract_os.models.opportunity import Opportunity


def test_dedupe_key_prefers_solicitation_number():
    key = Opportunity.dedupe_key(
        source_agency="Port of Seattle",
        solicitation_number="26-36",
        source_url="https://example.org/a",
        title="Some Title",
        due_at=None,
    )
    assert key == "port of seattle::26-36"


def test_dedupe_key_falls_back_to_url_title_due_date():
    due = dt.datetime(2026, 8, 1, tzinfo=dt.UTC)
    key = Opportunity.dedupe_key(
        source_agency="City of Seattle",
        solicitation_number=None,
        source_url="https://example.org/A",
        title="  Some   Title  ",
        due_at=due,
    )
    assert key == f"city of seattle::https://example.org/a::some title::{due.isoformat()}"


def test_build_id_is_deterministic():
    id1 = Opportunity.build_id("Port of Seattle", "26-36", None, "Title", None)
    id2 = Opportunity.build_id("Port of Seattle", "26-36", None, "Different Title", None)
    assert id1 == id2  # solicitation_number alone determines identity
    id3 = Opportunity.build_id("Port of Seattle", "26-37", None, "Title", None)
    assert id1 != id3


def test_compute_content_hash_changes_when_title_changes(make_opportunity):
    opportunity = make_opportunity()
    original_hash = opportunity.compute_content_hash()
    changed = opportunity.model_copy(update={"title": "A different title"})
    assert changed.compute_content_hash() != original_hash


def test_fit_level_boundaries():
    assert Analysis.fit_level_for_score(85) is FitLevel.IMMEDIATE_ATTENTION
    assert Analysis.fit_level_for_score(84) is FitLevel.WORTH_ANALYZING
    assert Analysis.fit_level_for_score(70) is FitLevel.WORTH_ANALYZING
    assert Analysis.fit_level_for_score(69) is FitLevel.WATCH
    assert Analysis.fit_level_for_score(50) is FitLevel.WATCH
    assert Analysis.fit_level_for_score(49) is FitLevel.USUALLY_SKIP
    assert Analysis.fit_level_for_score(0) is FitLevel.USUALLY_SKIP
