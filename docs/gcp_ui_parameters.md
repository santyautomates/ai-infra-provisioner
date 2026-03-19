# GCP UI Parameters — Policy-Aligned Reference

> All examples below are compliant with the organizational policies defined in `mcp_server.py`.
> Any value outside these constraints will be **REJECTED** by the Governance Agent.

---

## 🌍 Global Policy Constraints

| Policy | Allowed Values |
|---|---|
| **Regions** | `us-east1` (Strictly Enforced) |
| **Environments** | `dev`, `stag`, `prod` |
| **Naming Pattern** | `proj-[env]-[service]-[resource_type]` |

> ⚠️ **DEMO SCRIPT - GOVERNANCE HARD BLOCKS:** 
> We have purposefully restricted the MCP Policy to ONLY allow `us-east1` to pass Governance.
> 
> **To PASS (Green Status):** Select `us-east1`.
> **To FAIL (Red Rejection):** Select `us-central1` or ANY other region in the UI dropdown. The Governance Agent will intercept the AI plan and trigger a hard policy rejection!

---

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
| Image Family | `debian-11` only | `--image-family=debian-11` |
| Image Project | `debian-cloud` only | `--image-project=debian-cloud` |
| Public IP | **Not allowed** (`allow_public_ip: false`) | Must use `--no-address` |

**Valid gcloud command example:**
```bash
gcloud compute instances create proj-dev-payment-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --no-address
```

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
| Region | See allowed regions | `europe-west1` |
| Database Version | `POSTGRES_15`, `MYSQL_8_0`, `SQLSERVER_2019_STANDARD` | `POSTGRES_15` |
| Tier | `db-f1-micro`, `db-g1-small`, `db-custom-1-3840` | `db-g1-small` |

**Valid gcloud command example:**
```bash
gcloud sql instances create proj-prod-payment-db \
  --database-version=POSTGRES_15 \
  --tier=db-g1-small \
  --region=europe-west1
```

---

## ☸️ Google Kubernetes Engine (GKE)

**Naming**: `proj-[env]-[service]-cluster`

| Parameter | Allowed Values | Example |
|---|---|---|
| Cluster Name | Pattern above | `proj-stag-backend-cluster` |
| Region | See allowed regions | `asia-northeast1` |
| Machine Type | Same as VM: `allowed_machine_types` | `e2-small` |
| Node Count | 1–10 | `3` |

**Valid gcloud command example:**
```bash
gcloud container clusters create proj-stag-backend-cluster \
  --region=asia-northeast1 \
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

Pipelines must target only:
- `github_actions`
- `gitlab_ci`

Any other platform (Jenkins, CircleCI, etc.) will not be validated by the governance agent for automated provisioning.

---

## ❌ Common Rejection Reasons

| Mistake | Example | Fix |
|---|---|---|
| Wrong region | `us-central1` | Strict Policy Enforcement: You must use `us-east1`. |
| Execution Failed (Capacity) | `ZONE_RESOURCE_POOL_EXHAUSTED` | This happens on `e2-micro` instances during peak times. |
| Wrong machine type | `e2-highmem-16` | Use allowed sizes tightly coupled to the Environment (e.g. `dev` = `e2-micro/small/medium`) |
| Wrong SQL tier | `db-n1-standard-2` | Use `db-f1-micro`, `db-g1-small`, or `db-custom-1-3840` |
| Missing `--no-address` on VM | `gcloud compute instances create ...` | Always add `--no-address` |
| Bad naming | `payment-vm-dev` | Must be `proj-dev-payment-vm` |
| Unapproved Docker base | `FROM ubuntu:22.04` | Use `FROM debian-slim` or other approved images |
