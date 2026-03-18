import subprocess
import logging
import json
import os
from datetime import datetime, timezone
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

AUDIT_LOG_DIR = "audit_logs"

def _get_dated_log_path(filename: str) -> str:
    """Returns audit_logs/YYYY-MM-DD/<filename> for today's date (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_dir = os.path.join(AUDIT_LOG_DIR, today)
    os.makedirs(day_dir, exist_ok=True)
    return os.path.join(day_dir, filename)

def _write_audit_entry(entry: dict):
    """Append a single JSON audit record to today's gcloud_audit.log."""
    path = _get_dated_log_path("gcloud_audit.log")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

class GcloudCommandArgs(BaseModel):
    command: str = Field(
        ...,
        description="The full gcloud CLI command to execute, e.g. 'gcloud compute instances create ...'"
    )
    justification: str = Field(
        ...,
        description="A brief explanation of why this command is being run and how it complies with governance."
    )

def run_gcloud(args: GcloudCommandArgs) -> str:
    """
    Execute a validated gcloud command in the Google Cloud environment.
    This tool MUST be used to physically provision resources. Returning the command as JSON text is NOT sufficient.
    You must call this tool to execute the command.
    """
    # Security: Ensure it is actually a gcloud command
    cmd = args.command.strip()
    if not cmd.startswith("gcloud "):
        return "Error: Execution blocked. Only 'gcloud' commands are allowed."
    
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info(f"Executing: {cmd} | Justification: {args.justification}")

    audit_entry = {
        "timestamp": timestamp,
        "command": cmd,
        "justification": args.justification,
        "status": None,
        "stdout": None,
        "stderr": None,
    }

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Command executed successfully.")
        audit_entry["status"] = "SUCCESS"
        audit_entry["stdout"] = result.stdout
        _write_audit_entry(audit_entry)
        return f"SUCCESS\n\nstdout:\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        audit_entry["status"] = "FAILED"
        audit_entry["stdout"] = e.stdout
        audit_entry["stderr"] = e.stderr
        _write_audit_entry(audit_entry)
        return f"FAILED\n\nstderr:\n{e.stderr}\n\nstdout:\n{e.stdout}"
