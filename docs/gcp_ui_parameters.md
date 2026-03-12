# GCP Service UI Parameters & Governance Reference

This document details the exact input parameters available in the AI Infrastructure Provisioner's **GCP Configuration** panel, alongside the **strict organizational policies** enforced by the Governance Agent. Providing values outside these policies will result in immediate rejection.

## 🛡️ Global Governance Policies
* **Allowed Regions**: `us-central1`, `europe-west1`, `asia-northeast1`
* **Environments (`[env]`)**: `dev`, `stag`, `prod`
* **Default Naming Convention**: `proj-[env]-[service]-[resource_type]`

---

## Compute Engine
* **Project ID**: The destination GCP project
* **Instance Name**: Name of the VM. Must match pattern **`proj-[env]-[service]-vm`** (e.g., `proj-dev-payment-vm`)
* **Zone**: Deployment zone (must be within an allowed region, e.g., `us-central1-a`)
* **Instance Size (T-Shirt)**: Size of the VM instance. 
    * *Options*: `Small (e2-micro)`, `Medium (e2-small)`, `Large (e2-medium)`, `X-Large (n1-standard-1)`
    * *Backend Mapping*: The UI will automatically translate your selection into the GCP raw string (e.g., `e2-medium`) for the executor.
* **Source Image**: OS Image family. Default mandated by security: **`debian-11`** (from `debian-cloud`)
* *Note: Public IP addresses are strictly disabled for VMs.*

## Cloud Run
* **Project ID**: The destination GCP project
* **Service Name**: Name of the serverless deployment. Must match pattern **`proj-[env]-[service]-cloudrun`**
* **Region**: Deployment region (must be an allowed region)
* **Memory Size (T-Shirt)**: Allocated memory instance size.
    * *Options*: `Small (256Mi)`, `Medium (512Mi)`, `Large (1Gi)`, `X-Large (2Gi)`
* **Container Image URL**: The specific image to deploy. Must use an approved base image: **`alpine`, `debian-slim`, `node:18-alpine`, `python:3.11-slim`, `gcr.io/google-samples/hello-app:1.0`**
* **Container Port**: Exposed port
* **Authentication**: Choice between `Allow unauthenticated invocations` or `Require authentication`. *Note: Unauthenticated invocations are currently permitted for Cloud Run.*

## Kubernetes Engine (GKE)
* **Project ID**: The destination GCP project
* **Cluster Name**: The name of the cluster. Must match pattern **`proj-[env]-[service]-cluster`**
* **Zone/Region**: Deployment zone/region (must be an allowed region)
* **Number of Nodes**: Initial node count (integer)
* **Node Size (T-Shirt)**: Worker node instance size.
    * *Options*: `Small (e2-micro)`, `Medium (e2-small)`, `Large (e2-medium)`, `X-Large (n1-standard-1)`
    * *Backend Mapping*: Translated into the corresponding raw GCP string (e.g., `e2-medium`).
* *DevOps Policy: All deployed Kubernetes workloads are audited to ensure they contain `resources.limits`, `resources.requests`, and a `livenessProbe`.*

## Cloud Functions
* **Project ID**: The destination GCP project
* **Function Name**: Name of the function. Follows default fallback pattern.
* **Region**: Deployment region (must be an allowed region)
* **Runtime**: Execution environment (`nodejs20`, `python311`, `go121`, `java17`)
* **Memory Size (T-Shirt)**: Allocated memory size for the function.
    * *Options*: `Small (128MB)`, `Medium (256MB)`, `Large (512MB)`, `X-Large (1024MB)`
* **Trigger**: Invocation method (`HTTP`, `Pub/Sub`, `Cloud Storage`)

## VPC Network
* **Project ID**: The destination GCP project
* **VPC Name**: Name of the new network. Must match pattern **`proj-[env]-[service]-vpc`**
* **Subnet Mode**: Creation mode (`Custom`, `Auto`)

## Cloud Storage
* **Project ID**: The destination GCP project
* **Bucket Name**: Globally unique bucket name. Must match pattern **`proj-[env]-[service]-storage`**
* **Location**: Region/Multi-region (must be an allowed region)
* **Storage Class**: Data class (`STANDARD`, `NEARLINE`, `COLDLINE`, `ARCHIVE`)
* **Public Access**: Choice of `Not Public` or `Public`

## Cloud SQL
* **Project ID**: The destination GCP project
* **Instance ID**: Name of the database instance. Must match pattern **`proj-[env]-[service]-db`**
* **Database Version**: Engine version (`POSTGRES_15`, `POSTGRES_14`, `MYSQL_8_0`, `SQLSERVER_2019_STANDARD`)
* **Database Size (T-Shirt)**: Compute size for the database engine.
    * *Options*: `Small (db-f1-micro)`, `Medium (db-g1-small)`, `Large (db-custom-1-3840)`
* **Region**: Deployment region (must be an allowed region)

## Pub/Sub
* **Project ID**: The destination GCP project
* **Topic Name**: Name of the message topic. Must match pattern **`proj-[env]-[service]-topic`**
* **Subscription Name**: Associated default subscription name

## IAM
* **Project ID**: The destination GCP project
* **Principal**: The user or service account (e.g., `user:admin@example.com`)
* **Role**: The IAM role to grant (e.g., `roles/viewer`)

## Cloud Build
* **Project ID**: The destination GCP project
* **Trigger Name**: Name of the new build trigger
* **Source Repository**: connected Repo location
* *DevOps Policy: CI/CD configurations must target approved platforms: `github_actions`, `gitlab_ci`.*

---
*Other supported services with standard form fields: App Engine, Cloud Load Balancing, Spanner, Firestore, Bigtable, BigQuery, Artifact Registry, Secret Manager, Vertex AI, Cloud Monitoring.*
