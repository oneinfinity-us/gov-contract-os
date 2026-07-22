from __future__ import annotations

import datetime as dt

from gov_contract_os.models.analysis import FitLevel, RecommendedRole
from gov_contract_os.scoring.rules import (
    AI_AGENT_COPILOT_AZURE,
    score_capability_category,
    score_small_company_fit,
    score_timeline_feasibility,
)
from gov_contract_os.scoring.scorer import score_opportunity


def test_score_capability_category_no_match_is_zero():
    result = score_capability_category(
        "Roadway paving project", "asphalt and gravel work", AI_AGENT_COPILOT_AZURE
    )
    assert result.score == 0.0
    assert result.matched_keywords == []


def test_score_capability_category_title_hit_scores_higher_than_body_only():
    title_hit = score_capability_category(
        "Azure Copilot integration project", "", AI_AGENT_COPILOT_AZURE
    )
    body_hit = score_capability_category(
        "Some project", "uses azure cloud services", AI_AGENT_COPILOT_AZURE
    )
    assert title_hit.score > body_hit.score


def test_score_capability_category_flags_likely_mismatch():
    result = score_capability_category("Travel agent services contract", "", AI_AGENT_COPILOT_AZURE)
    assert result.likely_mismatch is True


def test_score_small_company_fit_thresholds():
    assert score_small_company_fit(None) == 5.0
    assert score_small_company_fit(500_000) == 10.0
    assert score_small_company_fit(5_000_000) == 2.5


def test_score_timeline_feasibility_boundaries():
    now = dt.datetime(2026, 7, 21, tzinfo=dt.UTC)
    assert score_timeline_feasibility(None, now) == 5.0
    assert score_timeline_feasibility(now - dt.timedelta(days=1), now) == 0.0
    assert score_timeline_feasibility(now + dt.timedelta(days=25), now) == 10.0
    assert score_timeline_feasibility(now + dt.timedelta(days=15), now) == 6.0
    assert score_timeline_feasibility(now + dt.timedelta(days=5), now) == 2.0


def test_score_opportunity_end_to_end_strong_match(make_opportunity, now):
    opportunity = make_opportunity(
        title="Microsoft Copilot and Azure AI Agent Consulting Services - Seattle",
        description=(
            "The Port of Seattle seeks a small business to provide software development, "
            "workflow automation, and system integration services, with subcontracting "
            "and teaming opportunities encouraged."
        ),
        due_at=now + dt.timedelta(days=30),
        estimated_value_max=500_000,
    )
    analysis = score_opportunity(opportunity, now=now)
    assert analysis.fit_score >= 70
    assert analysis.fit_level in (FitLevel.WORTH_ANALYZING, FitLevel.IMMEDIATE_ATTENTION)
    assert analysis.recommended_role == RecommendedRole.PRIME
    assert analysis.requires_human_review is True


def test_score_opportunity_end_to_end_weak_match(make_opportunity, now):
    opportunity = make_opportunity(
        title="Roadway Crack Sealing",
        description="Asphalt and concrete crack sealing services for city roadways.",
        due_at=now + dt.timedelta(days=5),
        estimated_value_max=5_000_000,
    )
    analysis = score_opportunity(opportunity, now=now)
    assert analysis.fit_score < 50
    assert analysis.fit_level is FitLevel.USUALLY_SKIP
    assert analysis.recommended_role == RecommendedRole.NO_BID
