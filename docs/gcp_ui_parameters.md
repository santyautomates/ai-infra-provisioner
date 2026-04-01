# GCP UI Parameters — Policy-Aligned Reference

> All examples below are compliant with the organizational policies defined in `mcp_server.py` and `policies/vm_policy.py`.
> Any value outside these constraints will be **REJECTED** by the Governance Agent.

---

## 🤖 AI Assistant — Agentic Provisioning (Primary UI)

The **AI Assistant tab** (first tab in the UI) provides a conversational provisioning experience for Compute Engine VMs:

1. **Describe your need** in plain English: *"I want a VM for the payments service in dev"*
2. The system **extracts intent** (environment + service name) and shows a **Policy Preview Panel**:
   - **Locked 🔒** — OS image, public IP, OS Login, labels — read-only, policy-enforced
   - **Editable ✏️** — instance name, zone, machine type, disk size, disk type, instance count — pre-filled with policy defaults
3. Modify any editable field, then click **✅ Confirm & Deploy via GitHub Actions**

The helper module `ui_policy_defaults.py` reads `VM_POLICY` directly so the preview is always in sync with the governance rules.

> For all other GCP services (Cloud Run, GKE, SQL, etc.) use the **☁️ Cloud Systems** tab.

---

## 🌍 Global Policy Constraints

| Policy | Allowed Values |
|---|---|
| **Regions (All Services)** | `us-central1`, `us-east1` |
| **Environments** | `dev`, `stag`, `prod` |
| **Naming Pattern** | `proj-[env]-[service]-[resource_type]` |

> ⚠️ **DEMO SCRIPT - GOVERNANCE HARD BLOCKS:** 
> We have purposefully restricted the MCP Policy to ONLY allow `us-east1` to pass Governance.
> 
> **To PASS (Green Status):** Select `us-east1`.
> **To FAIL (Red Rejection):** Select `us-central1` or ANY other region in the UI dropdown. The Governance Agent will intercept the AI plan and trigger a hard policy rejection!

---

## 📊 Per-Environment Zone & Region Matrix

### 🖥️ Compute Engine (VM) — from `policies/vm_policy.py`

Machine types are **strictly locked per environment**. Zones must fall within the allowed regions.

| Environment | Allowed Machine Types | Allowed Zones |
|---|---|---|
| `dev` | `e2-micro`, `e2-small`, `e2-medium` | `us-central1-a/b/c`, `us-east1-b/c/d` |
| `stag` | `e2-medium`, `n1-standard-1`, `n1-standard-2` | `us-central1-a/b/c`, `us-east1-b/c/d` |
| `prod` | `n1-standard-1`, `n1-standard-2`, `n1-standard-4`, `n2-standard-2` | `us-central1-a/b/c`, `us-east1-b/c/d` |

### ☁️ Cloud Run — from `mcp_server.py`

| Environment | Container Images | Region |
|---|---|---|
| `dev` | `python:3.11-slim`, `node:18-alpine`, `gcr.io/google-samples/hello-app:1.0` | `us-central1`, `us-east1` |
| `stag` | Same as dev | `us-central1`, `us-east1` |
| `prod` | Same as dev | `us-central1`, `us-east1` |

> Auth policy: `allow_unauthenticated_cloudrun: true` (all envs)

### 🗄️ Cloud SQL — from `mcp_server.py`

| Environment | Allowed Tiers | Region |
|---|---|---|
| `dev` | `db-f1-micro` | `us-central1`, `us-east1` |
| `stag` | `db-g1-small` | `us-central1`, `us-east1` |
| `prod` | `db-custom-1-3840` | `us-central1`, `us-east1` |

### ☸️ GKE, 🪣 GCS, 📡 Pub/Sub, 🔴 Memorystore, 🌐 VPC

All other services share the **global region policy** and do **not** have environment-specific zone restrictions:

| Service | Allowed Regions (All Envs) |
|---|---|
| GKE | `us-central1`, `us-east1` |
| Cloud Storage | `us-central1`, `us-east1` |
| Pub/Sub | Global (no region required) |
| Memorystore (Redis) | `us-central1`, `us-east1` |
| VPC / Subnets | `us-central1`, `us-east1` |
| Artifact Registry | `us-central1`, `us-east1` |
| Cloud Functions | `us-central1`, `us-east1` |
| BigQuery | `us-central1`, `us-east1` (dataset level) |
| Vertex AI | `us-central1`, `us-east1` |

## 🖥️ Compute Engine (VM)

**Naming**: `proj-[env]-[service]-vm`

| Parameter | Allowed Values | Example |
|---|---|---|
| Instance Name | Pattern above | `proj-dev-payment-vm` |
| Zone | Must be in allowed region | `us-central1-a` |
| Machine Type | **Strictly Tiered by Environment (See Below)** | `e2-medium` |

