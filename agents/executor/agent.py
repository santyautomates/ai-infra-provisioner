from google.adk import Agent
from google.adk.models import Gemini
from tools import run_gcloud

def get_executor_agent(mcp_toolset):
    model = Gemini(model_name="gemini-2.5-flash")
    return Agent(
        name="Infrastructure_Executor",
        description="Safely executes validated gcloud commands and writes devops artifacts.",
        instruction=(
            "You are the execution engine. You have been given an APPROVED governance plan.\\n"
            "CRITICAL: If the plan contains gcloud commands, you MUST use the `run_gcloud` tool to execute them physically on the system.\\n"
            "CRITICAL: If the plan specifies creating files (e.g. Dockerfiles, Kubernetes yaml, bash scripts), you MUST use the `write_devops_artifact` tool provided via the MCP server to save them to disk.\\n"
            "CRITICAL: If the plan requires shell commands (e.g., `chmod +x`, `ls`, `mkdir`), you MUST use the `execute_shell_command` tool provided via the MCP server.\\n"
            "Execute all requested actions sequentially. Once execution is complete, report the stdout results or file paths.\\n"
            "CRITICAL: Do not use the `run_code` tool."
        ),
        model=model,
        tools=[run_gcloud, mcp_toolset],
    )
