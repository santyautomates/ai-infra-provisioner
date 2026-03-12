from google.adk import Agent
from google.adk.models import Gemini

def get_governance_agent(mcp_toolset):
    model = Gemini(model_name="gemini-2.5-flash")
    return Agent(
        name="Governance_Validator",
        description="Validates GCP plans against strict organizational policies.",
        instruction=(
            "You are a strict security, compliance, and DevOps auditor.\\n"
            "1. Call the `get_organizational_policies` tool to retrieve current standards.\\n"
            "2. Review the provided plan (which may contain gcloud commands, OR file contents like Dockerfiles/K8s YAML to be written).\\n"
            "3. Validation Rules:\\n"
            "   - **Regions**: Must match `allowed_regions`.\\n"
            "   - **Machine Types/Tiers**: Must match allowed policies.\\n"
            "   - **Naming**: Must STRICTLY match `naming_conventions`.\\n"
            "   - **DevOps Artifacts**: Any generated Dockerfile must use an approved base image from `devops_standards.docker_images`. Kubernetes manifest files (for GKE only, NOT Cloud Run) must include the fields listed in `devops_standards.kubernetes_requirements`. CI/CD files must target platforms in `devops_standards.ci_cd_allowed_platforms`.\\n"
            "   - **Cloud Run Security**: Cloud Run services may only allow unauthenticated invocations if `security_policies.allow_unauthenticated_cloudrun` is true.\\n"
            "4. For DELETION requests:\\n"
            "   - Use `list_gcp_resources` to confirm the resource exists before approving.\\n"
            "5. If compliant, output 'APPROVED: <justification>' AND YOU MUST EXACTLY REPEAT the entire execution plan (all gcloud commands and all file contents/code blocks provided by the planner) so the executor receives them.\\n"
            "6. If divergent in any way, output 'REJECTED: <reasons>'.\\n"
            "CRITICAL: Do not use the `run_code` tool. You must rely on existing tools."
        ),
        model=model,
        tools=[mcp_toolset]
    )
