"""
state_manager.py — GCS-backed infrastructure state
====================================================

Provides lightweight Terraform-like state tracking for provisioned resources.
State is stored as JSON files in a GCS bucket, namespaced by project_id so
multiple projects and repos can share the same central bucket safely.

Bucket layout:
  gs://[GCS_STATE_BUCKET]/[GCS_STATE_PREFIX]/[resource_name]/state.json
  gs://[GCS_STATE_BUCKET]/[GCS_STATE_PREFIX]/_index/all_resources.json

Usage:
  from state_manager import StateManager
  sm = StateManager()                          # uses config.py defaults
  sm = StateManager(project_id="other-proj")  # override for a specific project
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

import config as cfg

logger = logging.getLogger("state_manager")


class StateManager:
    """Manages infrastructure state in GCS. Falls back gracefully if unavailable."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        bucket: Optional[str] = None,
        prefix: Optional[str] = None,
    ):
        self.project_id = project_id or cfg.GCP_PROJECT_ID
        self.bucket     = bucket or cfg.GCS_STATE_BUCKET
        self.prefix     = prefix or cfg.GCS_STATE_PREFIX or self.project_id
        self._client    = None   # lazy-loaded

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _get_client(self):
        """Lazy-load the GCS client so import doesn't fail if SDK is missing."""
        if self._client is None:
            try:
                from google.cloud import storage  # type: ignore
                self._client = storage.Client(project=self.project_id)
            except Exception as e:
                logger.warning(f"GCS client unavailable: {e}. State features disabled.")
        return self._client

    def _blob_path(self, resource_name: str) -> str:
        return f"{self.prefix}/{resource_name}/state.json"

    def _index_path(self) -> str:
        return f"{self.prefix}/_index/all_resources.json"

    def _read_blob(self, blob_path: str) -> Optional[dict]:
        client = self._get_client()
        if not client:
            return None
        try:
            bucket = client.bucket(self.bucket)
            blob = bucket.blob(blob_path)
            if not blob.exists():
                return None
            return json.loads(blob.download_as_text())
        except Exception as e:
            logger.error(f"Error reading GCS blob {blob_path}: {e}")
            return None

    def _write_blob(self, blob_path: str, data: dict) -> bool:
        client = self._get_client()
        if not client:
            return False
        try:
            bucket = client.bucket(self.bucket)
            blob = bucket.blob(blob_path)
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type="application/json",
            )
            logger.info(f"State written to gs://{self.bucket}/{blob_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing GCS blob {blob_path}: {e}")
            return False

    # ── Public API ─────────────────────────────────────────────────────────────

    def read_state(self, resource_name: str) -> Optional[dict]:
        """
        Read the state for a specific resource.
        Returns None if the resource has never been provisioned.
        """
        return self._read_blob(self._blob_path(resource_name))

    def is_running(self, resource_name: str) -> bool:
        """
        Returns True if the resource exists in state with status=RUNNING.
        Use this for idempotency: skip provisioning if already RUNNING.
        """
        state = self.read_state(resource_name)
        return state is not None and state.get("status") == "RUNNING"

    def write_state(
        self,
        resource_name: str,
        resource_type: str,
        status: str = "RUNNING",
        region: Optional[str] = None,
        zone: Optional[str] = None,
        environment: Optional[str] = None,
        service: Optional[str] = None,
        labels: Optional[dict] = None,
        run_id: Optional[str] = None,
        repo: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> bool:
        """
        Write or update state for a resource after successful provisioning.

        Args:
            resource_name:  Full resource name, e.g. proj-dev-payments-vm
            resource_type:  e.g. compute_instance, cloud_run_service
            status:         RUNNING | FAILED | DELETED
            region / zone:  GCP location
            environment:    dev | stag | prod
            service:        Service name, e.g. payments
            labels:         Resource labels dict
            run_id:         GitHub Actions run ID
            repo:           GitHub repo (owner/repo)
            extra:          Any extra metadata to merge in
        """
        now = datetime.now(timezone.utc).isoformat()

        # Preserve created_at from existing state if it exists
        existing = self.read_state(resource_name)
        created_at = existing.get("created_at", now) if existing else now

        state: dict = {
            "resource_name":  resource_name,
            "resource_type":  resource_type,
            "project_id":     self.project_id,
            "status":         status,
            "created_at":     created_at,
            "last_modified":  now,
        }

        if region:      state["region"]      = region
        if zone:        state["zone"]        = zone
        if environment: state["environment"] = environment
        if service:     state["service"]     = service
        if labels:      state["labels"]      = labels
        if run_id:      state["run_id"]      = run_id
        if repo:        state["repo"]        = repo
        if extra:       state.update(extra)

        ok = self._write_blob(self._blob_path(resource_name), state)
        if ok:
            self._update_index(resource_name, resource_type, status)
        return ok

    def delete_state(self, resource_name: str) -> bool:
        """
        Mark a resource as DELETED in state (does not delete the GCS blob).
        The history is preserved; the resource is just marked as gone.
        """
        existing = self.read_state(resource_name)
        if not existing:
            logger.warning(f"delete_state: no existing state for {resource_name}")
            return False
        existing["status"]        = "DELETED"
        existing["last_modified"] = datetime.now(timezone.utc).isoformat()
        ok = self._write_blob(self._blob_path(resource_name), existing)
        if ok:
            self._update_index(resource_name, existing.get("resource_type", "unknown"), "DELETED")
        return ok

    def list_states(self, status_filter: Optional[str] = None) -> list[dict]:
        """
        List all resources managed by this state manager (for this prefix/project).
        Optionally filter by status: 'RUNNING', 'DELETED', 'FAILED'.
        """
        index = self._read_blob(self._index_path()) or {"resources": []}
        resources = index.get("resources", [])
        if status_filter:
            resources = [r for r in resources if r.get("status") == status_filter]
        return resources

    # ── Index management ───────────────────────────────────────────────────────

    def _update_index(self, resource_name: str, resource_type: str, status: str):
        """Keep the flat index file up to date for dashboard use."""
        index = self._read_blob(self._index_path()) or {"resources": []}
        resources: list = index.get("resources", [])

        # Update existing entry or append new
        for entry in resources:
            if entry.get("resource_name") == resource_name:
                entry["status"]        = status
                entry["last_modified"] = datetime.now(timezone.utc).isoformat()
                break
        else:
            resources.append({
                "resource_name":  resource_name,
                "resource_type":  resource_type,
                "project_id":     self.project_id,
                "status":         status,
                "last_modified":  datetime.now(timezone.utc).isoformat(),
            })

        index["resources"] = resources
        index["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._write_blob(self._index_path(), index)
