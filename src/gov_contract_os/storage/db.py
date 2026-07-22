"""SQLite storage layer: engine/session helpers + upsert/query functions.

Deduplication happens implicitly: Opportunity.id is derived from
Opportunity.build_id() (agency+solicitation_number, or source_url+title+due
date as fallback), so re-discovering the same opportunity always maps to the
same row and upsert_opportunity() updates it in place instead of duplicating it.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from gov_contract_os.models.analysis import Analysis
from gov_contract_os.models.opportunity import Document, Opportunity
from gov_contract_os.storage.schema import AnalysisRecord, Base, OpportunityRecord


def _as_utc(value: dt.datetime | None) -> dt.datetime | None:
    """SQLite does not actually persist tzinfo (unlike Postgres' timestamptz), so
    datetimes read back from the DB are naive even though we always write UTC-aware
    values. Re-attach UTC here so downstream code can safely compare/subtract
    datetimes without re-deriving this fact every time.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value


def get_engine(db_path: Path) -> Engine:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", future=True)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _opportunity_to_kwargs(opportunity: Opportunity) -> dict:
    content_hash = opportunity.content_hash or opportunity.compute_content_hash()
    return {
        "id": opportunity.id,
        "source_agency": opportunity.source_agency,
        "source_system": opportunity.source_system.value,
        "solicitation_number": opportunity.solicitation_number,
        "title": opportunity.title,
        "description": opportunity.description,
        "status": opportunity.status.value,
        "procurement_type": opportunity.procurement_type.value,
        "categories": list(opportunity.categories),
        "published_at": opportunity.published_at,
        "questions_due_at": opportunity.questions_due_at,
        "prebid_at": opportunity.prebid_at,
        "due_at": opportunity.due_at,
        "award_date": opportunity.award_date,
        "estimated_value_min": opportunity.estimated_value_min,
        "estimated_value_max": opportunity.estimated_value_max,
        "currency": opportunity.currency,
        "location": opportunity.location,
        "prime_or_sub_notes": opportunity.prime_or_sub_notes,
        "small_business_goal": opportunity.small_business_goal,
        "wmbe_goal": opportunity.wmbe_goal,
        "mandatory_certifications": list(opportunity.mandatory_certifications),
        "mandatory_requirements": list(opportunity.mandatory_requirements),
        "contact_name": opportunity.contact_name,
        "contact_email": opportunity.contact_email,
        "source_url": opportunity.source_url,
        "documents": [doc.model_dump(mode="json") for doc in opportunity.documents],
        "discovered_at": opportunity.discovered_at,
        "last_checked_at": opportunity.last_checked_at,
        "content_hash": content_hash,
        "raw_source_reference": opportunity.raw_source_reference,
    }


def record_to_opportunity(record: OpportunityRecord) -> Opportunity:
    return Opportunity(
        id=record.id,
        source_agency=record.source_agency,
        source_system=record.source_system,
        solicitation_number=record.solicitation_number,
        title=record.title,
        description=record.description,
        status=record.status,
        procurement_type=record.procurement_type,
        categories=list(record.categories or []),
        published_at=_as_utc(record.published_at),
        questions_due_at=_as_utc(record.questions_due_at),
        prebid_at=_as_utc(record.prebid_at),
        due_at=_as_utc(record.due_at),
        award_date=_as_utc(record.award_date),
        estimated_value_min=record.estimated_value_min,
        estimated_value_max=record.estimated_value_max,
        currency=record.currency,
        location=record.location,
        prime_or_sub_notes=record.prime_or_sub_notes,
        small_business_goal=record.small_business_goal,
        wmbe_goal=record.wmbe_goal,
        mandatory_certifications=list(record.mandatory_certifications or []),
        mandatory_requirements=list(record.mandatory_requirements or []),
        contact_name=record.contact_name,
        contact_email=record.contact_email,
        source_url=record.source_url,
        documents=[Document(**doc) for doc in (record.documents or [])],
        discovered_at=_as_utc(record.discovered_at) or dt.datetime.now(dt.UTC),
        last_checked_at=_as_utc(record.last_checked_at),
        content_hash=record.content_hash,
        raw_source_reference=record.raw_source_reference,
    )


def upsert_opportunity(
    session: Session, opportunity: Opportunity
) -> tuple[OpportunityRecord, bool]:
    """Insert a new opportunity, or update the existing row with the same id.

    Returns (record, created) where created is True only for brand-new rows.
    """
    kwargs = _opportunity_to_kwargs(opportunity)
    existing = session.get(OpportunityRecord, opportunity.id)
    if existing is None:
        record = OpportunityRecord(**kwargs)
        session.add(record)
        return record, True

    for key, value in kwargs.items():
        if key == "id":
            continue
        setattr(existing, key, value)
    return existing, False


def upsert_analysis(session: Session, analysis: Analysis) -> AnalysisRecord:
    kwargs = {
        "opportunity_id": analysis.opportunity_id,
        "fit_score": analysis.fit_score,
        "fit_level": analysis.fit_level.value,
        "recommended_role": analysis.recommended_role.value,
        "matched_capabilities": list(analysis.matched_capabilities),
        "capability_gaps": list(analysis.capability_gaps),
        "mandatory_requirement_risks": list(analysis.mandatory_requirement_risks),
        "next_actions": list(analysis.next_actions),
        "requires_human_review": analysis.requires_human_review,
        "requires_advanced_model": analysis.requires_advanced_model,
        "analysis_version": analysis.analysis_version,
    }
    existing = session.get(AnalysisRecord, analysis.opportunity_id)
    if existing is None:
        record = AnalysisRecord(**kwargs)
        session.add(record)
        return record

    for key, value in kwargs.items():
        if key == "opportunity_id":
            continue
        setattr(existing, key, value)
    return existing


def list_opportunities(session: Session, source_agency: str | None = None) -> list[Opportunity]:
    stmt = select(OpportunityRecord)
    if source_agency:
        stmt = stmt.where(OpportunityRecord.source_agency == source_agency)
    return [record_to_opportunity(r) for r in session.scalars(stmt)]


def list_opportunities_without_analysis(session: Session) -> list[Opportunity]:
    """Opportunities that don't have an Analysis row yet - what `analyze --new` acts on."""
    analyzed_ids = select(AnalysisRecord.opportunity_id)
    stmt = select(OpportunityRecord).where(OpportunityRecord.id.not_in(analyzed_ids))
    return [record_to_opportunity(r) for r in session.scalars(stmt)]


def get_analysis(session: Session, opportunity_id: str) -> AnalysisRecord | None:
    return session.get(AnalysisRecord, opportunity_id)