**Environment-Based Machine Type Enforcements:**
| Environment Choice | Allowed Machine Types |
|---|---|
| `dev` | `e2-micro`, `e2-small`, `e2-medium` |
| `stag` | `e2-medium`, `n1-standard-1`, `n1-standard-2` |
| `prod` | `n1-standard-1`, `n1-standard-2`, `n1-standard-4`, `n2-standard-2` |
| Image Family | `debian-12` only | `--image-family=debian-12` |
| Image Project | `debian-cloud` only | `--image-project=debian-cloud` |
| Public IP | **Not allowed** (`allow_public_ip: false`) | Must use `--no-address` |

**Valid gcloud command example (confirmed working ✅):**
```bash
gcloud compute instances create proj-dev-payment-vm-1 \
  --project=gen-lang-client-0436480880 \
  --zone=us-east1-d \
  --machine-type=e2-small \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --no-address \
  --metadata=enable-oslogin=TRUE \
  --labels=env=dev,service=payment,managed-by=autoinfra
```

> ℹ️ When using the AI Assistant tab, this exact command is constructed automatically from the Policy Preview Panel parameters.

---

## ☁️ Cloud Run

**Naming**: `proj-[env]-[service]-cloudrun`

| Parameter | Allowed Values | Example |
|---|---|---|
| Service Name | Pattern above | `proj-dev-payment-cloudrun` |
| Region | See allowed regions | `us-central1` |
| Container Image | From `devops_standards.docker_images` | `gcr.io/google-samples/hello-app:1.0` |
| Allow Unauthenticated | Based on `allow_unauthenticated_cloudrun: true` | `--allow-unauthenticated` |

**Valid gcloud command example:**
```bash
gcloud run deploy proj-dev-payment-cloudrun \
  --image=gcr.io/google-samples/hello-app:1.0 \
  --region=us-central1 \
  --allow-unauthenticated
```

---

## 🗄️ Cloud SQL

**Naming**: `proj-[env]-[service]-db`

| Parameter | Allowed Values | Example |
|---|---|---|
| Instance ID | Pattern above | `proj-prod-payment-db` |
| Region | See allowed regions | `us-east1` |
| Database Version | `POSTGRES_15`, `MYSQL_8_0`, `SQLSERVER_2019_STANDARD` | `POSTGRES_15` |
| Tier | `db-f1-micro`, `db-g1-small`, `db-custom-1-3840` | `db-g1-small` |

**Valid gcloud command example:**
```bash
gcloud sql instances create proj-prod-payment-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=us-east1
```

---

## ☸️ Google Kubernetes Engine (GKE)

**Naming**: `proj-[env]-[service]-cluster`

| Parameter | Allowed Values | Example |
|---|---|---|
| Cluster Name | Pattern above | `proj-stag-backend-cluster` |
| Region | See allowed regions | `us-central1` |
| Machine Type | Same as VM: `allowed_machine_types` | `e2-small` |
| Node Count | 1–10 | `3` |

**Valid gcloud command example:**
```bash
gcloud container clusters create proj-stag-backend-cluster \
  --region=us-central1 \
  --machine-type=e2-small \
  --num-nodes=3
```

---

## 🪣 Cloud Storage (GCS)

**Naming**: `proj-[env]-[service]-storage`

| Parameter | Allowed Values | Example |
|---|---|---|
| Bucket Name | Pattern above | `proj-dev-media-storage` |
| Location | See allowed regions | `us-central1` |
| Storage Class | `STANDARD`, `NEARLINE`, `COLDLINE`, `ARCHIVE` | `STANDARD` |

**Valid gcloud command example:**
```bash
gcloud storage buckets create gs://proj-dev-media-storage \
  --location=us-central1 \
  --default-storage-class=STANDARD
```

---

## 📡 Pub/Sub

**Naming**: `proj-[env]-[service]-topic`

| Parameter | Allowed Values | Example |
|---|---|---|
| Topic Name | Pattern above | `proj-dev-orders-topic` |

**Valid gcloud command example:**
```bash
gcloud pubsub topics create proj-dev-orders-topic
```

---

## 🔴 Memorystore (Redis)

**Naming**: `proj-[env]-[service]-cache`

| Parameter | Allowed Values | Example |
|---|---|---|
| Instance Name | Pattern above | `proj-dev-session-cache` |
| Region | See allowed regions | `us-central1` |
| Tier | `BASIC`, `STANDARD_HA` | `BASIC` |

**Valid gcloud command example:**
```bash
gcloud redis instances create proj-dev-session-cache \
  --region=us-central1 \
  --tier=BASIC
```

---

## 🌐 VPC Network

