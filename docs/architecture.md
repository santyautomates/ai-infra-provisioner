# AutoInfra — System Architecture & Configuration Guide

> **AutoInfra** is an AI-driven infrastructure provisioning platform that converts natural language requests into secure, compliant, and production-ready cloud infrastructure commands using an LLM-powered multi-agent pipeline.

---

## 📐 System Architecture Overview

The system follows a **3-Stage Agentic Pipeline** pattern:

```
User (Streamlit UI)
       │
       ▼
┌──────────────────────────────────────────────────────┐
│                   AutoInfra (app.py)                 │
│                                                      │
│   ┌─────────────┐  ┌───────────────┐  ┌──────────┐  │
│   │   Planner   │─▶│  Governance   │─▶│ Executor │  │
│   │    Agent    │  │     Agent     │  │   Agent  │  │
│   └─────┬───────┘  └──────┬────────┘  └────┬─────┘  │
│         │                 │                │         │
│         ▼                 ▼                ▼         │
│   ┌──────────────────────────────────────────────┐  │
│   │       MCP Server (mcp_server.py)             │  │
│   │  - get_organizational_policies               │  │
│   │  - list_gcp_resources                        │  │
│   │  - write_devops_artifact                     │  │
│   │  - execute_shell_command                     │  │
│   └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
       │                                   │
       ▼                                   ▼
  GitHub Actions                     Google Cloud
  (Remote CI/CD)                   (Live Resources)
```

---

## 🌐 Network Flow

### Local Execution Path

```
[User] ──► [Streamlit UI] ──► [Planner Agent]
                               │
                               ├──MCP call──► [MCP Server: get_organizational_policies]
                               ├──MCP call──► [MCP Server: list_gcp_resources]
                               │
                               ▼
                      [Governance Agent]
                               │
                               ├──MCP call──► [MCP Server: get_organizational_policies]
                               │
                        ┌── APPROVED ──┐
                        │             │
                        ▼             ▼ REJECTED ──► [UI Error]
                 [Executor Agent]
                        │
                        ├──► [tools.py: run_gcloud] ──► Google Cloud API
                        ├──► [MCP: write_devops_artifact] ──► ./generated_artifacts/
                        └──► [MCP: execute_shell_command] ──► Local Shell
```

### GitHub Actions Execution Path

```
[User] ──► [Streamlit "Deploy via GitHub" Button]
                │
                ▼
  [GitHub REST API: POST /dispatches]
                │
                ▼
  [GitHub Actions Runner: provision.yml]
                │
      ┌─────────┴──────────┐
      ▼                    ▼
  [Authenticate GCP]   [Install Deps from requirements.txt]
      │
      ▼
  [python main.py --request "..."]  ──► (Same 3-agent flow as local)
      │
      ▼
  [actions/upload-artifact]  ──► GitHub Artifacts (downloadable)
```

---

## ⚙️ Environment Variables Reference

All environment variables must be defined in a `.env` file at the project root. 

> **IMPORTANT**: Never commit `.env` to version control. It is included in `.gitignore`.

### Core Variables (Required)

