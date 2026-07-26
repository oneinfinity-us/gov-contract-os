"""Shared primitives used by both the procurement (contracts) and grants domains.

Keep this package deliberately small: only types/enums/utilities that BOTH
`gov_contract_os` (existing procurement code) and `gov_contract_os.grants`
legitimately need. Domain-specific logic belongs in its own subpackage.
"""
