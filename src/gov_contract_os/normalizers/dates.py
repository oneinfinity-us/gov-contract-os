"""Normalize date/datetime strings from heterogeneous sources into aware datetimes."""

from __future__ import annotations

import datetime as dt

from dateutil import parser as dateutil_parser


def parse_date(value: str | dt.datetime | None) -> dt.datetime | None:
    """Parse a date/datetime string into a timezone-aware UTC datetime.

    Returns None for empty/unparseable input rather than raising, since
    government listings frequently have blank or malformed date fields.
    """
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        parsed = value
    else:
        try:
            parsed = dateutil_parser.parse(value)
        except (ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.UTC)
    return parsed
