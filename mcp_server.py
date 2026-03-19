import json
import logging
import asyncio
from typing import Any

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Per-service policy modules
from policies.vm_policy import VM_POLICY

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Initialize FastMCP server
mcp = FastMCP("infra-governance-mcp")

# Global organisational policies.
# ─ VM-specific rules have been moved to policies/vm_policy.py (served via get_vm_policies()).
# ─ As each service gets its own policy module, its entries will be removed from here too.
POLICIES = {
    # Regions apply globally across all GCP services
    "allowed_regions": ["us-central1", "us-east1"],

    # SQL tiers — will be moved to policies/sql_policy.py in a future iteration
    "allowed_sql_tiers": ["db-f1-micro", "db-g1-small", "db-custom-1-3840"],

    # Naming conventions for all services EXCEPT VM (moved to vm_policy.py)
    "naming_conventions": {
        "gke":                "proj-[env]-[service]-cluster",
        "sql":                "proj-[env]-[service]-db",
        "bucket":             "proj-[env]-[service]-storage",
        "pubsub_topic":       "proj-[env]-[service]-topic",
        "pubsub_subscription":"proj-[env]-[service]-sub",
        "redis":              "proj-[env]-[service]-cache",
        "cloudrun":           "proj-[env]-[service]-cloudrun",
        "vpc":                "proj-[env]-[service]-vpc",
        "subnet":             "proj-[env]-[service]-subnet",
        "artifact_registry":  "proj-[env]-[service]-repo",
        "cloud_function":     "proj-[env]-[service]-fn",
        "secret":             "proj-[env]-[service]-secret",
        "iam_sa":             "proj-[env]-[service]-sa",
        "vertex_endpoint":    "proj-[env]-[service]-endpoint",
        "bigquery_dataset":   "proj_[env]_[service]_dataset",
        "bigquery_table":     "proj_[env]_[service]_table",
        "bigtable":           "proj-[env]-[service]-bt",
        "spanner":            "proj-[env]-[service]-spanner",
        "firestore":          "proj-[env]-[service]-firestore",
        "cloud_build_trigger":"proj-[env]-[service]-trigger",
        "load_balancer":      "proj-[env]-[service]-lb",
        "app_engine":         "proj-[env]-[service]-app",
        "memorystore":        "proj-[env]-[service]-cache",
        "monitoring_alert":   "proj-[env]-[service]-alert",
        "default_fallback":   "proj-[env]-[service]-[short_resource_name]",
    },

    # Cloud Run security — will move to cloud_run_policy.py later
    "security_policies": {
        "allow_unauthenticated_cloudrun": True,
    },

    "environments": ["dev", "stag", "prod"],

    "devops_standards": {
        "docker_images": [
            "alpine", "alpine:3.18",
            "debian-slim", "debian:12-slim",
            "node:18-alpine", "node:20-alpine",
            "python:3.11-slim", "python:3.10-slim", "python:3.12-slim",
            "gcr.io/google-samples/hello-app:1.0",
            "nginx:alpine",
            "openjdk:17-slim",
        ],
        "kubernetes_requirements": ["resources.limits", "resources.requests", "livenessProbe"],
        "ci_cd_allowed_platforms": [
            "github_actions", "gitlab_ci", "google_cloud_build",
            "jenkins", "circleci", "azure_pipelines",
            "aws_codepipeline", "travis_ci", "bitbucket_pipelines",
        ],
    },

    "approved_non_gcp_providers": {
        "cloud":           ["AWS", "Azure", "Firebase", "Supabase"],
        "edge_and_cdn":    ["Cloudflare"],
        "devops_artifacts": [
            "Dockerfile", "Kubernetes YAML", "CI/CD Pipeline",
            "Bash Script", "Terraform", "AWS CloudFormation",
            "Azure ARM Template", "Firebase CLI config",
        ],
        "agentic_patterns": [
            "Microservices Architecture", "Serverless Architecture",
            "Monolithic Architecture", "Event-Driven Architecture",
            "API-First Development", "DevOps and Continuous Delivery",
            "Agile Development", "TDD", "BDD", "DDD",
        ],
        "dev_environments": [
            "Python", "Node.js", "Go", "Java", "Rust", "C#", "Ruby", "PHP", "C++",
        ],
    },
}

@mcp.tool()
def get_organizational_policies() -> str:
    """
    Retrieve the standard organizational policies, naming conventions,
    allowed regions, and internal security guardrails for infrastructure provisioning.
    Use this for global/cross-service lookups (DevOps standards, non-GCP providers, etc.).
    For a specific GCP service, prefer the dedicated service policy tool (e.g. get_vm_policies).
    """
    logger.info("Fetching organizational policies via MCP")
    return json.dumps(POLICIES, indent=2)


@mcp.tool()
def get_vm_policies() -> str:
    """
    Retrieve the FULL governance policy for GCP Compute Engine VM provisioning.
    Use this tool whenever the user request involves creating, modifying, or deleting a VM.

    Returns detailed rules for:
    - Naming convention and regex pattern (proj-[env]-[service]-vm)
    - Allowed machine types per environment tier (dev/stag/prod)
    - Allowed regions and zones
    - Required OS image (debian-11, debian-cloud)
    - Network security (no public IP, OS Login)
    - Disk type and size limits
    - Required resource labels (env, service, managed-by)
    - Required API enablement steps
    - A ready-to-use gcloud command template
    - Deletion policy
    - Common rejection reasons with exact remediation steps
    """
    logger.info("Fetching VM-specific governance policies via MCP")
    return json.dumps(VM_POLICY, indent=2)

@mcp.tool()
def list_gcp_resources(resource_type: str = "networks") -> str:
    """
    List the actual GCP resources of a certain type currently in the project.
    Use this to verify names before deletion.
    Supported types: 'networks', 'instances', 'buckets', 'services', 'cloudruns',
    'clusters', 'sql', 'functions', 'artifacts', 'secrets'.
    """
    import subprocess
    import os
    logger.info(f"Listing GCP resources for type: {resource_type}")

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    p = f" --project={project_id}" if project_id else ""

    cmd_map = {
        "networks":   f"gcloud compute networks list --format=json{p}",
        "instances":  f"gcloud compute instances list --format=json{p}",
        "buckets":    f"gcloud storage ls --format=json{p}",
        "services":   f"gcloud services list --enabled --format=json{p}",
        "cloudruns":  f"gcloud run services list --format=json{p}",
        "clusters":   f"gcloud container clusters list --format=json{p}",
        "sql":        f"gcloud sql instances list --format=json{p}",
        "functions":  f"gcloud functions list --format=json{p}",
        "artifacts":  f"gcloud artifacts repositories list --format=json{p}",
        "secrets":    f"gcloud secrets list --format=json{p}",
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
