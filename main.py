import asyncio
import os
import sys
import argparse
from dotenv import load_dotenv

from google.adk import Agent, Runner
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from mcp import StdioServerParameters

from tools import run_gcloud, GcloudCommandArgs

# Load environment variables from .env file
load_dotenv()

async def run_provisioning_flow(user_request: str):
    
    # Use native ADK McpToolset wrapping instead of older mcp class
    server_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"],
        )
    )
    
    # Use native ADK McpToolset wrapping
    mcp_toolset = McpToolset(connection_params=server_params)

    print("\\n[+] Initializing ADK MCP Toolset...")

    if "GOOGLE_API_KEY" not in os.environ:
        print("ERROR: GOOGLE_API_KEY environment variable is not set. Please set it before running.")
        sys.exit(1)

    model = Gemini(model_name="gemini-2.5-flash")

    from agents.planner.agent import get_planner_agent
    from agents.governance.agent import get_governance_agent
    from agents.executor.agent import get_executor_agent

    planner = get_planner_agent(mcp_toolset)
    governance = get_governance_agent(mcp_toolset)
    executor = get_executor_agent(mcp_toolset)
    
    session_service = InMemorySessionService()

    # Step 1
    print("\\n[+] Step 1: Planning Infrastructure...")
    runner1 = Runner(
        app_name="infra_provisioner",
        agent=planner,
        session_service=session_service,
        auto_create_session=True,
    )
    # The default behavior of gemini-2.5-flash sometimes forces a run_code call
    # instead of text generation when asked for commandline instructions.
    runner1._config = types.GenerateContentConfig(
        tools=[mcp_toolset],
        temperature=0.0
    )
    
    plan_text = ""
    async for event in runner1.run_async(
        user_id="user1", 
        session_id="session1", 
        new_message=types.Content(parts=[types.Part.from_text(text=f"User Request: {user_request}")])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    plan_text += part.text
            
    print(f"\\n=== PLAN ===\\n{plan_text}\\n===========\\n")

    if not plan_text.strip():
        print("[-] Error: The Infrastructure Planner did not return a valid plan. This may happen if the resource was not found or the request was ambiguous.")
        return

    # Step 2
    print("[+] Step 2: Governance Validation...")
    runner2 = Runner(
        app_name="infra_provisioner",
        agent=governance,
        session_service=session_service,
        auto_create_session=True,
    )
    
    validation_text = ""
    async for event in runner2.run_async(
        user_id="user1", 
        session_id="session2", 
        new_message=types.Content(parts=[types.Part.from_text(text=f"Please review this proposed plan:\\n{plan_text}")])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    validation_text += part.text
            
    print(f"\\n=== VALIDATION ===\\n{validation_text}\\n==================\\n")

    if "REJECTED" in validation_text:
        print("[-] Governance rejected the plan. Aborting execution.")
        return

    if "APPROVED" not in validation_text:
        print("[-] Governance response was ambiguous. Aborting execution for safety.")
        return

    # Step 3
    print("[+] Step 3: Command Execution...")
    runner3 = Runner(
        app_name="infra_provisioner",
        agent=executor,
        session_service=session_service,
        auto_create_session=True,
    )
    
    exec_text = ""
    async for event in runner3.run_async(
        user_id="user1", 
        session_id="session3", 
        new_message=types.Content(parts=[types.Part.from_text(text=f"Execute the following APPROVED plan:\\n{validation_text}")])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    exec_text += part.text
            
    print(f"\\n=== EXECUTION RESULT ===\\n{exec_text}\\n========================\\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Driven Infra Provisioner")
    parser.add_argument("--request", type=str, required=False, help="Natural language infrastructure request")
    args = parser.parse_args()
    
    if args.request:
        req = args.request
    else:
        req = "Create a VM in us-central1 for order service in dev"

    asyncio.run(run_provisioning_flow(req))
