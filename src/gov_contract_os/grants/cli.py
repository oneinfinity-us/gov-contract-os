"""Typer CLI for the grants domain.

Mounted under `gov_contract_os.cli.app` as the `grants` subcommand:
    python -m gov_contract_os grants import <inbox-folder>
    python -m gov_contract_os grants screen --nonprofit <slug> [--new]
    python -m gov_contract_os grants list

`--nonprofit` is REQUIRED for anything that produces an analysis or decision -
identity isolation (SECURITY.md) is enforced at this layer, not later.
"""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from gov_contract_os.config import REPO_ROOT, get_settings
from gov_contract_os.grants.eligibility import check_grant_eligibility
from gov_contract_os.grants.importer import import_grant_from_manifest
from gov_contract_os.grants.scoring import load_grant_scoring_config, score_grant
from gov_contract_os.grants.storage import (
    list_grants,
    list_grants_without_analysis,
    upsert_grant,
    upsert_grant_analysis,
)
from gov_contract_os.organizations import (
    InvalidOrganizationContextError,
    load_organization_profile,
)
from gov_contract_os.storage.db import get_engine, init_db, make_session_factory, session_scope

logger = logging.getLogger("gov_contract_os.grants.cli")

grants_app = typer.Typer(
    help=(
        "Grant opportunity discovery, eligibility, and scoring. "
        "Requires --nonprofit for any analysis command (identity isolation)."
    ),
)


def _session_factory():
    settings = get_settings()
    engine = get_engine(settings.db_path)
    # Ensure ORM models for both procurement AND grants are registered before
    # create_all() runs. Importing this module is enough because it declares
    # tables against `Base.metadata`.
    from gov_contract_os.grants import schema as _grants_schema  # noqa: F401

    init_db(engine)
    return make_session_factory(engine)


def _nonprofit_profile_path(slug: str) -> Path:
    return REPO_ROOT / "organizations" / slug / "organization-profile.yaml"


def _grant_scoring_config_path() -> Path:
    return REPO_ROOT / "config" / "scoring" / "grant-scoring.yaml"


def _load_nonprofit(slug: str):
    path = _nonprofit_profile_path(slug)
    try:
        profile = load_organization_profile(path)
    except FileNotFoundError as exc:
        typer.echo(f"Nonprofit profile not found: {path}")
        typer.echo(
            "Create the profile from the example at "
            "organizations/nonprofit/organization-profile.example.yaml"
        )
        raise typer.Exit(code=2) from exc
    if not profile.is_nonprofit():
        typer.echo(
            f"Organization {slug!r} has type={profile.type.value!r}, but grant "
            "commands require a nonprofit context. See SECURITY.md."
        )
        raise typer.Exit(code=2)
    return profile


@grants_app.command("import")
def grants_import(
    path: Path = typer.Argument(
        ...,
        help=(
            "Path to a manifest.yaml OR an inbox folder that contains one. "
            "Example: opportunities/grants/inbox/example-grant/"
        ),
    ),
) -> None:
    """Import a single grant record from a manifest.yaml under the grants inbox."""
    manifest_path = path if path.is_file() else path / "manifest.yaml"
    grant = import_grant_from_manifest(manifest_path)

    session_factory = _session_factory()
    with session_scope(session_factory) as session:
        _, created = upsert_grant(session, grant)
    typer.echo(
        f"{'+ new' if created else '~ updated'} grant: {grant.title} "
        f"(id={grant.id}, funder={grant.funder_name})"
    )


@grants_app.command("screen")
def grants_screen(
    nonprofit: str = typer.Option(
        ..., "--nonprofit", help="Nonprofit slug (matches organizations/<slug>/)."
    ),
    new: bool = typer.Option(
        False, "--new", help="Screen only grants without an analysis for this nonprofit."
    ),
) -> None:
    """Run eligibility + Level-1 scoring for stored grants against a nonprofit."""
    profile = _load_nonprofit(nonprofit)
    config = load_grant_scoring_config(_grant_scoring_config_path())

    session_factory = _session_factory()
    with session_scope(session_factory) as session:
        if new:
            grants = list_grants_without_analysis(session, nonprofit)
        else:
            grants = list_grants(session)
        typer.echo(f"Screening {len(grants)} grant(s) for nonprofit={nonprofit!r}")
        for grant in grants:
            try:
                eligibility = check_grant_eligibility(grant, profile)
                analysis = score_grant(grant, profile, eligibility, config=config)
            except InvalidOrganizationContextError as exc:
                # Should not happen because we already validated above, but be defensive.
                typer.echo(f"  ! aborted for {grant.title}: {exc}")
                raise typer.Exit(code=2) from exc
            upsert_grant_analysis(session, analysis)
            score_display = (
                f"score={analysis.fit_score}"
                if analysis.fit_score is not None
                else "score=n/a (ineligible)"
            )
            typer.echo(
                f"  {grant.title}: eligibility={analysis.eligibility.status.value} "
                f"{score_display} recommendation={analysis.recommendation.value}"
            )


@grants_app.command("list")
def grants_list() -> None:
    """List all stored grants (no analysis - just the raw catalog)."""
    session_factory = _session_factory()
    with session_scope(session_factory) as session:
        grants = list_grants(session)
    if not grants:
        typer.echo("No grants stored yet. Try `grants import <inbox-folder>`.")
        return
    for grant in grants:
        due = grant.full_proposal_due_at or grant.loi_due_at
        due_s = due.date().isoformat() if due else "unknown"
        typer.echo(f"  {due_s}  {grant.funder_name} :: {grant.title} ({grant.id})")


@grants_app.command("prepare-application")
def grants_prepare_application(
    grant_id: str = typer.Argument(...),
    nonprofit: str = typer.Option(..., "--nonprofit"),
) -> None:
    """Scaffold a grant-application workspace. NOT IMPLEMENTED in Phase 1."""
    _load_nonprofit(nonprofit)  # still validate context
    typer.echo(
        f"prepare-application is not implemented in Phase 1 (grant_id={grant_id}, "
        f"nonprofit={nonprofit}). Planned for Phase 4 - see docs/architecture.md."
    )
    raise typer.Exit(code=2)


@grants_app.command("validate-budget")
def grants_validate_budget(
    grant_id: str = typer.Argument(...),
    nonprofit: str = typer.Option(..., "--nonprofit"),
) -> None:
    """Validate a grant budget draft. NOT IMPLEMENTED in Phase 1."""
    _load_nonprofit(nonprofit)
    typer.echo(
        f"validate-budget is not implemented in Phase 1 (grant_id={grant_id}, "
        f"nonprofit={nonprofit}). Planned for Phase 4."
    )
    raise typer.Exit(code=2)
