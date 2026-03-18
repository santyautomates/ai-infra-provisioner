# AutoInfra — System Architecture & Configuration Guide

> **AutoInfra** is an AI-driven infrastructure provisioning platform that converts natural language requests into secure, compliant, and production-ready cloud infrastructure commands using an LLM-powered multi-agent pipeline.

---

## 📐 System Architecture Overview

The system follows a **3-Stage Agentic Pipeline** (`Think → Audit → Do`):

```
User (Streamlit UI / CLI)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   AutoInfra (app.py / main.py)          │
│                                                         │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │Infrastructure  │─▶│  Governance  │─▶│ Executor   │  │
│  │  Planner Agent │  │ Validator    │  │   Agent    │  │
│  └──────┬─────────┘  └──────┬───────┘  └─────┬──────┘  │
│         │                   │                │          │
│         ▼                   ▼                ▼          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         MCP Server (mcp_server.py)               │   │
│  │  • get_organizational_policies                   │   │
│  │  • list_gcp_resources (10 types)                 │   │
│  │  • write_devops_artifact                         │   │
│  │  • execute_shell_command                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
  GitHub Actions                    Google Cloud / AWS /
  (Remote CI/CD)                    Azure / Firebase / etc.
```

---

## 🌐 Network Flow

### Local Execution Path

```
[User] ──► [Streamlit UI] ──► [Planner Agent]
                               │
                               ├──MCP──► get_organizational_policies
                               ├──MCP──► list_gcp_resources (if deletion)
                               │
                               ▼
                      [Governance Agent]
                               │
                        ┌── TYPE A (GCP gcloud) ──────────────────────────┐
                        │   Validate: regions, naming, machine types,      │
                        │   SQL tiers, No Public IP, VM images             │
                        └── TYPE B (DevOps artifacts / non-GCP) ──────────┘
                            Validate: docker images, k8s fields, ci/cd platform
                               │
                        APPROVED ─────► [Executor Agent]
                        REJECTED ─────► [UI Error displayed]
                               │
                               ├──► [tools.py: run_gcloud] ──► GCP API
                               ├──► [MCP: write_devops_artifact] ──► ./generated_artifacts/
                               └──► [MCP: execute_shell_command] ──► chmod / local ops
```

### GitHub Actions Execution Path

```
[User] ──► [Streamlit "Deploy via GitHub" Button]
                │
                ▼
  [GitHub REST API: POST /repos/{owner}/{repo}/actions/workflows/{id}/dispatches]
                │
                ▼
  [GitHub Actions Runner: provision.yml]
                │
      ┌─────────┴──────────┐
      ▼                    ▼
  [Authenticate GCP]   [pip install -r requirements.txt]
      │
      ▼
  [python main.py --request "..."]  ──► (same 3-agent pipeline)
      │
      ▼
  [actions/upload-artifact@v4]  ──► Downloadable from Actions tab
```

---

## 🎛️ Feature Coverage Matrix

| Feature Category | Tab | Validated By | Output |
|---|---|---|---|
| GCP (20 services) | ☁️ Cloud | Governance: Type A | `gcloud` commands |
| AWS (8 service groups) | ☁️ Cloud | Governance: Type B | AWS CLI / CloudFormation |
| Azure (8 service groups) | ☁️ Cloud | Governance: Type B | Azure CLI / ARM |
| Firebase | ☁️ Cloud | Governance: Type B | Firebase CLI config |
| Supabase / Cloudflare | ☁️ Cloud | Governance: Type B | CLI config |
| CI/CD Pipelines (9 types) | 🚀 Pipeline | Governance: ci_cd_allowed_platforms | YAML file |
| Kubernetes YAML | 🚀 Pipeline | Governance: kubernetes_requirements | K8s manifest |
| Dockerfile | 🚀 Pipeline | Governance: docker_images | Dockerfile |
| Bash Script | 🚀 Pipeline | Pre-approved | .sh + chmod +x |
| Agentic App Design (10) | 🤖 Agentic | Pre-approved | Architecture + scaffolding |
| Cloudflare, Dev Config | 🔧 Other | Pre-approved | Config files |

---

## 🛡️ Governance Policy Engine

### Plan Classification (New in Current Version)

| Type | What it is | Rules Applied |
|---|---|---|
| **Type A** | GCP `gcloud` commands | Region ✓, Naming ✓, Machine types ✓, SQL tiers ✓, No Public IP ✓ |
| **Type B** | Everything else (CI/CD, Dockerfile, AWS, Azure, Firebase, scripts) | Docker base image ✓, K8s fields ✓, CI/CD platform allowlist ✓ |

### Naming Conventions (31 Rules)

