"""Normalize free-text dollar amounts into a (min, max) float range.

Handles common government listing phrasings such as:
  "$50,000 - $100,000", "$50,000 to $100,000", "Not to exceed $200,000",
  "Estimated at $1.2M", "$75,000".
Anything unrecognized returns (None, None) rather than guessing.
"""

from __future__ import annotations

import re

_RANGE_RE = re.compile(
    r"\$?\s*([\d,.]+)\s*([kKmM]?)\s*(?:-|to|through)\s*\$?\s*([\d,.]+)\s*([kKmM]?)"
)
_NOT_TO_EXCEED_RE = re.compile(r"not\s+to\s+exceed\s*\$?\s*([\d,.]+)\s*([kKmM]?)", re.IGNORECASE)
_SINGLE_AMOUNT_RE = re.compile(r"\$\s*([\d,.]+)\s*([kKmM]?)")

_MULTIPLIERS = {"": 1.0, "k": 1_000.0, "m": 1_000_000.0}


def _to_float(number: str, suffix: str) -> float:
    return float(number.replace(",", "")) * _MULTIPLIERS[suffix.lower()]


def parse_amount_range(text: str | None) -> tuple[float | None, float | None]:
    if not text:
        return (None, None)

    range_match = _RANGE_RE.search(text)
    if range_match:
        low = _to_float(range_match.group(1), range_match.group(2))
        high = _to_float(range_match.group(3), range_match.group(4))
        return (min(low, high), max(low, high))

    not_to_exceed_match = _NOT_TO_EXCEED_RE.search(text)
    if not_to_exceed_match:
        high = _to_float(not_to_exceed_match.group(1), not_to_exceed_match.group(2))
        return (None, high)

    single_match = _SINGLE_AMOUNT_RE.search(text)
    if single_match:
        value = _to_float(single_match.group(1), single_match.group(2))
        return (value, value)

    return (None, None)
