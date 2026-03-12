import subprocess
import logging
from typing import TypedDict
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

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
    
    logger.info(f"Executing: {cmd} | Justification: {args.justification}")
    
    try:
        # Run the command
        # For safety in this demo, you could append `--dry-run` to certain commands, or just run it natively.
        # We will use subprocess.run with capture_output
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Command executed successfully.")
        return f"SUCCESS\\n\\ntdo_stdout:\\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return f"FAILED\\n\\nstderr:\\n{e.stderr}\\n\\nstdout:\\n{e.stdout}"