| Resource | Convention |
|---|---|
| VM | `proj-[env]-[service]-vm` |
| GKE Cluster | `proj-[env]-[service]-cluster` |
| Cloud SQL | `proj-[env]-[service]-db` |
| Cloud Storage | `proj-[env]-[service]-storage` |
| Cloud Run | `proj-[env]-[service]-cloudrun` |
| VPC | `proj-[env]-[service]-vpc` |
| Artifact Registry | `proj-[env]-[service]-repo` |
| Cloud Function | `proj-[env]-[service]-fn` |
| Secret Manager | `proj-[env]-[service]-secret` |
| BigQuery Dataset | `proj_[env]_[service]_dataset` |
| Vertex AI Endpoint | `proj-[env]-[service]-endpoint` |
| IAM Service Account | `proj-[env]-[service]-sa` |
| Cloud Build Trigger | `proj-[env]-[service]-trigger` |
| Memorystore (Redis) | `proj-[env]-[service]-cache` |
| Load Balancer | `proj-[env]-[service]-lb` |
| Default (fallback) | `proj-[env]-[service]-[resource_name]` |
| + 15 more... | See `mcp_server.py POLICIES` |

### Allowed Values

| Policy | Values |
|---|---|
| Regions | `us-central1`, `europe-west1`, `asia-northeast1` |
| Machine Types | `e2-micro`, `e2-small`, `e2-medium`, `n1-standard-1` |
| SQL Tiers | `db-f1-micro`, `db-g1-small`, `db-custom-1-3840` |
| Docker Base Images | 12 approved images (see `mcp_server.py`) |
| CI/CD Platforms | 9 platforms (GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure Pipelines, AWS CodePipeline, GCB, Bitbucket, Travis CI) |
| Environments | `dev`, `stag`, `prod` |

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API key from [AI Studio](https://aistudio.google.com/) |
| `GOOGLE_CLOUD_PROJECT` | ✅ Yes | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | ✅ Yes | Default region (e.g. `us-central1`) |
| `GOOGLE_GENAI_USE_VERTEXAI` | Optional | Set `true` to use Vertex AI API |
| `GITHUB_PAT` | Optional | GitHub PAT with `workflow` scope for UI trigger |

---

## 📁 Project File Structure

```
ai-infra-provisioner/
├── .env                          # Local env vars (not committed)
├── app.py                        # Streamlit UI (~1180 lines)
├── main.py                       # CLI entrypoint for GitHub Actions
├── mcp_server.py                 # MCP policy server + tools
├── tools.py                      # run_gcloud tool wrapper
├── requirements.txt
├── agents/
│   ├── planner/agent.py          # Multi-cloud Planner (all 11 feature types)
│   ├── governance/agent.py       # Type A/B classifier + policy validator
│   └── executor/agent.py        # gcloud execution + artifact writer
├── scripts/
│   └── optimize_codebase.sh      # Housekeeping script (daily cron-safe)
├── generated_artifacts/          # Output: scripts, YAMLs, Dockerfiles
├── docs/
│   ├── architecture.md           # This document
│   ├── gcp_ui_parameters.md      # GCP service config reference
│   ├── multi_cloud_ui_parameters.md # AWS/Azure/Firebase/DevOps reference
│   ├── github_workflow_setup.md  # GitHub Secrets setup guide
│   └── demo_guide.md             # Onboarding & demo scenarios
└── .github/
    └── workflows/
        └── provision.yml         # GitHub Actions provisioning workflow
```

---

## 🔄 GitHub Actions CI/CD

Workflow triggers via `workflow_dispatch`. Steps:
1. Sets up Python 3.11 on `ubuntu-latest`
2. Authenticates to GCP with `GCP_SA_KEY` secret
3. Runs `python main.py --request "..."`
4. Uploads `generated_artifacts/` as downloadable `infrastructure-artifacts`

---

## 🧹 Housekeeping & Maintenance

```bash
# Daily cron (crontab -e)
0 0 * * * /path/to/ai-infra-provisioner/scripts/optimize_codebase.sh
```

Cleans: `__pycache__/`, `.pyc`, `.DS_Store`, `generated_artifacts/` contents. Logs to `optimization.log`.

Also available as the **🧺 Housekeeping** expander in the Streamlit sidebar.

---

## 🆕 UI Optimizations (Current Version)

| Feature | Description |
|---|---|
| Unique Session IDs | `uuid4()` per session — no concurrent user collision |
| 3-step Progress Bar | Real-time `⏳ Planning → ⏳ Governance → ⏳ Execution` |
| Dry Run Toggle | Preview commands without deploying anything |
| Pre-flight Checklist | Region/naming validation shown before submit |
| Request History Panel | Last 5 requests with status in sidebar |
| Copy-friendly Output | Execution results as `st.code(language="bash")` |
| Collapsible Sidebar | GitHub, Housekeeping, History all collapsed by default |
