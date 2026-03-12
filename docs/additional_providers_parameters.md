# Additional Supported Providers - UI Parameters & Governance Reference

This document details the exact input parameters available in the AI Infrastructure Provisioner's interface for providers **other** than Google Cloud (GCP), alongside the **global organizational policies** enforced by the Governance Agent.

## 🛡️ Global Governance Policies (Cross-Platform)
While GCP has specific region and machine type locks, the following policies apply universally across **all** providers (AWS, Azure, CI/CD, etc.):
* **Environments (`[env]`)**: `dev`, `stag`, `prod`
* **Default Naming Convention**: Unless specified otherwise, resources must match the pattern **`proj-[env]-[service]-[resource_type]`**
* **Container Images**: All Dockerfile or Kubernetes container images must be from the approved list (`alpine`, `debian-slim`, `node:18-alpine`, `python:3.11-slim`, `gcr.io/google-samples/hello-app:1.0`)
* **Kubernetes Standards**: All K8s manifests (EKS, AKS, or generic) must include `resources.limits`, `resources.requests`, and a `livenessProbe`.

## 🏗️ 1. CI/CD Pipelines
When selecting **Create CI/CD Pipeline**, the UI presents several options, but **the Governance Agent enforces strict platform limits**.

* **Allowed CI/CD Platforms**: **`github_actions`**, **`gitlab_ci`**
* *Note: Selecting Jenkins, CircleCI, Travis CI, Azure Pipelines, AWS CodePipeline, Google Cloud Build, or Bitbucket Pipelines will result in an automatic rejection by the Governance Agent.*

**Universal Parameters:**
* **Pipeline Name**: A descriptive name for your CI/CD configuration.
* **Stages**: A comma-separated list of execution phases (e.g., `build, test, deploy, notify`).

---

## ☁️ 2. AWS Configuration
The system supports generating AWS CloudFormation templates based on these categories:

### Hosting (EC2)
* **Stack Name**: CloudFormation stack identifier (e.g., `my-stack`)
* **EC2 Instance Type**: Compute size (e.g., `t2.micro`)
* **Region**: Target AWS Region (e.g., `us-east-1`)

### Networking (VPC)
* **Stack Name**: CloudFormation stack identifier
* **VPC ID**: The ID of the parent VPC (e.g., `vpc-123456`)
* **Subnet ID**: The target Subnet (e.g., `subnet-123456`)
* **Security Group ID**: Assigned AWS Security Group (e.g., `sg-123456`)

### Database
* **Stack Name**: CloudFormation stack identifier
* **Database Type**: Choice of engine (`RDS`, `DynamoDB`, `Aurora`, `Redshift`, `DocumentDB`)
* *Dynamic Fields depending on DB Type*:
    * **RDS**: `DB Instance Identifier`, `DB Instance Class`, `DB Engine` (`MySQL`, `PostgreSQL`, etc.)
    * **DynamoDB**: `Table Name`, `Read/Write Capacity`
    * **Aurora / Redshift / DocumentDB**: `Cluster Identifier`, `DB Instance/Node Class`

### Storage (S3)
* **Stack Name**: CloudFormation stack identifier
* **Bucket Name**: Globally unique AWS S3 Bucket Name
* **Storage Class**: AWS Storage tier (`STANDARD`, `INTELLIGENT_TIERING`, `GLACIER`, etc.)

*Other Supported AWS Categories: IAM, DevOps (CodePipeline), AI & Machine Learning (SageMaker), Monitoring (CloudWatch), Security (KMS).*

---

## 🟦 3. Azure Configuration
The system supports generating ARM templates / Azure configurations across these services:

### Hosting (App Service)
* **Resource Group**: Azure logical group (e.g., `my-resource-group`)
* **App Service Name**: Globally unique application name
* **Region**: Target Azure Region (e.g., `East US`)
* **Pricing Tier (SKU)**: Azure tier (`F1`, `B1`, `P1v2`, etc.)
* **Operating System**: Underlying OS (`Windows`, `Linux`)
* **Runtime Stack**: Native runtime (`.NET`, `Node`, `Python`, `Java`, `PHP`, `Ruby`)

### Networking (VNet)
* **Resource Group**: Azure logical group
* **VNet Name**: Name of the virtual network (e.g., `my-vnet`)
* **Address Space / Subnet Address**: CIDR Blocks (e.g., `10.0.0.0/16`)
* **Subnet Name**: Name of the subset network
* **Network Security Group (NSG)**: Target Azure NSG identifier

### Database
* **Resource Group**: Azure logical group
* **Database Type**: Engine (`SQL Database`, `Cosmos DB`, `MySQL`, `PostgreSQL`, `MariaDB`)
* *Dynamic Fields depending on DB Type*:
    * **SQL DB / MySQL / Postgres / MariaDB**: `Server Name`, `Version`, `Database Name`
    * **Cosmos DB**: `Account Name`, `Consistency Level` (`Strong`, `Eventual`, etc.)

### Storage
* **Resource Group**: Azure logical group
* **Storage Account Name**: Unique Azure Storage Name
* **SKU**: Redundancy tier (`Standard_LRS`, `Standard_GRS`, `Premium_LRS`, etc.)
* **Access Tier**: Temperature tier (`Hot`, `Cool`)

*Other Supported Azure Categories: IAM, DevOps, AI & Machine Learning, Monitoring, Security.*

---

## 🔥 4. Firebase Configuration
* **Project Name**: The associated GCP/Firebase project identifier.
* **Features to Enable**: Comma-separated list of Firebase services (e.g., `Authentication, Firestore, Hosting, Functions, Storage`).

## ⚡ 5. Supabase Configuration
* **Service**: Categorized by feature (`Hosting`, `Authentication`, `Storage`, `Database`)
* **Project Name**: Associated Supabase project identifier.
* **Region / App Name / Storage Bucket**: Conditional fields based on the chosen Service type.

## ☁️ 6. Cloudflare Configuration
* **Service**: Categorized by feature (`DNS`, `Workers`, `Security`)
* **Domain Name**: Associated Cloudflare Zone.
* **Additional Inputs**: Script Name (Workers), WAF configurations (Security), or DNS record configurations.
