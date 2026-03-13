# GCP Service UI Parameters & Governance Reference

This document details the exact input parameters available in the AI Infrastructure Provisioner's **GCP Configuration** panel, alongside the **strict organizational policies** enforced by the Governance Agent.

## 🛡️ Global Governance Policies
* **Allowed Regions**: `us-central1`, `europe-west1`, `asia-northeast1`
* **Environments (`[env]`)**: `dev`, `stag`, `prod`
* **Naming Convention**: `proj-[env]-[service]-[resource_type]`

---

## 🖥️ Compute & Hosting

### Compute Engine (VM)
*   **Instance Name**: Must match `proj-[env]-[service]-vm` (e.g., `proj-dev-payment-vm`)
*   **Instance Size (T-Shirt)**:
    *   `Small (e2-micro)` -> 2 vCPU, 1GB RAM
    *   `Medium (e2-small)` -> 2 vCPU, 2GB RAM
    *   `Large (e2-medium)` -> 2 vCPU, 4GB RAM
    *   `X-Large (n1-standard-1)` -> 1 vCPU, 3.75GB RAM
*   **Source Image**: `debian-11` (Default), `ubuntu-2204-lts`, `rhel-9`

### Cloud Run (Serverless Containers)
*   **Service Name**: Must match `proj-[env]-[service]-cloudrun`
*   **Memory Size (T-Shirt)**:
    *   `Small (256Mi)`, `Medium (512Mi)`, `Large (1Gi)`, `X-Large (2Gi)`
*   **Container Image**: Must be from an approved registry (e.g., `gcr.io/google-samples/hello-app:1.0`)

### Kubernetes Engine (GKE)
*   **Cluster Name**: Must match `proj-[env]-[service]-cluster`
*   **Node Size (T-Shirt)**: Matches Compute Engine sizes (e.g., `Large (e2-medium)`)
*   **Node Count**: 1 to 10 (Default: 3)

---

## 🌐 Networking

### VPC Network
*   **VPC Name**: Must match `proj-[env]-[service]-vpc`
*   **Subnet Mode**: `Custom` (Recommended) or `Auto`

### Cloud Load Balancing
*   **LB Name**: Must match `proj-[env]-[service]-lb`
*   **Type**: `External HTTP(S)`, `Internal HTTP(S)`, `Network TCP/UDP`

---

## 🗄️ Storage & Databases

### Cloud Storage (GCS)
*   **Bucket Name**: Must match `proj-[env]-[service]-storage`
*   **Storage Class**: `STANDARD`, `NEARLINE`, `COLDLINE`, `ARCHIVE`

### Cloud SQL (Relational DB)
*   **Instance ID**: Must match `proj-[env]-[service]-db`
*   **Database Version**: `POSTGRES_15`, `MYSQL_8_0`, `SQLSERVER_2019_STANDARD`
*   **Size (T-Shirt)**:
    *   `Small (db-f1-micro)`, `Medium (db-g1-small)`, `Large (db-custom-1-3840)`

### Spanner (Global Relational DB)
*   **Instance ID**: Must match `proj-[env]-[service]-spanner`
*   **Node Count**: 1 to 5 (Default: 1)

---

## 🧠 Data & AI

### BigQuery (Data Warehouse)
*   **Dataset ID**: Must match `proj_[env]_[service]_dataset` (Note: Underscores used for BQ)
*   **Location**: Matches allowed regions (e.g., `US`, `EU`, or specific regions)

### Vertex AI (Machine Learning)
*   **Endpoint Name**: Must match `proj-[env]-[service]-endpoint`
*   **Model Type**: `Gemini 1.5 Pro`, `Gemini 1.5 Flash`, `PaLM 2`

---

## 🛠️ DevOps & Security

### Artifact Registry
*   **Repository Name**: Must match `proj-[env]-[service]-repo`
*   **Format**: `DOCKER`, `MAVEN`, `NPM`, `PYTHON`

### Secret Manager
*   **Secret ID**: Must match `proj-[env]-[service]-secret`
*   **Replication**: `Automatic` or `Manual (Regional)`

### IAM (Identity & Access Management)
*   **Principal**: Email address (e.g., `service-account@project.iam.gserviceaccount.com`)
*   **Role**: Predefined role (e.g., `roles/storage.admin`, `roles/compute.viewer`)
