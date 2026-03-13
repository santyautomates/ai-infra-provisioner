import json
import logging
import asyncio
from typing import Any

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Initialize FastMCP server
mcp = FastMCP("infra-governance-mcp")

# Organizational Policies (Mock Data)
POLICIES = {
    "allowed_regions": ["us-central1", "europe-west1", "asia-northeast1"],
    "allowed_machine_types": ["e2-micro", "e2-small", "e2-medium", "n1-standard-1"],
    "allowed_sql_tiers": ["db-f1-micro", "db-g1-small", "db-custom-1-3840"],
    "naming_conventions": {
        "vm": "proj-[env]-[service]-vm",
        "gke": "proj-[env]-[service]-cluster",
        "sql": "proj-[env]-[service]-db",
        "bucket": "proj-[env]-[service]-storage",
        "pubsub": "proj-[env]-[service]-topic",
        "redis": "proj-[env]-[service]-cache",
        "cloudrun": "proj-[env]-[service]-cloudrun",
        "vpc": "proj-[env]-[service]-vpc",
        "default_fallback": "proj-[env]-[service]-[short_resource_name]"
    },
    "security_policies": {
        "vm_default_image_family": "debian-11",
        "vm_default_image_project": "debian-cloud",
        "allow_public_ip": False,
        "allow_unauthenticated_cloudrun": True
    },
    "environments": ["dev", "stag", "prod"],
    "devops_standards": {
        "docker_images": ["alpine", "debian-slim", "node:18-alpine", "python:3.11-slim", "gcr.io/google-samples/hello-app:1.0"],
        "kubernetes_requirements": ["resources.limits", "resources.requests", "livenessProbe"],
        "ci_cd_allowed_platforms": ["github_actions", "gitlab_ci"]
    }
}

@mcp.tool()
def get_organizational_policies() -> str:
    """
    Retrieve the standard organizational policies, naming conventions,
    allowed regions, and internal security guardrails for infrastructure provisioning.
    """
    logger.info("Fetching organizational policies via MCP")
    return json.dumps(POLICIES, indent=2)

@mcp.tool()
def list_gcp_resources(resource_type: str = "networks") -> str:
    """
    List the actual GCP resources of a certain type currently in the project.
    Use this to verify names before deletion.
    Supported types: 'networks', 'instances', 'buckets', 'services'.
    """
    import subprocess
    import os
    logger.info(f"Listing GCP resources for type: {resource_type}")
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    project_flag = f" --project={project_id}" if project_id else ""
    
    cmd_map = {
        "networks": f"gcloud compute networks list --format=json{project_flag}",
        "instances": f"gcloud compute instances list --format=json{project_flag}",
        "buckets": f"gcloud storage ls --format=json{project_flag}",
        "services": f"gcloud services list --enabled --format=json{project_flag}"
    }
    
    cmd = cmd_map.get(resource_type)
    if not cmd:
        return f"Error: Unsupported resource type: {resource_type}"
        
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error listing resources: {e.stderr or str(e)}"
    except Exception as e:
        return f"Error listing resources: {str(e)}"

@mcp.tool()
def write_devops_artifact(filename: str, content: str) -> str:
    """
    Write a generated DevOps artifact (e.g. Dockerfile, deployment.yaml, script.sh) to the local disk.
    Files are saved in the './generated_artifacts' directory.
    """
    import os
    logger.info(f"Writing DevOps artifact: {filename}")
    
    target_dir = os.path.join(os.getcwd(), "generated_artifacts")
    os.makedirs(target_dir, exist_ok=True)
    
    # Simple sanitization to prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(target_dir, safe_filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote artifact to generated_artifacts/{safe_filename}"
    except Exception as e:
        return f"Error writing artifact: {str(e)}"

@mcp.tool()
def execute_shell_command(command: str) -> str:
    """
    Execute a shell command (e.g. chmod, ls, mkdir) within the './generated_artifacts' directory.
    Use this for setting permissions or managing local files.
    """
    import subprocess
    import os
    logger.info(f"Executing shell command: {command}")
    
    target_dir = os.path.join(os.getcwd(), "generated_artifacts")
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=target_dir, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return f"Success: {result.stdout}"
        else:
            return f"Error ({result.returncode}): {result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

if __name__ == "__main__":
    # Start the FastMCP server when ran directly
    mcp.run()
