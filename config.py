"""
config.py — Centralised runtime configuration
==============================================

All project-specific values are read from environment variables (via .env
locally, or GitHub Secrets in CI). Defaults match the current project so
existing behaviour is unchanged out of the box.

To use a different project, repo, or state bucket:
  - Set the variables in .env  (local)
  - Add them as GitHub repository secrets  (CI/CD)
  - Or override in the Streamlit sidebar at runtime  (UI)
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    """Read an env var, stripping accidental whitespace."""
    return os.environ.get(key, default).strip()


# ── GCP Project ────────────────────────────────────────────────────────────────
GCP_PROJECT_ID: str = _get("GCP_PROJECT_ID", "gen-lang-client-0436480880")

# ── GCS State Backend ──────────────────────────────────────────────────────────
GCS_STATE_BUCKET: str = _get("GCS_STATE_BUCKET", "autoinfra-state")
# Namespace inside the bucket — defaults to project ID so projects never clash
GCS_STATE_PREFIX: str = _get("GCS_STATE_PREFIX", GCP_PROJECT_ID)

# ── GitHub Integration ─────────────────────────────────────────────────────────
GITHUB_PAT: str      = _get("GITHUB_PAT", "")
GITHUB_REPO: str     = _get("GITHUB_REPO", "santyautomates/ai-infra-provisioner")
GITHUB_WORKFLOW: str = _get("GITHUB_WORKFLOW", "provision.yml")

# ── AI / Gemini ────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str  = _get("GOOGLE_API_KEY", "")


def as_dict() -> dict:
    """Return all config as a dict (useful for passing to agents)."""
    return {
        "GCP_PROJECT_ID":    GCP_PROJECT_ID,
        "GCS_STATE_BUCKET":  GCS_STATE_BUCKET,
        "GCS_STATE_PREFIX":  GCS_STATE_PREFIX,
        "GITHUB_REPO":       GITHUB_REPO,
        "GITHUB_WORKFLOW":   GITHUB_WORKFLOW,
    }
