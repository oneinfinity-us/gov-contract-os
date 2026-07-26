"""Organization identity module.

The system may act on behalf of MORE THAN ONE legal entity (a consulting
business AND a 501(c)(3) nonprofit). This module defines the profile schema
and load helpers, plus the isolation rule that grants may only be pursued
under a nonprofit organization context (enforced in `grants.eligibility` /
CLI). See SECURITY.md.
"""

from gov_contract_os.organizations.profile import (
    InvalidOrganizationContextError,
    OrganizationProfile,
    OrganizationType,
    ensure_grant_context,
    load_organization_profile,
)

__all__ = [
    "InvalidOrganizationContextError",
    "OrganizationProfile",
    "OrganizationType",
    "ensure_grant_context",
    "load_organization_profile",
]
