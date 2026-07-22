"""Unified Analysis data model - the output of scoring/analyzers for one Opportunity."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class FitLevel(StrEnum):
    IMMEDIATE_ATTENTION = "immediate_attention"  # 85-100
    WORTH_ANALYZING = "worth_analyzing"  # 70-84
    WATCH = "watch"  # 50-69
    USUALLY_SKIP = "usually_skip"  # 0-49


class RecommendedRole(StrEnum):
    PRIME = "prime"
    SUBCONTRACTOR = "subcontractor"
    TEAMING_PARTNER = "teaming_partner"
    NO_BID = "no_bid"


class Analysis(BaseModel):
    opportunity_id: str
    fit_score: int = Field(ge=0, le=100)
    fit_level: FitLevel
    recommended_role: RecommendedRole

    matched_capabilities: list[str] = Field(default_factory=list)
    capability_gaps: list[str] = Field(default_factory=list)
    mandatory_requirement_risks: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)

    requires_human_review: bool = True
    requires_advanced_model: bool = False
    analysis_version: str = "0.1.0"

    @staticmethod
    def fit_level_for_score(score: int) -> FitLevel:
        if score >= 85:
            return FitLevel.IMMEDIATE_ATTENTION
        if score >= 70:
            return FitLevel.WORTH_ANALYZING
        if score >= 50:
            return FitLevel.WATCH
        return FitLevel.USUALLY_SKIP
