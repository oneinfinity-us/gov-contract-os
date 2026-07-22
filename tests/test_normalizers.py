from __future__ import annotations

import datetime as dt

from gov_contract_os.normalizers.agency import normalize_agency_name
from gov_contract_os.normalizers.amounts import parse_amount_range
from gov_contract_os.normalizers.dates import parse_date


def test_normalize_agency_name_known_variants():
    assert normalize_agency_name("port of seattle") == "Port of Seattle"
    assert normalize_agency_name("  WA State ") == "Washington State"
    assert normalize_agency_name("Seattle") == "City of Seattle"


def test_normalize_agency_name_unknown_passthrough():
    assert normalize_agency_name("  Some Other Agency ") == "Some Other Agency"


def test_parse_date_handles_iso_string():
    parsed = parse_date("2026-07-28T14:00:00-07:00")
    assert parsed is not None
    assert parsed.year == 2026 and parsed.month == 7 and parsed.day == 28


def test_parse_date_handles_none_and_empty():
    assert parse_date(None) is None
    assert parse_date("") is None


def test_parse_date_handles_naive_datetime_passthrough():
    naive = dt.datetime(2026, 1, 1)
    parsed = parse_date(naive)
    assert parsed is not None
    assert parsed.tzinfo is not None


def test_parse_date_unparseable_returns_none():
    assert parse_date("not a date at all !!!") is None


def test_parse_amount_range_dash_range():
    assert parse_amount_range("$50,000 - $100,000") == (50000.0, 100000.0)


def test_parse_amount_range_to_range():
    assert parse_amount_range("$50,000 to $100,000") == (50000.0, 100000.0)


def test_parse_amount_range_not_to_exceed():
    assert parse_amount_range("Not to exceed $200,000") == (None, 200000.0)


def test_parse_amount_range_single_amount():
    assert parse_amount_range("Estimated at $1,200,000") == (1200000.0, 1200000.0)


def test_parse_amount_range_k_and_m_suffixes():
    assert parse_amount_range("$50k - $1.2M") == (50000.0, 1200000.0)


def test_parse_amount_range_no_amount_found():
    assert parse_amount_range("No budget disclosed") == (None, None)


def test_parse_amount_range_none_input():
    assert parse_amount_range(None) == (None, None)
