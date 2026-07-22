"""Level-1 (deterministic, no LLM) scoring: Opportunity -> Analysis.

Output levels (per CLAUDE.md):
  85-100 immediate_attention   70-84 worth_analyzing
  50-69  watch                  0-49 usually_skip
"""

from __future__ import annotations

import datetime as dt

from gov_contract_os.models.analysis import Analysis, FitLevel, RecommendedRole
from gov_contract_os.models.opportunity import Opportunity
from gov_contract_os.scoring.rules import (
    CAPABILITY_CATEGORIES,
    score_capability_category,
    score_mandatory_requirements,
    score_small_company_fit,
    score_timeline_feasibility,
)

ADVANCED_MODEL_SCORE_THRESHOLD = 75


def score_opportunity(opportunity: Opportunity, now: dt.datetime | None = None) -> Analysis:
    now = now or dt.datetime.now(dt.UTC)
    title = opportunity.title or ""
    body = opportunity.description or ""

    matched_capabilities: list[str] = []
    capability_gaps: list[str] = []
    mismatch_notes: list[str] = []

    total_score = 0.0
    for category in CAPABILITY_CATEGORIES:
        result = score_capability_category(title, body, category)
        total_score += result.score
        if result.matched_keywords:
            matched_capabilities.extend(f"{category.name}: {kw}" for kw in result.matched_keywords)
        else:
            capability_gaps.append(category.name)
        if result.likely_mismatch:
            mismatch_notes.append(
                f"{category.name}: keyword hit but may not actually match "
                f"(found: {', '.join(result.matched_keywords)})"
            )

    total_score += score_small_company_fit(opportunity.estimated_value_max)
    total_score += score_mandatory_requirements(opportunity.mandatory_requirements)
    total_score += score_timeline_feasibility(opportunity.due_at, now)

    score = max(0, min(100, round(total_score)))
    fit_level = Analysis.fit_level_for_score(score)
    recommended_role = _recommend_role(fit_level, opportunity)

    next_actions = list(mismatch_notes)
    if capability_gaps:
        next_actions.append(
            "Confirm against company/capabilities.md whether these gaps are real: "
            + ", ".join(capability_gaps)
        )
    if not opportunity.mandatory_requirements:
        next_actions.append(
            "Mandatory requirements not yet extracted - run skills/opportunity-review "
            "or `rfp analyze` on the solicitation documents before deciding go/no-go."
        )

    return Analysis(
        opportunity_id=opportunity.id,
        fit_score=score,
        fit_level=fit_level,
        recommended_role=recommended_role,
        matched_capabilities=matched_capabilities,
        capability_gaps=capability_gaps,
        mandatory_requirement_risks=[],
        next_actions=next_actions,
        requires_human_review=True,
        requires_advanced_model=score >= ADVANCED_MODEL_SCORE_THRESHOLD,
        analysis_version="0.1.0",
    )


def _recommend_role(fit_level: FitLevel, opportunity: Opportunity) -> RecommendedRole:
    if fit_level is FitLevel.USUALLY_SKIP:
        return RecommendedRole.NO_BID
    if fit_level is FitLevel.WATCH:
        return RecommendedRole.TEAMING_PARTNER
    # worth_analyzing / immediate_attention: default to Prime unless the
    # opportunity clearly looks too large for a small firm to lead solo.
    if opportunity.estimated_value_max and opportunity.estimated_value_max > 2_000_000:
        return RecommendedRole.SUBCONTRACTOR
    return RecommendedRole.PRIME