**Naming**: `proj-[env]-[service]-vpc`

| Parameter | Allowed Values | Example |
|---|---|---|
| VPC Name | Pattern above | `proj-dev-core-vpc` |
| Subnet Mode | `custom` (recommended) or `auto` | `custom` |

**Valid gcloud command example:**
```bash
gcloud compute networks create proj-dev-core-vpc \
  --subnet-mode=custom
```

---

## 🐳 Dockerfiles (DevOps Artifacts)

| Parameter | Allowed Values | Example |
|---|---|---|
| Base Image | `alpine`, `debian-slim`, `node:18-alpine`, `python:3.11-slim`, `gcr.io/google-samples/hello-app:1.0` | `python:3.11-slim` |

**Valid Dockerfile example:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

---

## ⚓ Kubernetes Manifests (GKE Only)

Kubernetes YAML must include the following required fields per `devops_standards.kubernetes_requirements`:
- `resources.limits`
- `resources.requests`
- `livenessProbe`

**Valid Kubernetes Deployment example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: proj-stag-payment-deployment
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: payment-app
        image: gcr.io/google-samples/hello-app:1.0
        resources:
          requests:
            cpu: "250m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
```

---

## ⚙️ CI/CD Pipelines

Pipelines must target one of the approved CI/CD platforms from `devops_standards.ci_cd_allowed_platforms`:

| Platform | Status |
|---|---|
| `github_actions` | ✅ Approved |
| `gitlab_ci` | ✅ Approved |
| `google_cloud_build` | ✅ Approved |
| `jenkins` | ✅ Approved |
| `circleci` | ✅ Approved |
| `azure_pipelines` | ✅ Approved |
| `aws_codepipeline` | ✅ Approved |
| `travis_ci` | ✅ Approved |
| `bitbucket_pipelines` | ✅ Approved |

---

## ❌ Common Rejection Reasons

| Mistake | Example | Fix |
|---|---|---|
| Wrong region | `us-central1` | Strict Policy Enforcement: You must use `us-east1`. |
| Execution Failed (Capacity) | `ZONE_RESOURCE_POOL_EXHAUSTED` | Use `us-east1-d` with `e2-small` — confirmed stable zone. |
| Wrong machine type | `e2-highmem-16` | Use allowed sizes tightly coupled to the Environment (e.g. `dev` = `e2-micro/small/medium`) |
| Wrong SQL tier | `db-n1-standard-2` | Use `db-f1-micro`, `db-g1-small`, or `db-custom-1-3840` |
| Missing `--no-address` on VM | `gcloud compute instances create ...` | Always add `--no-address` |
| Bad naming (with space) | `proj-dev-payment -vm` | Must be `proj-dev-payment-vm` (no spaces) |
| Unapproved Docker base | `FROM ubuntu:22.04` | Use `FROM debian-slim` or other approved images |
| Retired image | `--image-family=debian-11` | `debian-11` is retired — use `debian-12` |

---

## 🔧 Troubleshooting — Known Issues & Fixes

### Parallel Provisioning (3-Instance Matrix)

When running the GitHub Actions parallel matrix for 3 instances, the following issues have been debugged and resolved:

| Issue | Symptom | Fix Applied |
|---|---|---|
| **Gemini hallucinates `run_code` tool** | `ValueError: Tool 'run_code' not found` — crashes during Planner step | Added stub `run_code` tool in `mcp_server.py` that redirects the LLM to output as plain text |
| **anyio cancel scope crash** | `RuntimeError: Attempted to exit cancel scope in a different task` | Happens during MCP session teardown (after work completes). Suppressed via `try/except` in `main.py` |
| **Incomplete plan rejected by Governance** | `REJECTED: The plan only includes API enablement but not the VM creation command` | Added `COMPLETENESS — CRITICAL` rule to Planner agent prompt |
| **Instance 1 failing at 0s delay** | Planner tool calls fail immediately at startup | Changed stagger formula from `(idx-1)*30` to `15 + (idx-1)*30` so Instance 1 waits 15s for MCP warmup |
| **Zone capacity exhausted** | `ZONE_RESOURCE_POOL_EXHAUSTED` for `e2-medium` | Switched to `us-east1-d` with `e2-small` — stable and confirmed working |

### Recommended Parallel Run Settings (✅ Confirmed Working)

| Field | Value |
|---|---|
| **Zone** | `us-east1-d` |
| **Machine Type** | `e2-small` (dev) or `e2-micro` (demo) |
| **Image** | `debian-12` / `debian-cloud` |
| **Stagger Delay** | `15 + (instance_index - 1) * 30` seconds |
| **Naming** | `proj-[env]-[service]-vm-[N]` (suffix auto-injected by `main.py`) |
