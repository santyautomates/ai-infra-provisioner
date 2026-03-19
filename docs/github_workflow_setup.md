# DevSecOps AI Infra Provisioner — GitHub Workflow Setup Guide

> All infrastructure provisioning is executed exclusively through GitHub Actions. There is no local execution path — this ensures every change is version-controlled, auditable, and compliant.

---

## 1. Configure GitHub Secrets

Go to your repository settings: **Settings > Secrets and variables > Actions** and add:

| Secret | Description |
|---|---|
| `GCP_SA_KEY` | GCP Service Account JSON key (Compute Admin + IAM roles) |
| `GOOGLE_API_KEY` | Gemini API key from [Google AI Studio](https://aistudio.google.com/) |
| `GCP_PROJECT_ID` | Your GCP Project ID (e.g. `my-project-123`) |

---

## 2. Configure the Streamlit UI

In the **🐙 GitHub Integration** sidebar expander:

| Field | Value |
|---|---|
| Personal Access Token (PAT) | GitHub PAT with `workflow` + `actions:read` scopes |
| Repository | `owner/repo` (e.g. `santyautomates/ai-infra-provisioner`) |
| Workflow Filename | `provision.yml` |

> 💡 Set `GITHUB_PAT` in your `.env` to auto-fill the PAT field.

---

## 3. Trigger a Deployment

1. Select your **Cloud Provider**, **Service**, and configure all options in the UI.
2. Review the **⚈ Pre-flight Checklist** to confirm settings.
3. Click **🚀 Deploy via GitHub Actions**.
4. The workflow is dispatched immediately — navigate to your repo's **Actions** tab to monitor progress.

---

## 4. Monitor & Download Artifacts

After the workflow completes:

- **Actions tab** → Select the run → Click **Summary**
- Download artifacts:
  - `infrastructure-artifacts-N` — JSON report + human-readable `.txt` report per instance
  - `audit-logs` — Cumulative daily audit trail across all runs

---

## 5. Parallel Provisioning

Set **Number of Instances** (1–10) in the UI before deploying. The workflow creates N parallel matrix jobs, each provisioning an independent resource with a unique `-N` suffix (e.g. `proj-dev-payments-vm-1`, `proj-dev-payments-vm-2`).
