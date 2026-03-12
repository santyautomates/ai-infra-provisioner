# AI Infrastructure Provisioner: Cloud Shell Demo Guide

This guide will walk you through setting up and demonstrating the AI Infrastructure Provisioner to your team using Google Cloud Shell.

## 1. Preparing the Environment (Cloud Shell)

1.  **Open Cloud Shell**: Navigate to the [Google Cloud Console](https://console.cloud.google.com/) and click the "**Activate Cloud Shell**" icon in the top right.
2.  **Upload/Clone Code**: Upload the `ai-infra-provisioner_backup_20260310.tar.gz` archive to Cloud Shell and extract it, or clone your repository.
    ```bash
    tar -xzf ai-infra-provisioner_backup_20260310.tar.gz
    cd ai-infra-provisioner
    ```
3.  **Run Setup**: We provided a handy script to set up your Python virtual environment and prompt you for the required API keys and new Project ID.
    ```bash
    chmod +x setup_cloudshell.sh
    ./setup_cloudshell.sh
    ```

## 2. Customizing for Your Demo Project

To make the demo relevant to your team, you can quickly customize the organizational policies encoded in the MCP Server.

Open `mcp_server.py` and modify the `POLICIES` dictionary (around line 20):

### Customizing Regions
Change the allowed regions to match your team's typical deployment zones:
```python
"allowed_regions": ["us-east1", "europe-west4"],
```

### Customizing Naming Conventions
Change the prefixes to match your new project's standards. For example, if your new project is `acme-corp`, change `proj-` to `acme-`:
```python
"naming_conventions": {
    "vm": "acme-[env]-[service]-vm",
    "vpc": "acme-[env]-[service]-vpc",
    # ...
}
```

## 3. Running the Demo

Now that the policies are customized and the environment is set up, you can start running demo prompts using the new Web UI. 

Make sure your virtual environment is activated, then start the Streamlit app:
```bash
# Ensure your environment is active:
source .venv/bin/activate

# Start the Streamlit App:
streamlit run app.py
```

This will provide a URL (usually `http://localhost:8501`) which you can open in your browser or through Cloud Shell's "Web Preview" feature.

Once the UI is open, you can demonstrate the following scenarios using the text input box:

**Demo Scenario A: The Happy Path (Successful Provisioning)**
Show how a simple natural language prompt generates and executes secure infrastructure. Enter this into the app:
> "Create a VPC network for core-networking in stag environment"
*(The system should plan it, govern it, and ultimately create `acme-stag-core-networking-vpc`)*

**Demo Scenario B: Policy Rejection (The "Guardrail")**
Show how the Governance agent blocks non-compliant requests. Enter this:
> "Deploy an e2-highmem-16 VM in asia-south1"
*(The system should REJECT the plan because `asia-south1` is not in our `allowed_regions` and `e2-highmem-16` is not an allowed machine type.)*

**Demo Scenario C: Safe Deletion**
Show how the agent discovers existing infrastructure to prevent hallucinations before deleting.
> "Delete the core networking vpc we just made"
*(The Planner will autonomously list VPCs, identify `acme-stag-core-networking-vpc`, and govern its deletion securely.)*
