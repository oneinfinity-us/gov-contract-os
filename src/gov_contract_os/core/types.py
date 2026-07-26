"""Cross-domain enums.

`OpportunityType` is the single source of truth for what kind of funding
opportunity a row represents. The existing procurement `Opportunity` model in
`gov_contract_os.models.opportunity` is implicitly `GOVERNMENT_CONTRACT`; the
new `GrantOpportunity` model in `gov_contract_os.grants.models` sets one of
the grant types explicitly.
"""

from __future__ import annotations

from enum import StrEnum


class OpportunityType(StrEnum):
    GOVERNMENT_CONTRACT = "government_contract"
    GOVERNMENT_GRANT = "government_grant"
    FOUNDATION_GRANT = "foundation_grant"
    CORPORATE_GRANT = "corporate_grant"
    SPONSORSHIP = "sponsorship"
    PARTNERSHIP = "partnership"


GRANT_TYPES: frozenset[OpportunityType] = frozenset(
    {
        OpportunityType.GOVERNMENT_GRANT,
        OpportunityType.FOUNDATION_GRANT,
        OpportunityType.CORPORATE_GRANT,
    }
)


def is_grant_type(opportunity_type: OpportunityType) -> bool:
    return opportunity_type in GRANT_TYPES
