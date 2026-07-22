"""Deterministic Level-1 scoring rules and weights.

This is intentionally NOT an LLM call - it's the fast, free, always-available
first pass described in CLAUDE.md's two-tier model workflow. Opportunities
that score high here get flagged `requires_advanced_model=True` for a Level-2
LLM pass (not implemented in this MVP round).

Weights sum to 100:
  ai_agent_copilot_azure        25
  software_dev_automation       15
  wa_seattle_local               10
  small_company_fit              10
  subcontracting_teaming         10
  demonstrable_tech_experience   10
  mandatory_requirements_met     10
  timeline_feasibility            10
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

# --- keyword categories -----------------------------------------------------


@dataclass(frozen=True)
class KeywordCategory:
    name: str
    weight: float
    keywords: tuple[str, ...]


AI_AGENT_COPILOT_AZURE = KeywordCategory(
    name="ai_agent_copilot_azure",
    weight=25.0,
    keywords=(
        "artificial intelligence",
        "generative ai",
        "genai",
        "copilot",
        "microsoft copilot",
        "azure",
        "ai agent",
        "agent",
        "agentic",
        "large language model",
        "llm",
        "machine learning",
        "chatbot",
        "cognitive services",
        " ai ",
    ),
)

SOFTWARE_DEV_AUTOMATION = KeywordCategory(
    name="software_dev_automation",
    weight=15.0,
    keywords=(
        "software development",
        "application development",
        "app development",
        "automation",
        "workflow automation",
        "system integration",
        "integration services",
        "api development",
        "cloud migration",
        "power platform",
        "power automate",
        "power apps",
        "devops",
        "application modernization",
        "custom software",
    ),
)

WA_SEATTLE_LOCAL = KeywordCategory(
    name="wa_seattle_local",
    weight=10.0,
    keywords=(
        "washington state",
        "seattle",
        "bellevue",
        "king county",
        "puget sound",
        "pacific northwest",
    ),
)

SUBCONTRACTING_TEAMING = KeywordCategory(
    name="subcontracting_teaming",
    weight=10.0,
    keywords=(
        "subcontract",
        "sub-contract",
        "subconsultant",
        "teaming",
        "joint venture",
        "mentor-protege",
        "mentor protege",
        "prime contractor may",
    ),
)

# Reused (at reduced weight) as a coarse proxy for "can we show relevant
# experience" - a real assessment needs company/capabilities.md + past
# performance, which belongs in skills/opportunity-review (human/LLM), not here.
DEMONSTRABLE_TECH_EXPERIENCE = KeywordCategory(
    name="demonstrable_tech_experience",
    weight=10.0,
    keywords=AI_AGENT_COPILOT_AZURE.keywords + SOFTWARE_DEV_AUTOMATION.keywords,
)

CAPABILITY_CATEGORIES: tuple[KeywordCategory, ...] = (
    AI_AGENT_COPILOT_AZURE,
    SOFTWARE_DEV_AUTOMATION,
    WA_SEATTLE_LOCAL,
    SUBCONTRACTING_TEAMING,
    DEMONSTRABLE_TECH_EXPERIENCE,
)

# Phrases where a keyword hit is likely a false positive (e.g. "agent" matching
# "insurance agent" rather than "AI agent"). Flagged, not silently dropped.
FALSE_POSITIVE_PHRASES: tuple[str, ...] = (
    "insurance agent",
    "travel agent",
    "real estate agent",
    "leasing agent",
    "customs agent",
    "purchasing agent",
    "special agent",
)

SMALL_COMPANY_FIT_WEIGHT = 10.0
MANDATORY_REQUIREMENTS_WEIGHT = 10.0
TIMELINE_FEASIBILITY_WEIGHT = 10.0

# Value above which a solicitation looks too large for a small firm to prime
# solo (still fine as a sub/teaming partner - see scorer.py role logic).
SMALL_COMPANY_VALUE_CEILING = 2_000_000.0


@dataclass
class CategoryScoreResult:
    score: float
    matched_keywords: list[str] = field(default_factory=list)
    likely_mismatch: bool = False


def score_capability_category(
    title: str, body: str, category: KeywordCategory
) -> CategoryScoreResult:
    """Keyword-weighted score for one category: title hits count double body hits.

    The score is capped via a ratio (not raw keyword count) so keyword-stuffing
    can't inflate a category past its weight, per CLAUDE.md scoring rules.
    """
    title_l = f" {title.lower()} "
    body_l = f" {(body or '').lower()} "

    matched: list[str] = []
    title_hits = 0
    body_hits = 0
    for kw in category.keywords:
        kw_norm = kw.strip()
        if not kw_norm:
            continue
        in_title = kw in title_l or kw_norm in title.lower()
        in_body = kw in body_l or kw_norm in (body or "").lower()
        if in_title:
            title_hits += 1
            matched.append(kw_norm)
        elif in_body:
            body_hits += 1
            matched.append(kw_norm)

    if title_hits == 0 and body_hits == 0:
        return CategoryScoreResult(score=0.0, matched_keywords=[], likely_mismatch=False)

    likely_mismatch = any(
        phrase in title.lower() or phrase in (body or "").lower()
        for phrase in FALSE_POSITIVE_PHRASES
    )

    raw = title_hits * 2 + body_hits
    capped_ratio = min(1.0, raw / 3.0)
    score = category.weight * capped_ratio
    if likely_mismatch:
        score *= 0.5
    return CategoryScoreResult(
        score=round(score, 2), matched_keywords=matched, likely_mismatch=likely_mismatch
    )


def score_small_company_fit(estimated_value_max: float | None) -> float:
    """Full credit when the opportunity is unsized or within a small firm's reach."""
    if estimated_value_max is None:
        return SMALL_COMPANY_FIT_WEIGHT * 0.5  # unknown -> neutral, needs human confirmation
    if estimated_value_max <= SMALL_COMPANY_VALUE_CEILING:
        return SMALL_COMPANY_FIT_WEIGHT
    return SMALL_COMPANY_FIT_WEIGHT * 0.25


def score_mandatory_requirements(mandatory_requirements: list[str]) -> float:
    """Level-1 cannot verify mandatory requirements against company profile - neutral
    default; a real assessment happens in skills/opportunity-review or a Level-2 pass.
    """
    del mandatory_requirements  # not yet used - reserved for a future rules-based check
    return MANDATORY_REQUIREMENTS_WEIGHT * 0.5


def score_timeline_feasibility(due_at: dt.datetime | None, now: dt.datetime) -> float:
    if due_at is None:
        return TIMELINE_FEASIBILITY_WEIGHT * 0.5
    days_remaining = (due_at - now).total_seconds() / 86_400
    if days_remaining < 0:
        return 0.0
    if days_remaining >= 21:
        return TIMELINE_FEASIBILITY_WEIGHT
    if days_remaining >= 10:
        return TIMELINE_FEASIBILITY_WEIGHT * 0.6
    return TIMELINE_FEASIBILITY_WEIGHT * 0.2
