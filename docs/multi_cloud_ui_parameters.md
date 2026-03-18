# Multi-Cloud & DevOps UI Parameters Reference

> This document covers all **non-GCP** configuration options in the AutoInfra UI. For GCP-specific parameters and naming conventions, see [`gcp_ui_parameters.md`](./gcp_ui_parameters.md).

---

## ☁️ Tab 1: Cloud Systems

### 🔶 AWS Configuration

All AWS inputs generate **AWS CLI** or **CloudFormation** commands. No GCP naming or region rules apply.

#### Hosting (EC2 / Elastic Beanstalk)

| Field | Example Value | Notes |
|---|---|---|
| Stack Name | `my-web-stack` | CloudFormation stack name |
| EC2 Instance Type | `t2.micro`, `t3.small` | Follow AWS free-tier or sizing guidelines |
| Region | `us-east-1`, `eu-west-1` | Any valid AWS region |

```bash
# Example generated command
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t2.micro \
  --region us-east-1
```

---

#### Networking (VPC / Subnet / Security Groups)

| Field | Example Value | Notes |
|---|---|---|
| Stack Name | `my-network-stack` | CloudFormation identifier |
| VPC ID | `vpc-0a1b2c3d4e5f` | Existing VPC or auto-created |
| Subnet ID | `subnet-0a1b2c3d` | Public or private subnet |
| Security Group ID | `sg-0a1b2c3d4e` | Inbound/outbound rules reference |

```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region us-east-1
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
```

---

#### IAM (Roles & Policies)

| Field | Example Value | Notes |
|---|---|---|
| Stack Name | `my-iam-stack` | CloudFormation identifier |
| Role Name | `my-app-role` | Descriptive, no spaces |
| Policy ARN | `arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess` | AWS managed or custom |

```bash
aws iam create-role --role-name my-app-role \
  --assume-role-policy-document file://trust-policy.json
aws iam attach-role-policy --role-name my-app-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

---

#### Database (RDS / DynamoDB / Aurora / Redshift / DocumentDB)

| Sub-Type | Key Fields | Example |
|---|---|---|
| RDS | DB Identifier, Class, Engine | `db.t2.micro`, `PostgreSQL 15` |
| DynamoDB | Table Name, Read/Write Capacity | `orders-table`, RCU: 5, WCU: 5 |
| Aurora | Cluster ID, Class, Mode | `db.r5.large`, `serverless` |
| Redshift | Cluster ID, Node Type, Count | `dc2.large`, 2 nodes |
| DocumentDB | Cluster ID, Instance Class | `db.r5.large` |

---

#### Storage (S3)

| Field | Example Value | Notes |
|---|---|---|
| Bucket Name | `my-app-assets` | Must be globally unique |
| Storage Class | `STANDARD`, `INTELLIGENT_TIERING`, `GLACIER` | Cost vs access tradeoff |

```bash
aws s3 mb s3://my-app-assets --region us-east-1
aws s3api put-bucket-versioning --bucket my-app-assets \
  --versioning-configuration Status=Enabled
```

---

#### DevOps (CodePipeline)

| Field | Example Value |
|---|---|
| Pipeline Name | `my-deploy-pipeline` |
| Repository Name | `my-app-repo` |
| Stack Name | `my-codepipeline-stack` |

---

#### AI & Machine Learning (SageMaker)

| Field | Example Value | Notes |
|---|---|---|
| Notebook Instance Name | `my-ml-notebook` | SageMaker notebook |
| Instance Type | `ml.t2.medium`, `ml.m5.large` | ML-specific types |

---

#### Monitoring (CloudWatch)

| Field | Example Value |
|---|---|
| CloudWatch Alarm Name | `high-cpu-alarm` |
| Metric Name | `CPUUtilization`, `NetworkIn` |
| Threshold | `80` (percent) |

---

#### Security (KMS / WAF)

| Field | Example Value |
|---|---|
| KMS Key ID | `arn:aws:kms:us-east-1:123:key/abc-123` |
| Security Policy Name | `my-waf-policy` |

---

### 🔵 Azure Configuration

All Azure inputs generate **Azure CLI** or **ARM Template** commands.

#### App Service (Web Apps & Functions)

| Field | Example Value | Notes |
|---|---|---|
| App Name | `my-web-app` | Globally unique |
| Resource Group | `my-resource-group` | Azure container for resources |
| App Service Plan | `my-plan` | Tier: Free, Basic, Standard |
| Runtime | `PYTHON:3.11`, `NODE:18-lts` | App runtime stack |
| Region | `eastus`, `westeurope` | Any Azure region |

```bash
az webapp create \
  --resource-group my-resource-group \
  --plan my-plan \
  --name my-web-app \
  --runtime "PYTHON:3.11"
