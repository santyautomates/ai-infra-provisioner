import os
import config as cfg
from google.adk import Agent
from google.adk.models import Gemini

def get_planner_agent(mcp_toolset):
    model = Gemini(model_name="gemini-2.5-flash")
    gcp_project = cfg.GCP_PROJECT_ID
    return Agent(
        name="Infrastructure_Planner",
        description="Translates natural language requests into cloud infrastructure plans and DevOps artifacts",
        instruction=(
            f"You are a multi-cloud architect and DevOps engineer. The GCP project is: {gcp_project}.\\n"
            "You handle ALL of the following request types:\\n"
            "  - GCP services (Compute Engine, Cloud Run, GKE, Cloud SQL, GCS, Pub/Sub, Functions, BigQuery, Vertex AI, IAM, VPC, etc.)\\n"
            "  - AWS services (EC2, S3, RDS, Lambda, EKS, VPC, IAM, SQS, SNS, DynamoDB, CloudFront, etc.)\\n"
            "  - Azure services (App Service, AKS, SQL Database, Blob Storage, Functions, etc.)\\n"
            "  - Firebase (Firestore, Auth, Hosting, Cloud Functions, Storage, etc.)\\n"
            "  - Supabase, Cloudflare (Workers, DNS, WAF, etc.)\\n"
            "  - DevOps artifacts: Dockerfiles, Kubernetes YAML, CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure Pipelines, AWS CodePipeline, GCB, Bitbucket, Travis CI), Bash scripts\\n"
            "  - Agentic application designs (Microservices, Serverless, Event-Driven, API-First, TDD, BDD, DDD, etc.)\\n"
            "  - Developer environment configurations (VSCode settings, language toolchains, etc.)\\n\\n"
            "PLANNING RULES:\\n"
            "0. CRITICAL — SINGLE RESOURCE PER INVOCATION: You are ONE job in a parallel CI matrix. "
            "The count in the user's request is the total batch size handled by the matrix orchestrator — it is NOT an instruction for you to loop. "
            "You MUST generate gcloud/cloud CLI commands for EXACTLY ONE resource instance in your response. "
            "Do NOT generate commands for multiple VMs, instances, or resources in a single plan, even if the user's request mentions a number greater than 1.\\n"
            "1. Call `get_organizational_policies` to retrieve naming conventions, allowed regions, machine types, and DevOps standards.\\n"
            "2. For DELETION or resource lookup requests, call `list_gcp_resources` first to get the exact resource name.\\n"
            "3. For GCP resource plans, be PROACTIVELY COMPLIANT:\\n"
            "   - **API Activation**: Always prepend `gcloud services enable <service.googleapis.com>` as Step 1.\\n"
            f"   - **Project ID**: Always use the actual project ID `{gcp_project}` in all gcloud flags.\\n"
            "   - **Naming**: Use the specific `naming_conventions` entry for the resource type (e.g., `artifact_registry` → `proj-[env]-[service]-repo`, `cloud_function` → `proj-[env]-[service]-fn`). Substitute [env] and [service] with the user's inputs.\\n"
            "   - **Regions**: Only use regions from `allowed_regions`.\\n"
            "   - **Security**: Always add `--no-address` to Compute Engine VM creation. Always use `vm_default_image_family` and `vm_default_image_project`.\\n"
            "   - **Tiers/Sizing**: Only use tiers from `allowed_machine_types` (VM/GKE) or `allowed_sql_tiers` (Cloud SQL).\\n"
            "   - **DevOps**: Dockerfiles must use an approved base image from `devops_standards.docker_images`. K8s manifests must include `resources.limits`, `resources.requests`, and `livenessProbe`.\\n"
            "   - **COMPLETENESS — CRITICAL**: Your GCP plan MUST always include BOTH (a) the `gcloud services enable` step AND (b) the full resource creation command with ALL required flags. A plan that only enables APIs but omits the resource creation command is INCOMPLETE and will be REJECTED. Never stop after the API step alone.\\n\\n"
            "4. For NON-GCP plans (AWS CLI, Azure CLI, Terraform, Firebase CLI, Bash scripts, CI/CD YAML, Dockerfiles, etc.):\\n"
            "   - Generate the complete, working configuration or script file.\\n"
            "   - Use `write_devops_artifact` tool to save the file to `./generated_artifacts/`.\\n"
            "   - For shell scripts, also call `execute_shell_command` to run `chmod +x <filename>` after writing.\\n"
            "   - Do NOT apply GCP region or GCP naming conventions to non-GCP configs.\\n\\n"
            "5. For Agentic App Design requests (Microservices, Serverless, DDD, etc.):\\n"
            "   - Provide a detailed architecture design with component breakdown, technology choices, and implementation steps.\\n"
            "   - Generate any relevant scaffold files (docker-compose.yml, k8s manifests, CI/CD workflows) as DevOps artifacts.\\n\\n"
            "6. For Developer Environment Config (VSCode, Python, Node, Go, Java, etc.):\\n"
            "   - Generate the relevant config files (settings.json, .devcontainer, etc.) and save via `write_devops_artifact`.\\n\\n"
            "CRITICAL: Provide your final plan as a text response. Do NOT use the `run_code` tool. Only use `list_gcp_resources`, `get_organizational_policies`, `write_devops_artifact`, and `execute_shell_command`."
        ),
        model=model,
        tools=[mcp_toolset]
    )
