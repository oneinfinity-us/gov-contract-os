"""Configuration loading.

Reads settings from environment variables (optionally populated from a local
.env file - see .env.example). Real secrets must never be committed; this
module only ever reads them, never writes/logs them.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "runtime" / "gov_contract_os.sqlite3"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE per line, '#' comments, no interpolation.

    Does not override variables already present in the real environment, and
    is not a replacement for a real secrets manager - just enough to read
    local dev values out of .env without adding a dependency.
    """
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    db_path: Path = DEFAULT_DB_PATH
    anthropic_api_key: str | None = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY") or None
    )
    openclaw_gateway_token: str | None = field(
        default_factory=lambda: os.environ.get("OPENCLAW_GATEWAY_TOKEN") or None
    )
    http_min_interval_seconds: float = 2.0
    http_timeout_seconds: float = 15.0

    # GovDelivery email-subscription connector settings. All optional; when the
    # required ones are unset the connector reports NOT_IMPLEMENTED (i.e. install
    # step incomplete) rather than crashing. Passwords MUST be app-specific /
    # scoped and MUST NOT be committed - see .env.example.
    govdelivery_imap_host: str | None = field(
        default_factory=lambda: os.environ.get("GCO_GOVDELIVERY_IMAP_HOST") or None
    )
    govdelivery_imap_port: int = field(
        default_factory=lambda: int(os.environ.get("GCO_GOVDELIVERY_IMAP_PORT") or "993")
    )
    govdelivery_imap_user: str | None = field(
        default_factory=lambda: os.environ.get("GCO_GOVDELIVERY_IMAP_USER") or None
    )
    govdelivery_imap_password: str | None = field(
        default_factory=lambda: os.environ.get("GCO_GOVDELIVERY_IMAP_PASSWORD") or None
    )
    govdelivery_imap_mailbox: str = field(
        default_factory=lambda: os.environ.get("GCO_GOVDELIVERY_IMAP_MAILBOX") or "INBOX"
    )
    govdelivery_lookback_days: int = field(
        default_factory=lambda: int(os.environ.get("GCO_GOVDELIVERY_LOOKBACK_DAYS") or "30")
    )


def get_settings() -> Settings:
    return Settings()
