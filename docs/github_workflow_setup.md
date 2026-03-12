# GitHub Workflow Setup Guide

To run the AI Infrastructure Provisioner via GitHub Actions, follow these steps:

## 1. Configure GitHub Secrets

Go to your repository settings: **Settings > Secrets and variables > Actions** and add the following secrets:

- `GCP_SA_KEY`: The JSON key of a Google Cloud Service Account with the necessary permissions (e.g., Editor or specific roles like Compute Admin).
- `GOOGLE_API_KEY`: Your Gemini API Key.

## 2. Usage

1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Provision Infrastructure** workflow.
3. Click **Run workflow**.
4. Enter your natural language request in the `request` field.
5. Click **Run workflow** to start the process.

## 3. Monitoring

You can click on the running workflow to see the real-time logs of the Planning, Governance, and Execution steps.
