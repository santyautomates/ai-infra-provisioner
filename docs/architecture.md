# DevSecOps AI Infra Provisioner — System Architecture & Configuration Guide

> **DevSecOps AI Infra Provisioner** is an AI-driven, security-first cloud infrastructure provisioning platform that converts natural language requests into secure, compliant, and production-ready cloud infrastructure via an automated GitHub Actions pipeline.

---

## 📐 System Architecture Overview

The system follows a **3-Stage Agentic Pipeline** (`Think → Audit → Do`), triggered exclusively through GitHub Actions:

```
User (Streamlit UI — 🤖 AI Assistant tab)
         │  Types natural language: "VM for payments in dev"
         ▼
┌─────────────────────────────────────────────────────────┐
│          DevSecOps AI Infra Provisioner (app.py)        │
│                                                         │
│   ui_policy_defaults.py ──► Policy Preview Panel        │
│   (shows locked/editable params from vm_policy.py)      │
│   User tweaks params → Confirms                         │
│                                                         │
│   GitHub PAT + Repo Config ──► GitHub REST API          │
│   🚀 Deploy via GitHub Actions                          │
└─────────────────────────────────────────────────────────┘
         │
         ▼  (workflow_dispatch)
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions: provision.yml              │
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
│  │  • get_vm_policies                               │   │
│  │  • list_gcp_resources (10 types)                 │   │
│  │  • write_devops_artifact                         │   │
│  │  • execute_shell_command                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
  Generated Artifacts                 Google Cloud / AWS / Azure
  (uploaded to Actions tab)           (actual resource creation)
```

---

## 🌐 Execution Flow — GitHub Actions Only

> ⚠️ **DevSecOps Principle**: There is NO local execution path. All infrastructure changes are version-controlled, auditable, and executed through GitHub Actions.

```
[User] ──► [Streamlit UI: "Deploy via GitHub Actions"]
                │
                ▼
  [GitHub REST API: POST /repos/{owner}/{repo}/actions/workflows/{id}/dispatches]
                │
                ▼
  [GitHub Actions Runner: provision.yml]
                │
      ┌─────────┴──────────────────────┐
      │   Parallel Matrix (N instances) │
      │   (1 to 10 in parallel)        │
      └─────────┬──────────────────────┘
                │
                ▼
  [Authenticate GCP] + [pip install -r requirements.txt]
                │
                ▼
  [python main.py --request "..." --index N --count N]
                │
                ▼  (3-agent pipeline)
  ┌──────────────────────────────────┐
  │  Step 1: Planner Agent           │ ──► Creates detailed gcloud/CLI plan
  │  Step 2: Governance Validator    │ ──► APPROVED or REJECTED (policy check)
  │  Step 3: Executor Agent          │ ──► Runs commands, writes artifacts
  └──────────────────────────────────┘
                │
                ▼
  [actions/upload-artifact@v4]
  ├── infrastructure-artifacts-N    (generated_artifacts/*.json, *.txt, *.yaml)
  └── audit-logs-instance-N        (audit_logs/YYYY-MM-DD/audit_summary.log)
```

---

## 🎛️ Feature Coverage Matrix

| Feature Category | Tab | Validated By | Output |
|---|---|---|---|
| GCP (20+ services) | ☁️ Cloud Systems | Governance: Type A | `gcloud` commands |
| AWS (8 service groups) | ☁️ Cloud Systems | Governance: Type B | AWS CloudFormation / CLI |
| Azure (8 service groups) | ☁️ Cloud Systems | Governance: Type B | Azure ARM / CLI |
| GitHub Actions CI/CD | 🚀 Pipeline & DevOps | Governance: ci_cd_allowed | YAML workflow |
| Kubernetes YAML | 🚀 Pipeline & DevOps | Governance: kubernetes_requirements | K8s manifest |
| Dockerfile | 🚀 Pipeline & DevOps | Governance: docker_images | Dockerfile |
| Bash Script | 🚀 Pipeline & DevOps | Pre-approved | .sh + chmod +x |
| Agentic App Design | 🤖 Agentic Apps | Pre-approved | Architecture + scaffolding |

---

## 🛡️ Governance Policy Engine

### Plan Classification

| Type | What it is | Rules Applied |
|---|---|---|
| **Type A** | GCP `gcloud` commands | Region ✓, Naming ✓, Machine types ✓, SQL tiers ✓, No Public IP ✓ |
| **Type B** | DevOps artifacts (CI/CD, Dockerfile, AWS, Azure, scripts) | Docker base image ✓, K8s fields ✓, CI/CD platform allowlist ✓ |

### VM Naming Convention (with Parallel Support)

| Scenario | Convention | Example |
|---|---|---|
| Single instance | `proj-[env]-[service]-vm` | `proj-dev-payments-vm` |
| Parallel instances | `proj-[env]-[service]-vm-[N]` | `proj-dev-payments-vm-1` |

> The system auto-injects the `-N` suffix when `INSTANCE_COUNT > 1`. Governance approves these names automatically.

