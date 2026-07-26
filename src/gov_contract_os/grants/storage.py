"""Storage helpers for grants: upsert and query for GrantOpportunity /
GrantAnalysis rows. Mirrors the pattern in `gov_contract_os.storage.db` but
for the grants tables.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from gov_contract_os.grants.models import (
    EligibilityCheck,
    EligibilityResult,
    EligibilityStatus,
    GrantAnalysis,
    GrantFitLevel,
    GrantOpportunity,
    GrantRecommendation,
)
from gov_contract_os.grants.schema import GrantAnalysisRecord, GrantOpportunityRecord
from gov_contract_os.models.opportunity import Document, SourceSystemType


def _as_utc(value: dt.datetime | None) -> dt.datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value


def _grant_to_kwargs(grant: GrantOpportunity) -> dict:
    content_hash = grant.content_hash or grant.compute_content_hash()
    return {
        "id": grant.id,
        "opportunity_type": grant.opportunity_type.value,
        "funder_name": grant.funder_name,
        "funder_type": grant.funder_type.value,
        "program_name": grant.program_name,
        "funding_opportunity_number": grant.funding_opportunity_number,
        "title": grant.title,
        "description": grant.description,
        "stage": grant.stage.value,
        "posted_at": grant.posted_at,
        "loi_due_at": grant.loi_due_at,
        "full_proposal_due_at": grant.full_proposal_due_at,
        "award_notification_at": grant.award_notification_at,
        "project_start_at": grant.project_start_at,
        "project_end_at": grant.project_end_at,
        "award_ceiling": grant.award_ceiling,
        "award_floor": grant.award_floor,
        "total_program_funding": grant.total_program_funding,
        "expected_awards_count": grant.expected_awards_count,
        "cost_share_required": grant.cost_share_required,
        "cost_share_percent": grant.cost_share_percent,
        "indirect_cost_limit_percent": grant.indirect_cost_limit_percent,
        "currency": grant.currency,
        "eligible_applicants": [t.value for t in grant.eligible_applicants],
        "focus_areas": list(grant.focus_areas),
        "geographic_scope": list(grant.geographic_scope),
        "populations_served": list(grant.populations_served),
        "cfda_or_aln_codes": list(grant.cfda_or_aln_codes),
        "requires_501c3": grant.requires_501c3,
        "requires_sam_registration": grant.requires_sam_registration,
        "invitation_only": grant.invitation_only,
        "letter_of_inquiry_required": grant.letter_of_inquiry_required,
        "preapplication_required": grant.preapplication_required,
        "mandatory_requirements": list(grant.mandatory_requirements),
        "required_documents": list(grant.required_documents),
        "reporting_requirements": list(grant.reporting_requirements),
        "evaluation_requirements": list(grant.evaluation_requirements),
        "source_system": grant.source_system.value,
        "source_url": grant.source_url,
        "contact_name": grant.contact_name,
        "contact_email": grant.contact_email,
        "documents": [doc.model_dump(mode="json") for doc in grant.documents],
        "discovered_at": grant.discovered_at,
        "last_checked_at": grant.last_checked_at,
        "content_hash": content_hash,
        "raw_source_reference": grant.raw_source_reference,
    }


def record_to_grant(record: GrantOpportunityRecord) -> GrantOpportunity:
    from gov_contract_os.grants.models import (  # local import to avoid cycles
        EligibleApplicantType,
        FunderType,
        GrantStage,
    )
    from gov_contract_os.core.types import OpportunityType

    return GrantOpportunity(
        id=record.id,
        opportunity_type=OpportunityType(record.opportunity_type),
        funder_name=record.funder_name,
        funder_type=FunderType(record.funder_type),
        program_name=record.program_name,
        funding_opportunity_number=record.funding_opportunity_number,
        title=record.title,
        description=record.description,
        stage=GrantStage(record.stage),
        posted_at=_as_utc(record.posted_at),
        loi_due_at=_as_utc(record.loi_due_at),
        full_proposal_due_at=_as_utc(record.full_proposal_due_at),
        award_notification_at=_as_utc(record.award_notification_at),
        project_start_at=_as_utc(record.project_start_at),
        project_end_at=_as_utc(record.project_end_at),
        award_ceiling=record.award_ceiling,
        award_floor=record.award_floor,
        total_program_funding=record.total_program_funding,
        expected_awards_count=record.expected_awards_count,
        cost_share_required=record.cost_share_required,
        cost_share_percent=record.cost_share_percent,
        indirect_cost_limit_percent=record.indirect_cost_limit_percent,
        currency=record.currency,
        eligible_applicants=[EligibleApplicantType(v) for v in (record.eligible_applicants or [])],
        focus_areas=list(record.focus_areas or []),
        geographic_scope=list(record.geographic_scope or []),
        populations_served=list(record.populations_served or []),
        cfda_or_aln_codes=list(record.cfda_or_aln_codes or []),
        requires_501c3=record.requires_501c3,
        requires_sam_registration=record.requires_sam_registration,
        invitation_only=record.invitation_only,
        letter_of_inquiry_required=record.letter_of_inquiry_required,
        preapplication_required=record.preapplication_required,
        mandatory_requirements=list(record.mandatory_requirements or []),
        required_documents=list(record.required_documents or []),
        reporting_requirements=list(record.reporting_requirements or []),
        evaluation_requirements=list(record.evaluation_requirements or []),
        source_system=SourceSystemType(record.source_system),
        source_url=record.source_url,
        contact_name=record.contact_name,
        contact_email=record.contact_email,
        documents=[Document(**doc) for doc in (record.documents or [])],
        discovered_at=_as_utc(record.discovered_at) or dt.datetime.now(dt.UTC),
        last_checked_at=_as_utc(record.last_checked_at),
        content_hash=record.content_hash,
        raw_source_reference=record.raw_source_reference,
    )


def upsert_grant(
    session: Session, grant: GrantOpportunity
) -> tuple[GrantOpportunityRecord, bool]:
    kwargs = _grant_to_kwargs(grant)
    existing = session.get(GrantOpportunityRecord, grant.id)
    if existing is None:
        record = GrantOpportunityRecord(**kwargs)
        session.add(record)
        return record, True
    for key, value in kwargs.items():
        if key == "id":
            continue
        setattr(existing, key, value)
    return existing, False


def _analysis_to_kwargs(analysis: GrantAnalysis) -> dict:
    return {
        "grant_id": analysis.grant_id,
        "nonprofit_slug": analysis.nonprofit_slug,
        "eligibility_status": analysis.eligibility.status.value,
        "eligibility_checks": [c.model_dump(mode="json") for c in analysis.eligibility.checks],
        "eligibility_hard_failures": list(analysis.eligibility.hard_failures),
        "eligibility_missing_information": list(analysis.eligibility.missing_information),
        "eligibility_conditional_actions": list(analysis.eligibility.conditional_actions),
        "fit_score": analysis.fit_score,
        "fit_level": analysis.fit_level.value if analysis.fit_level else None,
        "recommendation": analysis.recommendation.value,
        "matched_criteria": list(analysis.matched_criteria),
        "gaps": list(analysis.gaps),
        "risks": list(analysis.risks),
        "next_actions": list(analysis.next_actions),
        "requires_human_review": analysis.requires_human_review,
        "requires_advanced_model": analysis.requires_advanced_model,
        "analysis_version": analysis.analysis_version,
    }


def upsert_grant_analysis(session: Session, analysis: GrantAnalysis) -> GrantAnalysisRecord:
    kwargs = _analysis_to_kwargs(analysis)
    existing = session.get(
        GrantAnalysisRecord, (analysis.grant_id, analysis.nonprofit_slug)
    )
    if existing is None:
        record = GrantAnalysisRecord(**kwargs)
        session.add(record)
        return record
    for key, value in kwargs.items():
        if key in ("grant_id", "nonprofit_slug"):
            continue
        setattr(existing, key, value)
    return existing


def list_grants(session: Session) -> list[GrantOpportunity]:
    stmt = select(GrantOpportunityRecord)
    return [record_to_grant(r) for r in session.scalars(stmt)]


def list_grants_without_analysis(
    session: Session, nonprofit_slug: str
) -> list[GrantOpportunity]:
    analyzed = select(GrantAnalysisRecord.grant_id).where(
        GrantAnalysisRecord.nonprofit_slug == nonprofit_slug
    )
    stmt = select(GrantOpportunityRecord).where(GrantOpportunityRecord.id.not_in(analyzed))
    return [record_to_grant(r) for r in session.scalars(stmt)]


def record_to_analysis(record: GrantAnalysisRecord) -> GrantAnalysis:
    eligibility = EligibilityResult(
        status=EligibilityStatus(record.eligibility_status),
        checks=[EligibilityCheck(**c) for c in (record.eligibility_checks or [])],
        hard_failures=list(record.eligibility_hard_failures or []),
        missing_information=list(record.eligibility_missing_information or []),
        conditional_actions=list(record.eligibility_conditional_actions or []),
    )
    return GrantAnalysis(
        grant_id=record.grant_id,
        nonprofit_slug=record.nonprofit_slug,
        eligibility=eligibility,
        fit_score=record.fit_score,
        fit_level=GrantFitLevel(record.fit_level) if record.fit_level else None,
        recommendation=GrantRecommendation(record.recommendation),
        matched_criteria=list(record.matched_criteria or []),
        gaps=list(record.gaps or []),
        risks=list(record.risks or []),
        next_actions=list(record.next_actions or []),
        requires_human_review=record.requires_human_review,
        requires_advanced_model=record.requires_advanced_model,
        analysis_version=record.analysis_version,
    )


def get_grant_analysis(
    session: Session, grant_id: str, nonprofit_slug: str
) -> GrantAnalysis | None:
    record = session.get(GrantAnalysisRecord, (grant_id, nonprofit_slug))
    return record_to_analysis(record) if record else None