| Variable | Description | Example Value |
|---|---|---|
| `GOOGLE_API_KEY` | Gemini API Key for Planner, Governance & Executor Agents. Obtained from [Google AI Studio](https://aistudio.google.com/). | `AIzaSyXXXXXXXXX` |
| `GOOGLE_CLOUD_PROJECT` | The GCP Project ID where resources will be provisioned. | `my-project-123` |
| `GOOGLE_CLOUD_LOCATION` | Default GCP region for resource creation. | `us-central1` |
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `true` to use Vertex AI instead of Gemini API directly. | `false` |

### Optional Variables

| Variable | Description | Example Value |
|---|---|---|
| `GITHUB_PAT` | GitHub Personal Access Token for triggering workflow dispatches from the UI. Pre-fills the sidebar PAT field. | `ghp_XXXXXXXXXXXXXX` |

### GitHub Actions Secrets (Required for Remote CI/CD)

Set these in your **GitHub Repository → Settings → Secrets and Variables → Actions**.

| Secret Name | Description |
|---|---|
| `GCP_SA_KEY` | JSON contents of your GCP Service Account key file with appropriate permissions. |
| `GOOGLE_API_KEY` | Same Gemini API Key as in your `.env` file. |

### Example `.env` File

```env
GOOGLE_API_KEY="your-gemini-api-key"
GOOGLE_CLOUD_PROJECT="gen-lang-client-XXXXXXXXXX"
GOOGLE_GENAI_USE_VERTEXAI="false"
GOOGLE_CLOUD_LOCATION="us-central1"
GITHUB_PAT="ghp_your_token_here"
```

---

## 🎛️ Configuration Panel Reference

The UI is organized into four tabs:

### ☁️ Tab 1: Cloud Systems

#### GCP Configuration
Provisions Google Cloud Platform resources via `gcloud` CLI commands.

| Sub-Service | Key Inputs | Naming Convention |
|---|---|---|
| Compute Engine | Instance Name, Machine Size (T-shirt), Zone, Image | `proj-[env]-[service]-vm` |
| Cloud Run | Service Name, Container Image, Memory | `proj-[env]-[service]-cloudrun` |
| Cloud SQL | Instance ID, DB Version (PG/MySQL), Tier | `proj-[env]-[service]-db` |
| GKE | Cluster Name, Node Size, Node Count | `proj-[env]-[service]-cluster` |
| Cloud Storage | Bucket Name, Storage Class | `proj-[env]-[service]-storage` |
| Pub/Sub | Topic Name | `proj-[env]-[service]-topic` |
| Memorystore (Redis) | Instance Name | `proj-[env]-[service]-cache` |
| VPC Network | VPC Name, Subnet Mode | `proj-[env]-[service]-vpc` |
| BigQuery | Dataset ID | `proj_[env]_[service]_dataset` |
| IAM | Principal (email), Role | `roles/service.role` |
| Cloud Functions | Function Name, Runtime, Trigger | `proj-[env]-[service]-fn` |
| Vertex AI | Endpoint Name, Model Type | `proj-[env]-[service]-endpoint` |
| Artifact Registry | Repo Name, Format (Docker/NPM) | `proj-[env]-[service]-repo` |
| Secret Manager | Secret ID | `proj-[env]-[service]-secret` |

#### AWS Configuration
Generates AWS CLI commands for core services including EC2, S3, RDS, Lambda, EKS, VPC, IAM, SQS, SNS, DynamoDB, CloudFront, Route 53, ElastiCache, ECS, and CloudWatch.

#### Azure Configuration
Generates Azure CLI commands for App Service, Networking, IAM, Database, Storage, DevOps, AI/ML, Monitoring, and Security.

#### Firebase Configuration
Sets up Firestore, Authentication, Cloud Functions, Hosting, Storage, Realtime Database, Analytics, Remote Config, Cloud Messaging, and A/B Testing.

#### Supabase Configuration
Configures Supabase projects with Database, Authentication, Storage, Edge Functions, and Realtime Subscriptions.

---

### 🚀 Tab 2: Pipeline & DevOps

#### Create CI/CD Pipeline
Generates pipeline configuration files for:
- **GitHub Actions** — `.github/workflows/pipeline.yml`
- **GitLab CI** — `.gitlab-ci.yml`
- **Jenkins** — `Jenkinsfile`
- **CircleCI** — `.circleci/config.yml`
- **Travis CI** — `.travis.yml`
- **Azure Pipelines** — `azure-pipelines.yml`
- **AWS CodePipeline** — Via CloudFormation
- **Google Cloud Build** — `cloudbuild.yaml`
- **Bitbucket Pipelines** — `bitbucket-pipelines.yml`

| Input | Description |
|---|---|
| Pipeline Name | Name for the CI/CD pipeline |
| Stages | Comma-separated list (e.g., `build, test, deploy`) |

#### Create Kubernetes Configuration
Generates Kubernetes manifests (Deployment, Service, Ingress, HPA).

| Input | Description |
|---|---|
| Deployment Name | Name of the K8s Deployment |
| Container Image | Image URI (e.g., `gcr.io/myproject/app:latest`) |
| Cluster Name | Target GKE cluster name |
| Namespaces | Target namespaces (e.g., `default, production`) |

#### Create Dockerfile
Generates a Dockerfile based on your specifications.

| Input | Description |
|---|---|
| Base Image | Must be from `devops_standards.docker_images` approved list |
| Packages | Python/Node/system packages to install |

#### Create Bash Script
Generates a shell script with error handling and comments.

| Input | Description |
|---|---|
| Script Purpose | Description of what the script does |
| Commands | Shell commands to include |

---

### 🤖 Tab 3: Agentic Apps

Enables AI-driven application design using software architecture patterns:

| Approach | Description |
|---|---|
| Microservices Architecture | Suite of small, independently deployable services |
| Serverless Architecture | Function-based compute without server management |
| Monolithic Architecture | Single unified application |
| Event-Driven Architecture | Event-triggered actions with message brokers |
| API-First Development | Design API contracts before implementation |
| DevOps & Continuous Delivery | CI/CD toolchain design and configuration |
| Agile Development | Sprint-based workflow with JIRA/Confluence |
| TDD | Test-first development with unit test scaffolding |
| BDD | Behavior specification with Cucumber/Gherkin |
| DDD | Domain-oriented bounded context design |

---

### 🔧 Tab 4: Other Tools

#### Cloudflare Configuration
Manages Cloudflare Workers, DNS records, WAF rules, CDN, SSL/TLS, and Rate Limiting.

#### Developer Configuration
Generates code scaffolding, README files, project structures, and developer environment setup.

---

## 🛡️ Governance Policy Engine

Policies are centrally stored and exposed by the **MCP Server** (`mcp_server.py`). All agents fetch these policies at runtime via the `get_organizational_policies` tool.

### Active Policy Rules

```json
{
  "allowed_regions": ["us-central1", "europe-west1", "asia-northeast1"],
  "allowed_machine_types": ["e2-micro", "e2-small", "e2-medium", "n1-standard-1"],
  "allowed_sql_tiers": ["db-f1-micro", "db-g1-small", "db-custom-1-3840"],
  "naming_conventions": {
    "vm": "proj-[env]-[service]-vm",
    "gke": "proj-[env]-[service]-cluster",
    "sql": "proj-[env]-[service]-db",
    "bucket": "proj-[env]-[service]-storage",
    "cloudrun": "proj-[env]-[service]-cloudrun",
    "vpc": "proj-[env]-[service]-vpc"
  },
  "security_policies": {
    "allow_public_ip": false,
    "allow_unauthenticated_cloudrun": true,
    "vm_default_image_family": "debian-11",
    "vm_default_image_project": "debian-cloud"
  }
}
```

### Policy Enforcement Matrix

| Policy | Enforced By | Action on Violation |
|---|---|---|
| Region compliance | Governance Agent | REJECTED |
| Naming convention | Governance Agent | REJECTED |
| No public IP on VM | Planner (proactive) + Governance (audit) | `--no-address` added / REJECTED if missing |
| Machine type limits | Governance Agent | REJECTED |
| Docker image allowlist | Governance Agent | REJECTED |
| K8s resource requirements | Governance Agent | REJECTED |
| Cloud Run auth policy | Governance Agent | REJECTED |

---

## 📁 Project File Structure

```
ai-infra-provisioner/
├── .env                         # Local environment variables (not committed)
├── .gitignore                   # Git exclusions
├── app.py                       # Main Streamlit UI application (~1100 lines)
├── main.py                      # CLI entry point for GitHub Actions
├── mcp_server.py                # MCP tool server (policies, gcloud listing)
├── tools.py                     # run_gcloud tool for the Executor Agent
├── requirements.txt             # Python dependencies
├── agents/
│   ├── planner/agent.py         # Infrastructure Planner Agent
│   ├── governance/agent.py      # Governance Validator Agent
│   └── executor/agent.py        # Infrastructure Executor Agent
├── scripts/
│   └── optimize_codebase.sh     # Housekeeping script (daily cron-safe)
├── generated_artifacts/         # Output: generated scripts, YAMLs, Dockerfiles
├── docs/
│   ├── architecture.md          # This document
│   ├── gcp_ui_parameters.md     # GCP service configuration reference
│   └── github_workflow_setup.md # GitHub secrets & CI/CD setup guide
└── .github/
    └── workflows/
        └── provision.yml        # GitHub Actions provisioning workflow
```

---

## 🚀 Local Setup & Running

```bash
# 1. Clone the repository
git clone https://github.com/santyautomates/ai-infra-provisioner.git
cd ai-infra-provisioner

# 2. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env   # Edit with your actual keys

# 5. Run the Streamlit UI
streamlit run app.py

# OR: Run from the CLI directly
python main.py --request "Create a Cloud Run service for payments in dev"
```

---

## 🔄 GitHub Actions CI/CD

The `.github/workflows/provision.yml` workflow:

1. Triggers via `workflow_dispatch` (manually or via Streamlit UI)
2. Sets up Python 3.11 on `ubuntu-latest`
3. Authenticates to GCP using `GCP_SA_KEY` secret
4. Runs `python main.py --request "..."` with the user's request
5. **Uploads all files from `generated_artifacts/`** as a downloadable artifact named `infrastructure-artifacts`

### Triggering via Streamlit
Set the following in the sidebar:
- **PAT**: Your GitHub Personal Access Token (with `workflow` scope)
- **Repository**: `your-org/ai-infra-provisioner`
- **Workflow Filename**: `provision.yml`

---

## 🧹 Housekeeping & Maintenance

A daily cron job can be scheduled to automatically clean up the project:

```bash
# Add to crontab (crontab -e)
0 0 * * * /path/to/ai-infra-provisioner/scripts/optimize_codebase.sh
```

The script removes:
- All `__pycache__/` directories
- `.pyc` compiled files
- `.DS_Store` system files
- Contents of `generated_artifacts/`
- Appends a timestamped entry to `optimization.log`

The same action can be triggered manually from the **🧺 Housekeeping** section in the Streamlit sidebar.
