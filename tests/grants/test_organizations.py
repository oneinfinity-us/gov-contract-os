from __future__ import annotations

from textwrap import dedent

import pytest

from gov_contract_os.organizations import (
    InvalidOrganizationContextError,
    OrganizationType,
    ensure_grant_context,
    load_organization_profile,
)


def test_load_nonprofit_profile_example_yaml():
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "organizations" / "nonprofit" / "organization-profile.example.yaml"
    profile = load_organization_profile(path)
    assert profile.type is OrganizationType.NONPROFIT
    assert profile.is_nonprofit()
    assert profile.tax_status == "501(c)(3)"
    assert profile.is_501c3()


def test_load_consulting_business_profile():
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / "organizations" / "consulting-business" / "organization-profile.example.yaml"
    profile = load_organization_profile(path)
    assert profile.type is OrganizationType.CONSULTING_BUSINESS
    assert not profile.is_nonprofit()
    assert not profile.is_501c3()


def test_ensure_grant_context_rejects_consulting_business(consulting_profile):
    with pytest.raises(InvalidOrganizationContextError):
        ensure_grant_context(consulting_profile)


def test_ensure_grant_context_accepts_nonprofit(nonprofit_profile):
    ensure_grant_context(nonprofit_profile)  # does not raise


def test_load_organization_profile_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_organization_profile(tmp_path / "nope.yaml")


def test_load_organization_profile_bad_shape(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text(dedent("- one\n- two\n"), encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_organization_profile(path)
