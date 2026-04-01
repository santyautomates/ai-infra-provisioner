# AI Infrastructure Provisioner: Demo Guide

This guide walks you through demonstrating the DevSecOps AI Infra Provisioner to your team.

---

## 1. Preparing the Environment

1. **Clone the repo** and navigate into the project:
   ```bash
   cd ai-infra-provisioner
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure your `.env` file** (copy from `.env.example` if present):
   ```
   GOOGLE_API_KEY=<your Gemini API key>
   GOOGLE_CLOUD_PROJECT=<your GCP project ID>
   GITHUB_PAT=<your GitHub Personal Access Token>
   ```

---

## 2. Customizing for Your Demo Project

To adapt the organizational policies for your team, open `mcp_server.py` and modify the `POLICIES` dict (around line 20):

### Customizing Allowed Regions
```python
"allowed_regions": ["us-east1", "us-central1"],
```

### Customizing Naming Conventions
Change the `proj-` prefix to match your organization:
```python
"naming_conventions": {
    "vm":  "acme-[env]-[service]-vm",
    "vpc": "acme-[env]-[service]-vpc",
    # ...
}
```

> Any naming changes will also automatically appear in the AI Assistant's Policy Preview Panel because `ui_policy_defaults.py` reads from `vm_policy.py` directly.

---

## 3. Running the Demo

Start the Streamlit app:
```bash
source .venv/bin/activate
streamlit run app.py
```

Open `http://localhost:8501` in your browser (or use Cloud Shell Web Preview).

---

## 4. Demo Scenarios

### 🤖 Scenario A: AI Assistant — Happy Path (VM Provisioning)

Demonstrates the new **conversational agentic provisioning** flow.

1. Click the **🤖 AI Assistant** tab (first tab, selected by default).
2. Type any natural language VM request:
   > "I want a VM for the payments service in dev"
3. Click **🔍 Analyse Request**.
4. The **Policy Preview Panel** appears instantly:
   - **Editable fields** pre-filled: instance name (`proj-dev-payments-vm`), zone (`us-east1-d`), machine type (`e2-micro`), disk size (50 GB)
   - **Locked fields** shown read-only: OS image (`debian-12`), no public IP, OS Login enabled, labels
5. Optionally change the Zone or Disk Size.
6. Click **✅ Confirm & Deploy via GitHub Actions**.

*The system dispatches a fully-formed, policy-compliant provisioning request to GitHub Actions — no manual form-filling required.*

---

### 🛡️ Scenario B: Policy Rejection (Governance Guardrail)

Shows how the Governance Agent blocks non-compliant requests via the legacy **☁️ Cloud Systems** tab.

1. Select **☁️ Cloud Systems → GCP Configuration → Compute Engine**.
2. Change the zone to `us-west1-a` and the machine type to `e2-highmem-16`.
3. Click **🚀 Deploy via GitHub Actions**.
4. *(The Governance Agent will REJECT the plan — `us-west1-a` is not in `allowed_regions` and `e2-highmem-16` is not an allowed machine type.)*

---

### 🗑️ Scenario C: Safe Deletion

Shows how the agent discovers existing resources before deleting.

1. In the AI Assistant tab, type:
   > "Delete the payments VM in dev"
2. The Planner will call `list_gcp_resources(instances)` first to confirm the resource exists, then govern its deletion.

---

### 📋 Scenario D: DevOps Artifact — Dockerfile

1. Click **🚀 Pipeline & DevOps → Create Dockerfile**.
2. Set Base Image to `python:3.11-slim`.
3. Deploy via GitHub Actions.
4. *(The Governance Agent automatically validates the base image against `devops_standards.docker_images`. The artifact is saved to `generated_artifacts/`.)*

---

## 5. Governance Policy Quick Reference

| Check | Enforced By | How to pass |
|---|---|---|
| Region | Governance Agent | Use `us-east1` or `us-central1` |
| VM naming | Governance Agent | `proj-[env]-[service]-vm` |
| Machine type (dev) | Governance Agent + AI Assistant preview | `e2-micro`, `e2-small`, `e2-medium` |
| OS image | AI Assistant (locked) + Governance | `debian-12 / debian-cloud` |
| No public IP | AI Assistant (locked) + Governance | `--no-address` (always added) |
| Labels | AI Assistant (locked) + Governance | `env`, `service`, `managed-by=autoinfra` |