### Naming Conventions (All Resources)

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
| Default (fallback) | `proj-[env]-[service]-[resource_name]` |

### Allowed Values

| Policy | Values |
|---|---|
| Regions | `us-central1`, `europe-west1`, `asia-northeast1` |
| VM Machine Types | `e2-micro`, `e2-small`, `e2-medium`, `n1-standard-1/2/4`, `n2-standard-2` |
| SQL Tiers | `db-f1-micro`, `db-g1-small`, `db-custom-1-3840` |
| Docker Base Images | 12 approved images (see `mcp_server.py`) |
| CI/CD Platform | GitHub Actions only (UI-enforced) |
| Environments | `dev`, `stag`, `prod` |

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API key from [AI Studio](https://aistudio.google.com/) |
| `GOOGLE_CLOUD_PROJECT` | ✅ Yes | GCP project ID |
| `GITHUB_PAT` | ✅ Yes | GitHub PAT with `workflow` + `actions:read` scope |

---

## 📁 Project File Structure

```
ai-infra-provisioner/
├── .env                          # Local env vars (not committed)
├── app.py                        # Streamlit UI — AI Infra Provisioner
├── ui_policy_defaults.py         # 🆕 Policy defaults helper for AI Assistant tab
├── main.py                       # CLI entrypoint for GitHub Actions runner
├── mcp_server.py                 # MCP policy server + tools
├── tools.py                      # run_gcloud tool wrapper
├── requirements.txt
├── agents/
│   ├── planner/agent.py          # Infrastructure Planner (GCP + DevOps artifacts)
│   ├── governance/agent.py       # Type A/B classifier + policy validator
│   └── executor/agent.py        # gcloud execution + artifact writer
├── policies/
│   └── vm_policy.py             # VM-specific governance rules
├── scripts/
│   └── optimize_codebase.sh     # Housekeeping script
├── generated_artifacts/         # Output: JSON reports, TXT reports, YAMLs
├── audit_logs/                  # Daily audit trail (YYYY-MM-DD/audit_summary.log)
├── backups/
│   └── v4/                      # Pre-DevSecOps redesign backup
├── docs/
│   ├── architecture.md          # This document
│   ├── gcp_ui_parameters.md     # GCP service config reference
│   ├── multi_cloud_ui_parameters.md # AWS/Azure/DevOps reference
│   ├── github_workflow_setup.md # GitHub Secrets setup guide
│   └── demo_guide.md            # Onboarding & demo scenarios
└── .github/
    └── workflows/
        └── provision.yml        # GitHub Actions: parallel provisioning workflow
```

---

## 🔄 GitHub Actions CI/CD Workflow

Workflow triggers via `workflow_dispatch`. Supports parallel provisioning:

1. **Build Matrix** — Generates N parallel instances (1–10)
2. **Each Instance**:
   - Sets up Python 3.11 on `ubuntu-latest`
   - Authenticates to GCP with `GCP_SA_KEY`
   - Installs dependencies via `requirements.txt`
   - Runs `python main.py --request "..." --index N --count N`
   - Uploads `generated_artifacts/` and `audit_logs/` as downloadable artifacts
3. **Merge Audit Logs** — Combines per-instance logs into a single cumulative `audit-logs` artifact

### Required GitHub Secrets

| Secret | Description |
|---|---|
| `GCP_SA_KEY` | GCP Service Account JSON key (Compute Admin, Editor, or specific roles) |
| `GOOGLE_API_KEY` | Gemini API key |
| `GCP_PROJECT_ID` | Your GCP project ID |

---

## 🧹 Housekeeping

Available as the **🧺 Housekeeping** expander in the Streamlit sidebar. Cleans `__pycache__/`, `.pyc`, `.DS_Store`, and temp files.

---

## 🆕 UI Features (Current Version)

| Feature | Description |
|---|---|
| **🤖 AI Assistant tab** | Primary entry point — type a natural language request, get a policy preview instantly |
| **Policy Preview Panel** | Shows every VM parameter pre-filled from `vm_policy.py`; locked fields (OS image, no-address, labels) are read-only |
| **Editable policy params** | Zone, machine type, disk size (slider), disk type, instance count — all constrained to allowed values |
| **"Confirm & Deploy" flow** | Single button triggers GitHub Actions with the exact (possibly overridden) parameter set |
| DevSecOps Branding | Green/blue/indigo gradient — security-first identity |
| GitHub-Only Deployment | No local execution — all changes go through GitHub Actions |
| Unique Session IDs | `uuid4()` per session — no concurrent user collision |
| Dry Run Toggle | Preview the request without triggering the workflow |
| Pre-flight Checklist | Region/naming/service validation shown before submit (legacy tab) |
| Request History Panel | Last 5 requests with status in sidebar |
| Parallel Provisioning | Set 1–10 instances; each runs as a separate matrix job |
| Legacy Cloud Tabs | ☁️ Cloud Systems / 🚀 Pipeline & DevOps / 🤖 Agentic Apps / 🔧 Other Tools remain for non-VM resources |