```

---

#### Networking (VNet / NSG / Load Balancer)

| Field | Example Value |
|---|---|
| Virtual Network Name | `my-vnet` |
| Subnet Name | `my-subnet` |
| NSG Name | `my-nsg` |
| Address Prefix | `10.0.0.0/16` |

---

#### IAM (RBAC / Service Principals)

| Field | Example Value |
|---|---|
| Principal Name | `my-service-principal` |
| Role | `Contributor`, `Reader`, `Owner` |
| Scope | `/subscriptions/{id}/resourceGroups/{rg}` |

---

#### Database (Azure SQL / Cosmos DB / PostgreSQL)

| Sub-Type | Key Fields |
|---|---|
| Azure SQL | Server Name, DB Name, Admin Login/Password, Tier |
| Cosmos DB | Account Name, API Type (SQL/MongoDB/Cassandra) |
| PostgreSQL | Server Name, SKU (`B1ms`, `GP_Gen5_2`), Version |

---

#### Storage (Blob / Data Lake)

| Field | Example Value |
|---|---|
| Storage Account | `mystorageaccount` (lowercase, no spaces) |
| Container Name | `my-container` |
| SKU | `Standard_LRS`, `Standard_GRS` |
| Access Tier | `Hot`, `Cool`, `Archive` |

---

#### DevOps (Azure Pipelines / AKS / Container Registry)

| Field | Example Value |
|---|---|
| Pipeline Name | `my-devops-pipeline` |
| AKS Cluster Name | `my-aks-cluster` |
| Node Count | `3` |
| VM Size | `Standard_D2_v2` |
| ACR Name | `mycontainerregistry` |

---

#### AI & Machine Learning (Azure ML / Cognitive Services)

| Field | Example Value |
|---|---|
| ML Workspace | `my-ml-workspace` |
| Compute Cluster | `my-compute-cluster` |
| Cognitive Service | `TextAnalytics`, `ComputerVision` |

---

#### Monitoring (Azure Monitor / Log Analytics)

| Field | Example Value |
|---|---|
| Log Analytics Workspace | `my-log-workspace` |
| Alert Rule Name | `high-cpu-alert` |
| Metric | `Percentage CPU` |
| Threshold | `80` |

---

#### Security (Key Vault / Policy)

| Field | Example Value |
|---|---|
| Key Vault Name | `my-keyvault` |
| Secret Name | `db-password` |
| Policy Assignment | `Require HTTPS on storage accounts` |

---

### 🔥 Firebase Configuration

Generates **Firebase CLI** commands and config.

| Feature | What It Configures |
|---|---|
| Authentication | Email/Password, Google, GitHub, Phone providers |
| Firestore | Database rules, indexes, collection setup |
| Cloud Functions | Node.js/Python function scaffolding and deploy |
| Hosting | `firebase.json`, `hosting` config, custom domain |
| Storage | Security rules for Firebase Storage |
| Realtime Database | Rules JSON, REST API endpoints |
| Analytics | Google Analytics integration |
| Remote Config | Parameter groups, conditions |
| Cloud Messaging | FCM config, notification topics |
| A/B Testing | Experiment setup with Remote Config |

**Key Inputs:**

| Field | Example Value |
|---|---|
| Project Name | `my-firebase-project` |
| Features to Enable | `Authentication, Firestore, Hosting` |

```bash
firebase init --project my-firebase-project
firebase deploy --only hosting,firestore
```

---

### 🟢 Supabase Configuration

Generates Supabase project configuration.

| Service | Key Inputs |
|---|---|
| Hosting | Project Name, Region |
| Authentication | Auth providers (Email, Google, GitHub, Discord) |
| Storage | Bucket name, policies |
| Database | PostgreSQL schema, RLS policies |

```bash
supabase init
supabase functions new my-function
supabase db push
```

---

### 🟠 Cloudflare Configuration

Generates Cloudflare Workers and DNS config.

| Service | Key Inputs |
|---|---|
| DNS | Zone ID, Record Type (`A`, `CNAME`, `TXT`), Name, Value, TTL |
| Workers | Worker Name, Script content |
| Security / WAF | Rule Name, Action (`block`, `challenge`), Expression |

```bash
wrangler pages deploy ./dist --project-name=my-site
wrangler deploy --name my-worker
```

---

## 🚀 Tab 2: Pipeline & DevOps

### Create CI/CD Pipeline

All 9 platforms are approved by the Governance agent.

| Platform | Output File | Key Inputs |
|---|---|---|
| **GitHub Actions** | `.github/workflows/[name].yml` | Pipeline name, stages |
| **GitLab CI** | `.gitlab-ci.yml` | Stages |
| **Jenkins** | `Jenkinsfile` | Stages |
| **CircleCI** | `.circleci/config.yml` | Orb, stages |
| **Azure Pipelines** | `azure-pipelines.yml` | Pool, stages |
| **AWS CodePipeline** | CloudFormation JSON | Pipeline name, stages |
| **Google Cloud Build** | `cloudbuild.yaml` | Steps |
| **Bitbucket Pipelines** | `bitbucket-pipelines.yml` | Steps |
| **Travis CI** | `.travis.yml` | Language, stages |

**Common Inputs:**

| Field | Example Value |
|---|---|
| Pipeline Name | `python-ci` |
| Stages | `build, test, deploy` |

```yaml
# Example GitHub Actions (generated)
name: python-ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
```

---

### Create Kubernetes Configuration

| Field | Example Value | Notes |
|---|---|---|
| Deployment Name | `proj-stag-backend-deployment` | Descriptive |
| Container Image | `gcr.io/my-project/my-app:latest` | From approved registry |
| Cluster Name | `proj-stag-backend-cluster` | GKE cluster |
| Namespaces | `default, production` | Comma-separated |

> **Required fields** (Governance-validated): `resources.limits`, `resources.requests`, `livenessProbe`

---

### Create Dockerfile

| Field | Example Value | Notes |
|---|---|---|
| Base Image | `python:3.11-slim` | Must be from approved list |
| Packages | `flask, sqlalchemy` | Pip packages |

**Approved base images:** `alpine`, `alpine:3.18`, `debian-slim`, `debian:12-slim`, `node:18-alpine`, `node:20-alpine`, `python:3.11-slim`, `python:3.10-slim`, `python:3.12-slim`, `nginx:alpine`, `openjdk:17-slim`, `gcr.io/google-samples/hello-app:1.0`

---

### Create Bash Script

| Field | Example Value |
|---|---|
| Script Purpose | `Deployment script for the payments service` |
| Commands | `echo "Deploying...", kubectl apply -f deploy.yaml` |

Output is saved to `generated_artifacts/` and made executable (`chmod +x`).

---

## 🤖 Tab 3: Agentic Apps

Pre-approved by Governance. The Planner generates a full architecture design + scaffold files.

| Approach | What is Generated |
|---|---|
| **Microservices** | Service breakdown, docker-compose.yml, API gateway config |
| **Serverless** | Function definitions, event triggers, IAM roles |
| **Monolithic** | MVC scaffold, Dockerfile, CI/CD pipeline |
| **Event-Driven** | Pub/Sub topology, broker config, consumer/producer patterns |
| **API-First** | OpenAPI spec, FastAPI/Express scaffold, postman collection |
| **DevOps & CD** | CI/CD pipeline + environment config + deployment strategy |
| **Agile** | Sprint board structure, JIRA/Confluence setup guide |
| **TDD** | Project scaffold + test fixtures + CI pipeline |
| **BDD** | Gherkin feature files + Cucumber/pytest-bdd scaffold |
| **DDD** | Bounded context model + aggregate + repository pattern |

---

## 🔧 Tab 4: Other Tools

### Developer Configuration (VSCode / Toolchains)

| Language | Generated Files |
|---|---|
| **Python** | `settings.json`, `.devcontainer/devcontainer.json`, `extensions.json` |
| **Node.js** | `settings.json`, `.nvmrc`, ESLint + Prettier config |
| **Go** | `settings.json`, gopls config |
| **Java** | `settings.json`, Maven/Gradle settings |
| **Rust** | `settings.json`, `rust-analyzer` config |
| **C#** | `settings.json`, OmniSharp settings |
| **Ruby** | `settings.json`, RuboCop config |
| **PHP** | `settings.json`, PHP IntelliSense config |
| **C++** | `settings.json`, clangd / IntelliSense config |

**Common Inputs:**

| Field | Example Value |
|---|---|
| Configuration Name | `Python Dev Environment` |
| VS Code Extensions | `ms-python.python, ms-python.vscode-pylance` |
| VS Code Settings | `{"python.linting.enabled": true}` |

---

## 📦 Generated Artifacts

All generated files are saved to `./generated_artifacts/` and uploaded as a GitHub Actions artifact named `infrastructure-artifacts`.

| Artifact Type | Typical Filename |
|---|---|
| CI/CD Pipeline | `github_actions_pipeline.yml` |
| Dockerfile | `Dockerfile` |
| K8s Manifest | `deployment.yaml` |
| Bash Script | `deploy_script.sh` |
| CloudFormation | `cf_template.json` |
| Azure ARM | `arm_template.json` |
