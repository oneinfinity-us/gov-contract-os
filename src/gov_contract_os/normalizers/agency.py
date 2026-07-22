"""Normalize agency names to a canonical form.

Different sources spell/abbreviate the same agency in different ways (e.g.
"Port of Seattle", "POS", "port-of-seattle"). Collectors should normalize
before constructing an Opportunity so dedupe/scoring/reporting can group by
agency reliably.
"""

from __future__ import annotations

_CANONICAL_AGENCIES = {
    "port of seattle": "Port of Seattle",
    "pos": "Port of Seattle",
    "washington state": "Washington State",
    "wa state": "Washington State",
    "state of washington": "Washington State",
    "king county": "King County",
    "city of seattle": "City of Seattle",
    "seattle": "City of Seattle",
    "city of bellevue": "City of Bellevue",
    "bellevue": "City of Bellevue",
}


def normalize_agency_name(raw_name: str) -> str:
    """Return the canonical agency name, or the trimmed input if unrecognized."""
    key = " ".join(raw_name.strip().lower().split())
    return _CANONICAL_AGENCIES.get(key, raw_name.strip())
