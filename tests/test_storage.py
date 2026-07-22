from __future__ import annotations

from pathlib import Path

from gov_contract_os.models.analysis import Analysis, FitLevel, RecommendedRole
from gov_contract_os.storage.db import (
    get_engine,
    init_db,
    list_opportunities,
    list_opportunities_without_analysis,
    make_session_factory,
    session_scope,
    upsert_analysis,
    upsert_opportunity,
)


def _make_engine(tmp_path: Path):
    engine = get_engine(tmp_path / "test.sqlite3")
    init_db(engine)
    return engine


def test_upsert_opportunity_inserts_new_row(tmp_path, make_opportunity):
    engine = _make_engine(tmp_path)
    session_factory = make_session_factory(engine)
    opportunity = make_opportunity()

    with session_scope(session_factory) as session:
        _, created = upsert_opportunity(session, opportunity)
        assert created is True

    with session_scope(session_factory) as session:
        stored = list_opportunities(session)
        assert len(stored) == 1
        assert stored[0].id == opportunity.id
        assert stored[0].title == opportunity.title


def test_opportunities_round_trip_with_utc_aware_datetimes(tmp_path, make_opportunity):
    # Regression test: SQLite does not persist tzinfo, so datetimes read back
    # from the DB used to come back naive and crashed scoring (which subtracts
    # them from a tz-aware `now`). See gov_contract_os.storage.db._as_utc.
    engine = _make_engine(tmp_path)
    session_factory = make_session_factory(engine)
    opportunity = make_opportunity()
    assert opportunity.due_at is not None

    with session_scope(session_factory) as session:
        upsert_opportunity(session, opportunity)

    with session_scope(session_factory) as session:
        stored = list_opportunities(session)[0]
        assert stored.due_at is not None
        assert stored.due_at.tzinfo is not None
        assert stored.discovered_at.tzinfo is not None
        # must not raise TypeError: can't subtract offset-naive and offset-aware
        stored.due_at - opportunity.discovered_at


def test_upsert_opportunity_updates_existing_row_instead_of_duplicating(tmp_path, make_opportunity):
    engine = _make_engine(tmp_path)
    session_factory = make_session_factory(engine)
    opportunity = make_opportunity()

    with session_scope(session_factory) as session:
        upsert_opportunity(session, opportunity)

    updated = opportunity.model_copy(
        update={"title": "Updated Title", "status": opportunity.status}
    )
    with session_scope(session_factory) as session:
        _, created = upsert_opportunity(session, updated)
        assert created is False

    with session_scope(session_factory) as session:
        stored = list_opportunities(session)
        assert len(stored) == 1
        assert stored[0].title == "Updated Title"


def test_list_opportunities_without_analysis(tmp_path, make_opportunity):
    engine = _make_engine(tmp_path)
    session_factory = make_session_factory(engine)
    scored = make_opportunity(id="scored-id", solicitation_number="A-1")
    unscored = make_opportunity(id="unscored-id", solicitation_number="A-2")

    with session_scope(session_factory) as session:
        upsert_opportunity(session, scored)
        upsert_opportunity(session, unscored)
        upsert_analysis(
            session,
            Analysis(
                opportunity_id=scored.id,
                fit_score=90,
                fit_level=FitLevel.IMMEDIATE_ATTENTION,
                recommended_role=RecommendedRole.PRIME,
            ),
        )

    with session_scope(session_factory) as session:
        pending = list_opportunities_without_analysis(session)
        assert [o.id for o in pending] == ["unscored-id"]


def test_upsert_analysis_updates_existing(tmp_path, make_opportunity):
    engine = _make_engine(tmp_path)
    session_factory = make_session_factory(engine)
    opportunity = make_opportunity()

    with session_scope(session_factory) as session:
        upsert_opportunity(session, opportunity)
        upsert_analysis(
            session,
            Analysis(
                opportunity_id=opportunity.id,
                fit_score=50,
                fit_level=FitLevel.WATCH,
                recommended_role=RecommendedRole.TEAMING_PARTNER,
            ),
        )
        upsert_analysis(
            session,
            Analysis(
                opportunity_id=opportunity.id,
                fit_score=90,
                fit_level=FitLevel.IMMEDIATE_ATTENTION,
                recommended_role=RecommendedRole.PRIME,
            ),
        )

    with session_scope(session_factory) as session:
        from gov_contract_os.storage.db import get_analysis

        record = get_analysis(session, opportunity.id)
        assert record is not None
        assert record.fit_score == 90
        assert record.recommended_role == "prime"
