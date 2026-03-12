import os
from google.adk import Agent
from google.adk.models import Gemini

def get_planner_agent(mcp_toolset):
    model = Gemini(model_name="gemini-2.5-flash")
    gcp_project = os.environ.get("GOOGLE_CLOUD_PROJECT", "[YOUR_GCP_PROJECT_ID]")
    return Agent(
        name="Infrastructure_Planner",
        description="Translates natural language to GCP infrastructure plans",
        instruction=(
            f"You are a GCP cloud architect and DevOps engineer. The user wants to provision infrastructure or generate DevOps artifacts (Dockerfiles, K8s configs, CI/CD pipelines) for the GCP project: {gcp_project}.\\n"
            "1. Call the `get_organizational_policies` tool to retrieve naming rules, allowed regions, and DevOps standards.\\n"
            "2. If the request is for DELETION or involves existing remote resources, call `list_gcp_resources` to find the exact name.\\n"
            "3. Generate a strict plan detailing the exact actions. This can include `gcloud` commands AND/OR the contents of files to generate (e.g. providing the full text for a Dockerfile).\\n"
            "   IMPORTANT: For GCP resources, you must ALWAYS include a `gcloud services enable <service-api>` command as the first step.\\n"
            "4. Ensure project IDs in gcloud commands are actual, not placeholders.\\n"
            "5. Explain how the proposed plan complies with the policies (e.g. verifying the Docker base image or K8s resource limits against devops_standards).\\n"
            "CRITICAL: You MUST provide your final plan as a text response. Do NOT use the `run_code` tool as it is not registered. Only use `list_gcp_resources` and `get_organizational_policies`."
        ),
        model=model,
        tools=[mcp_toolset]
    )
