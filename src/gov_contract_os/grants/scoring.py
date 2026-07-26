"""Level-1 grant scoring (deterministic, no LLM).

Reads weights from `config/scoring/grant-scoring.yaml` so scoring can be
tuned per-nonprofit without code changes. Runs only on grants that passed
`check_grant_eligibility` with status ELIGIBLE or CONDITIONAL - ineligible
grants get `fit_score=None`.

This matches the Level-1 pattern already used for procurement scoring
(`gov_contract_os.scoring.scorer`): fast, free, deterministic, and
`requires_advanced_model=True` gates a later LLM pass.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from gov_contract_os.grants.models import (
    EligibilityStatus,
    EligibilityResult,
    GrantAnalysis,
    GrantFitLevel,
    GrantOpportunity,
    GrantRecommendation,
)
from gov_contract_os.organizations import OrganizationProfile, ensure_grant_context

ADVANCED_MODEL_SCORE_THRESHOLD = 70


class GrantScoringWeights(BaseModel):
    """Weights that must sum to 100 (validated at load time)."""

    mission_alignment: float = 20
    program_alignment: float = 15
    population_alignment: float = 10
    geographic_fit: float = 10
    entity_eligibility: float = 15
    funding_amount_fit: float = 5
    allowable_cost_fit: float = 5
    organizational_capacity: float = 5
    outcomes_fit: float = 5
    application_effort: float = 5
    deadline_feasibility: float = 5


class GrantScoringThresholds(BaseModel):
    immediate_action: int = 85
    strong_candidate: int = 70
    monitor: int = 50


class GrantScoringConfig(BaseModel):
    weights: GrantScoringWeights = Field(default_factory=GrantScoringWeights)
    thresholds: GrantScoringThresholds = Field(default_factory=GrantScoringThresholds)

    def total_weight(self) -> float:
        w = self.weights
        return (
            w.mission_alignment
            + w.program_alignment
            + w.population_alignment
            + w.geographic_fit
            + w.entity_eligibility
            + w.funding_amount_fit
            + w.allowable_cost_fit
            + w.organizational_capacity
            + w.outcomes_fit
            + w.application_effort
            + w.deadline_feasibility
        )


def load_grant_scoring_config(path: Path | None = None) -> GrantScoringConfig:
    if path is None or not path.exists():
        return GrantScoringConfig()
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    config = GrantScoringConfig.model_validate(raw)
    total = config.total_weight()
    if abs(total - 100.0) > 0.01:
        raise ValueError(
            f"grant-scoring.yaml weights must sum to 100; got {total}. Path: {path}"
        )
    return config


# ---------------------------------------------------------------------------
# Individual criterion scorers - each returns (score, matched_hint, gap_hint).
# ---------------------------------------------------------------------------


@dataclass
class CriterionOutcome:
    score: float
    matched: str | None = None
    gap: str | None = None


def _lowerset(values: list[str]) -> set[str]:
    return {v.strip().lower() for v in values if v and v.strip()}


def _overlap_ratio(a: list[str], b: list[str]) -> float:
    aa, bb = _lowerset(a), _lowerset(b)
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa)


def _score_mission_alignment(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    if not grant.focus_areas or not org.focus_areas:
        return CriterionOutcome(
            score=weight * 0.5 if not grant.focus_areas else 0.0,
            gap=(
                "Grant focus_areas empty - cannot judge mission fit"
                if not grant.focus_areas
                else "Nonprofit profile has no focus_areas."
            ),
        )
    ratio = _overlap_ratio(grant.focus_areas, org.focus_areas)
    matched = sorted(_lowerset(grant.focus_areas) & _lowerset(org.focus_areas))
    if matched:
        return CriterionOutcome(
            score=weight * min(1.0, ratio * 2),  # any strong overlap gets full credit
            matched="Focus overlap: " + ", ".join(matched),
        )
    return CriterionOutcome(score=0.0, gap="No focus_areas overlap with nonprofit mission.")


def _score_program_alignment(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    if not org.programs:
        return CriterionOutcome(
            score=weight * 0.5, gap="Nonprofit profile has no programs listed."
        )
    grant_text = " ".join(
        [
            (grant.title or "").lower(),
            (grant.description or "").lower(),
            " ".join(grant.focus_areas).lower(),
        ]
    )
    hits = [p.name for p in org.programs if p.name and p.name.lower() in grant_text]
    if hits:
        return CriterionOutcome(
            score=weight, matched="Program name(s) referenced: " + ", ".join(hits)
        )
    # Partial: any of the nonprofit's focus areas showing up in grant text
    org_focus_hits = [
        f for f in org.focus_areas if f and f.lower() in grant_text
    ]
    if org_focus_hits:
        return CriterionOutcome(
            score=weight * 0.6,
            matched="Nonprofit focus area(s) present in grant text: " + ", ".join(org_focus_hits),
        )
    return CriterionOutcome(score=0.0, gap="No program-level signal in grant text.")


def _score_population_alignment(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    if not grant.populations_served or not org.populations_served:
        return CriterionOutcome(
            score=weight * 0.5,
            gap="Populations served missing on grant or nonprofit; needs human review.",
        )
    overlap = sorted(_lowerset(grant.populations_served) & _lowerset(org.populations_served))
    if overlap:
        return CriterionOutcome(
            score=weight, matched="Populations overlap: " + ", ".join(overlap)
        )
    return CriterionOutcome(
        score=0.0, gap="No overlap between grant populations and nonprofit populations."
    )


def _score_geographic_fit(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    # Eligibility already gated hard geographic mismatch. Here we just reward
    # tight overlap vs. broad national scope.
    if not grant.geographic_scope:
        return CriterionOutcome(
            score=weight * 0.5, gap="Grant geographic_scope not specified."
        )
    if _lowerset(grant.geographic_scope) & _lowerset(org.service_geographies):
        return CriterionOutcome(score=weight, matched="Direct geographic match.")
    # National scope but no direct city/state match -> partial
    return CriterionOutcome(
        score=weight * 0.6, matched="National/broad scope; nonprofit competes with wider field."
    )


def _score_entity_eligibility(
    grant: GrantOpportunity,
    org: OrganizationProfile,
    weight: float,
    eligibility: EligibilityResult,
) -> CriterionOutcome:
    if eligibility.status is EligibilityStatus.ELIGIBLE:
        return CriterionOutcome(score=weight, matched="Passes all hard eligibility checks.")
    if eligibility.status is EligibilityStatus.CONDITIONAL:
        return CriterionOutcome(
            score=weight * 0.5,
            gap=(
                "Conditional eligibility - action needed: "
                + "; ".join(eligibility.conditional_actions)
            ),
        )
    return CriterionOutcome(score=0.0, gap="Eligibility unknown.")


def _score_funding_amount_fit(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    ceiling = grant.award_ceiling
    floor = grant.award_floor
    min_pref = org.minimum_award
    max_pref = org.maximum_award
    if ceiling is None and floor is None:
        return CriterionOutcome(score=weight * 0.5, gap="Grant award size not specified.")
    if min_pref is None and max_pref is None:
        return CriterionOutcome(score=weight * 0.5, gap="Nonprofit funding preferences not set.")
    if min_pref is not None and ceiling is not None and ceiling < min_pref:
        return CriterionOutcome(
            score=0.0, gap=f"Award ceiling ${ceiling:,.0f} below nonprofit minimum ${min_pref:,.0f}."
        )
    if max_pref is not None and floor is not None and floor > max_pref:
        return CriterionOutcome(
            score=weight * 0.3,
            gap=f"Award floor ${floor:,.0f} exceeds nonprofit typical maximum ${max_pref:,.0f}.",
        )
    return CriterionOutcome(score=weight, matched="Award size within nonprofit preference.")


def _score_allowable_cost_fit(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    problems = []
    if grant.cost_share_required and org.accepts_matching_grants is False:
        problems.append("Nonprofit does not currently pursue matching-grant programs.")
    if (
        grant.indirect_cost_limit_percent is not None
        and grant.indirect_cost_limit_percent < 10
    ):
        problems.append(
            f"Indirect cost cap {grant.indirect_cost_limit_percent}% is unusually low."
        )
    if problems:
        return CriterionOutcome(score=weight * 0.4, gap="; ".join(problems))
    return CriterionOutcome(score=weight, matched="No red flags in cost structure.")


def _score_organizational_capacity(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    attestations = [
        org.has_501c3_determination_letter,
        org.has_audited_financials,
        org.has_board_list,
        org.has_nondiscrimination_policy,
    ]
    known_true = sum(1 for a in attestations if a is True)
    total = len(attestations)
    if all(a is None for a in attestations):
        return CriterionOutcome(
            score=weight * 0.5, gap="Organizational capacity attestations not set."
        )
    return CriterionOutcome(
        score=weight * (known_true / total),
        matched=f"{known_true}/{total} standard organizational-capacity attestations on file.",
    )


def _score_outcomes_fit(
    grant: GrantOpportunity, org: OrganizationProfile, weight: float
) -> CriterionOutcome:
    if not org.programs:
        return CriterionOutcome(
            score=weight * 0.5, gap="No documented program outcomes on nonprofit profile."
        )
    docs = [p for p in org.programs if p.outcomes]
    if not docs:
        return CriterionOutcome(
            score=weight * 0.3,
            gap="Programs present, but none list measurable outcomes.",
        )
    return CriterionOutcome(
        score=weight,
        matched=f"{len(docs)} program(s) with documented outcomes.",
    )


def _score_application_effort(
    grant: GrantOpportunity, weight: float
) -> CriterionOutcome:
    # Rough proxy: LOI/preapp programs = lower up-front effort; full application
    # with many required docs = higher effort.
    if grant.letter_of_inquiry_required or grant.preapplication_required:
        return CriterionOutcome(
            score=weight,
            matched="LOI / pre-application stage - lower initial effort to test fit.",
        )
    doc_count = len(grant.required_documents)
    if doc_count == 0:
        return CriterionOutcome(
            score=weight * 0.5,
            gap="Required documents not enumerated - true effort unclear.",
        )
    if doc_count <= 5:
        return CriterionOutcome(score=weight, matched=f"{doc_count} required documents.")
    return CriterionOutcome(
        score=weight * 0.4,
        gap=f"{doc_count} required documents - substantial application effort.",
    )


def _score_deadline_feasibility(
    grant: GrantOpportunity, weight: float, now: dt.datetime
) -> CriterionOutcome:
    deadline = grant.full_proposal_due_at or grant.loi_due_at
    if deadline is None:
        return CriterionOutcome(
            score=weight * 0.5, gap="No deadline recorded on grant."
        )
    days = (deadline - now).days
    if days < 0:
        return CriterionOutcome(score=0.0, gap="Deadline has passed.")
    if days < 7:
        return CriterionOutcome(score=weight * 0.2, gap=f"Only {days} days until deadline.")
    if days < 21:
        return CriterionOutcome(score=weight * 0.6, matched=f"{days} days until deadline.")
    return CriterionOutcome(score=weight, matched=f"{days} days until deadline - comfortable.")


# ---------------------------------------------------------------------------
# Top-level scorer
# ---------------------------------------------------------------------------


def _recommendation(
    fit_level: GrantFitLevel | None,
    eligibility: EligibilityResult,
) -> GrantRecommendation:
    if eligibility.status is EligibilityStatus.INELIGIBLE:
        return GrantRecommendation.DO_NOT_APPLY
    if eligibility.status is EligibilityStatus.UNKNOWN:
        return GrantRecommendation.REQUEST_CLARIFICATION
    if eligibility.status is EligibilityStatus.CONDITIONAL:
        # Look at conditional_actions to decide sub-recommendation.
        actions = " ".join(eligibility.conditional_actions).lower()
        if "fiscal sponsor" in actions:
            return GrantRecommendation.SEEK_FISCAL_SPONSOR
        if "partner" in actions:
            return GrantRecommendation.APPLY_WITH_PARTNER
        # Otherwise fall through to score-based routing.
    if fit_level is None:
        return GrantRecommendation.MONITOR
    if fit_level in (GrantFitLevel.IMMEDIATE_ACTION, GrantFitLevel.STRONG_CANDIDATE):
        return GrantRecommendation.APPLY
    if fit_level is GrantFitLevel.MONITOR:
        return GrantRecommendation.MONITOR
    return GrantRecommendation.DO_NOT_APPLY


def score_grant(
    grant: GrantOpportunity,
    nonprofit: OrganizationProfile,
    eligibility: EligibilityResult,
    config: GrantScoringConfig | None = None,
    now: dt.datetime | None = None,
) -> GrantAnalysis:
    """Score a grant against a nonprofit and produce a GrantAnalysis.

    Precondition: caller must have already run `check_grant_eligibility`.
    Ineligible grants get `fit_score=None` and DO_NOT_APPLY recommendation -
    they are intentionally not ranked against eligible ones.
    """
    ensure_grant_context(nonprofit)
    now = now or dt.datetime.now(dt.UTC)
    cfg = config or GrantScoringConfig()
    w = cfg.weights

    matched: list[str] = []
    gaps: list[str] = []

    if eligibility.status is EligibilityStatus.INELIGIBLE:
        return GrantAnalysis(
            grant_id=grant.id,
            nonprofit_slug=nonprofit.slug,
            eligibility=eligibility,
            fit_score=None,
            fit_level=None,
            recommendation=GrantRecommendation.DO_NOT_APPLY,
            matched_criteria=[],
            gaps=eligibility.hard_failures,
            risks=[],
            next_actions=["Archive - hard eligibility failure(s)."],
            requires_human_review=True,
            requires_advanced_model=False,
        )

    outcomes: list[CriterionOutcome] = [
        _score_mission_alignment(grant, nonprofit, w.mission_alignment),
        _score_program_alignment(grant, nonprofit, w.program_alignment),
        _score_population_alignment(grant, nonprofit, w.population_alignment),
        _score_geographic_fit(grant, nonprofit, w.geographic_fit),
        _score_entity_eligibility(grant, nonprofit, w.entity_eligibility, eligibility),
        _score_funding_amount_fit(grant, nonprofit, w.funding_amount_fit),
        _score_allowable_cost_fit(grant, nonprofit, w.allowable_cost_fit),
        _score_organizational_capacity(grant, nonprofit, w.organizational_capacity),
        _score_outcomes_fit(grant, nonprofit, w.outcomes_fit),
        _score_application_effort(grant, w.application_effort),
        _score_deadline_feasibility(grant, w.deadline_feasibility, now),
    ]

    total = 0.0
    for o in outcomes:
        total += o.score
        if o.matched:
            matched.append(o.matched)
        if o.gap:
            gaps.append(o.gap)

    score = max(0, min(100, round(total)))
    if score >= cfg.thresholds.immediate_action:
        fit_level = GrantFitLevel.IMMEDIATE_ACTION
    elif score >= cfg.thresholds.strong_candidate:
        fit_level = GrantFitLevel.STRONG_CANDIDATE
    elif score >= cfg.thresholds.monitor:
        fit_level = GrantFitLevel.MONITOR
    else:
        fit_level = GrantFitLevel.DO_NOT_APPLY

    recommendation = _recommendation(fit_level, eligibility)

    next_actions: list[str] = []
    if eligibility.missing_information:
        next_actions.append(
            "Fill in missing nonprofit profile fields: "
            + "; ".join(eligibility.missing_information)
        )
    if eligibility.conditional_actions:
        next_actions.extend(eligibility.conditional_actions)
    if recommendation in (
        GrantRecommendation.APPLY,
        GrantRecommendation.APPLY_WITH_PARTNER,
    ):
        next_actions.append(
            "Draft opportunity-summary.md and eligibility-matrix.csv under "
            "reports/grants/<grant-id>/; queue LLM Level-2 review."
        )

    return GrantAnalysis(
        grant_id=grant.id,
        nonprofit_slug=nonprofit.slug,
        eligibility=eligibility,
        fit_score=score,
        fit_level=fit_level,
        recommendation=recommendation,
        matched_criteria=matched,
        gaps=gaps,
        risks=[],
        next_actions=next_actions,
        requires_human_review=True,
        requires_advanced_model=score >= ADVANCED_MODEL_SCORE_THRESHOLD,
    )
