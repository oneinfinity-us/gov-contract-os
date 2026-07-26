from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from gov_contract_os.grants.eligibility import check_grant_eligibility
from gov_contract_os.grants.models import (
    EligibilityStatus,
    GrantFitLevel,
    GrantRecommendation,
)
from gov_contract_os.grants.scoring import (
    GrantScoringConfig,
    load_grant_scoring_config,
    score_grant,
)
from gov_contract_os.organizations import InvalidOrganizationContextError


def test_default_config_weights_sum_to_100():
    cfg = GrantScoringConfig()
    assert cfg.total_weight() == 100.0


def test_load_grant_scoring_config_from_repo_yaml():
    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "config" / "scoring" / "grant-scoring.yaml"
    cfg = load_grant_scoring_config(path)
    assert cfg.total_weight() == 100.0
    assert cfg.thresholds.immediate_action == 85


def test_load_grant_scoring_config_missing_path_returns_defaults(tmp_path):
    cfg = load_grant_scoring_config(tmp_path / "does-not-exist.yaml")
    assert isinstance(cfg, GrantScoringConfig)


def test_load_grant_scoring_config_rejects_bad_weight_sum(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "weights:\n"
        "  mission_alignment: 10\n"
        "  program_alignment: 10\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="sum to 100"):
        load_grant_scoring_config(bad)


def test_score_grant_strong_match_recommends_apply(make_grant, nonprofit_profile, now):
    grant = make_grant()
    eligibility = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert eligibility.status is EligibilityStatus.ELIGIBLE
    analysis = score_grant(grant, nonprofit_profile, eligibility, now=now)
    assert analysis.fit_score is not None
    assert analysis.fit_score >= 70
    assert analysis.fit_level in (
        GrantFitLevel.STRONG_CANDIDATE,
        GrantFitLevel.IMMEDIATE_ACTION,
    )
    assert analysis.recommendation is GrantRecommendation.APPLY
    assert analysis.requires_human_review is True
    assert analysis.requires_advanced_model is True  # score >= 70


def test_score_grant_ineligible_returns_none_score(make_grant, nonprofit_profile, now):
    grant = make_grant(invitation_only=True)
    eligibility = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert eligibility.status is EligibilityStatus.INELIGIBLE
    analysis = score_grant(grant, nonprofit_profile, eligibility, now=now)
    assert analysis.fit_score is None
    assert analysis.fit_level is None
    assert analysis.recommendation is GrantRecommendation.DO_NOT_APPLY


def test_score_grant_conditional_fiscal_sponsor_recommendation(
    make_grant, nonprofit_profile, now
):
    from gov_contract_os.grants.models import EligibleApplicantType

    grant = make_grant(
        eligible_applicants=[
            EligibleApplicantType.EDUCATIONAL_INSTITUTION,
            EligibleApplicantType.FISCAL_SPONSOR_ELIGIBLE,
        ]
    )
    eligibility = check_grant_eligibility(grant, nonprofit_profile, now=now)
    assert eligibility.status is EligibilityStatus.CONDITIONAL
    analysis = score_grant(grant, nonprofit_profile, eligibility, now=now)
    assert analysis.recommendation is GrantRecommendation.SEEK_FISCAL_SPONSOR


def test_score_grant_weak_mission_scores_low(make_grant, nonprofit_profile, now):
    grant = make_grant(
        title="Grant for oceanographic research",
        description="Funds oceanographic buoy deployment.",
        focus_areas=["oceanography", "marine biology"],
        populations_served=["marine researchers"],
    )
    eligibility = check_grant_eligibility(grant, nonprofit_profile, now=now)
    # Still eligible (501c3, national/WA overlap not blocked, etc.), but no mission match.
    analysis = score_grant(grant, nonprofit_profile, eligibility, now=now)
    assert analysis.fit_score is not None
    assert analysis.fit_score < 70
    assert analysis.recommendation in (
        GrantRecommendation.MONITOR,
        GrantRecommendation.DO_NOT_APPLY,
    )


def test_score_grant_identity_isolation(make_grant, consulting_profile, now):
    from gov_contract_os.grants.models import EligibilityResult, EligibilityStatus

    grant = make_grant()
    with pytest.raises(InvalidOrganizationContextError):
        score_grant(
            grant,
            consulting_profile,
            EligibilityResult(status=EligibilityStatus.UNKNOWN),
            now=now,
        )


def test_score_grant_conditional_deadline_flag_shows_up_in_next_actions(
    make_grant, nonprofit_profile, now
):
    grant = make_grant(full_proposal_due_at=now + dt.timedelta(days=3))
    eligibility = check_grant_eligibility(grant, nonprofit_profile, now=now)
    analysis = score_grant(grant, nonprofit_profile, eligibility, now=now)
    # Conditional actions include the deadline warning
    joined = " ".join(analysis.next_actions).lower()
    assert "3 days" in joined
