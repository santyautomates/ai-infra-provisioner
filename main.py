import asyncio
import os
import sys
import json
import argparse
from datetime import datetime, timezone
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

AUDIT_LOG_DIR = "audit_logs"
ARTIFACT_DIR = "generated_artifacts"

def _get_dated_log_path(filename: str) -> str:
    """Returns audit_logs/YYYY-MM-DD/<filename> for today's date (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    day_dir = os.path.join(AUDIT_LOG_DIR, today)
    os.makedirs(day_dir, exist_ok=True)
    return os.path.join(day_dir, filename)

def _write_audit_summary(data: dict):
    """Append the full pipeline run record to audit_logs/YYYY-MM-DD/audit_summary.log."""
    path = _get_dated_log_path("audit_summary.log")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
    print(f"\n[+] Audit summary appended → {path}")

def _write_provision_artifact(audit: dict):
    """Write a JSON + human-readable .txt artifact into generated_artifacts/ so GitHub
    Actions always has files to upload regardless of request type."""
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    idx = audit.get("instance_index", 1)
    base = f"provision_{ts}_instance{idx}"

    # JSON artifact (machine-readable)
    json_path = os.path.join(ARTIFACT_DIR, f"{base}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    # Human-readable report
    txt_path = os.path.join(ARTIFACT_DIR, f"{base}_report.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  ShieldInfra — DevSecOps AI Infra Provisioner\n")
        f.write("=" * 60 + "\n")
        f.write(f"Timestamp : {audit.get('run_timestamp')}\n")
        f.write(f"Instance  : {idx} of {audit.get('total_count', 1)}\n")
        f.write(f"Status    : {audit.get('governance_status', 'UNKNOWN')}\n")
        f.write("\n--- REQUEST ---\n")
        f.write(str(audit.get("request", "")) + "\n")
        f.write("\n--- PLAN ---\n")
        f.write(str(audit.get("plan", "")) + "\n")
        f.write("\n--- GOVERNANCE ---\n")
        f.write(str(audit.get("governance_response", "")) + "\n")
        f.write("\n--- EXECUTION RESULT ---\n")
        f.write(str(audit.get("execution_result", "")) + "\n")

    print(f"[+] Artifact saved → {json_path}")
    print(f"[+] Report saved  → {txt_path}")

async def run_provisioning_flow(user_request: str, instance_index: int = 1, total_count: int = 1):
    run_ts = datetime.now(timezone.utc).isoformat()
    audit = {
        "run_timestamp": run_ts,
        "request": user_request,
        "instance_index": instance_index,
        "total_count": total_count,
        "plan": None,
        "governance_status": None,
        "governance_response": None,
        "execution_result": None,
    }
    
    # Use native ADK McpToolset wrapping instead of older mcp class
    server_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"],
        )
    )
    
    # Use native ADK McpToolset wrapping
    mcp_toolset = McpToolset(connection_params=server_params)

    print("\n[🛡️] Initializing ShieldInfra AI Orchestrator...")

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
    print("\n[🛡️] Step 1: Shield Planning & Architecture...")
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
            
    print(f"\n=== PLAN ===\n{plan_text}\n===========\n")
    audit["plan"] = plan_text

    if not plan_text.strip():
        print("[-] Error: The Infrastructure Planner did not return a valid plan.")
        audit["governance_status"] = "ERROR_NO_PLAN"
        _write_audit_summary(audit)
        _write_provision_artifact(audit)
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
            
    print(f"\n=== VALIDATION ===\n{validation_text}\n==================\n")
    audit["governance_response"] = validation_text

    if "REJECTED" in validation_text:
        print("[-] Governance rejected the plan. Aborting execution.")
        audit["governance_status"] = "REJECTED"
        _write_audit_summary(audit)
        _write_provision_artifact(audit)
        return

    if "APPROVED" not in validation_text:
        print("[-] Governance response was ambiguous. Aborting execution for safety.")
        audit["governance_status"] = "AMBIGUOUS"
        _write_audit_summary(audit)
        _write_provision_artifact(audit)
        return

    audit["governance_status"] = "APPROVED"

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
            
    print(f"\n=== EXECUTION RESULT ===\n{exec_text}\n========================\n")
    audit["execution_result"] = exec_text
    _write_audit_summary(audit)
    _write_provision_artifact(audit)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShieldInfra: DevSecOps AI Provisioner")
    parser.add_argument("--request", type=str, required=False,
                        help="Natural language infrastructure request")
    parser.add_argument("--index", type=int, default=1,
                        help="Instance index when running as part of a parallel matrix (1-based)")
    parser.add_argument("--count", type=int, default=1,
                        help="Total number of instances being provisioned in this run")
    args = parser.parse_args()

    base_request = args.request or "Create a VM in us-central1 for order service in dev"

    if args.count > 1:
        # ── Deterministic suffix injection ───────────────────────────────────
        # Parse the 'Instance Name: <name>' field out of the request and
        # rewrite it to '<name>-{index}' BEFORE sending to the Planner LLM.
        # This guarantees unique, govenance-compliant names regardless of how
        # the LLM interprets free-text instructions.
        import re

        def _inject_index_suffix(request_text: str, idx: int) -> str:
            """
            Find 'Instance Name: <value>' in the request and append '-<idx>' to
            the value. Uses re.sub with word boundaries to avoid double-replacing
            the name after it has already been suffixed.
            """
            pattern = r'(Instance Name\s*:\s*)(\S+)'
            match = re.search(pattern, request_text, re.IGNORECASE)

            if match:
                original_name = match.group(2)
                suffixed_name = f"{original_name}-{idx}"

                # Replace ALL occurrences of the bare original_name with the
                # suffixed version in ONE pass using a word-boundary pattern,
                # so the already-suffixed text is never touched a second time.
                name_pattern = r'(?<!\w)' + re.escape(original_name) + r'(?!\w|-\d)'
                request_text = re.sub(name_pattern, suffixed_name, request_text)

            # Belt-and-suspenders instruction for the LLM
            request_text += (
                f"\n\n[SYSTEM] This is parallel instance {idx} of {args.count}. "
                f"All resource names MUST carry the '-{idx}' suffix already injected above. "
                f"CRITICAL: Generate gcloud/cloud CLI commands for EXACTLY ONE resource (this instance only). "
                f"Do NOT generate commands for multiple resources or loop over the count — "
                f"the other {args.count - 1} instance(s) are handled by separate parallel jobs."
            )
            return request_text

        req = _inject_index_suffix(base_request, args.index)
        print(f"\n[+] Instance {args.index}/{args.count} — request after suffix injection:\n{req}\n")
    else:
        req = base_request

    try:
        asyncio.run(run_provisioning_flow(req, instance_index=args.index, total_count=args.count))
    except RuntimeError as e:
        # Suppress the known anyio/asyncio MCP session teardown error.
        # This error fires AFTER provisioning completes successfully, during
        # cleanup of the MCP stdio connection in a different asyncio task.
        # It does NOT indicate a provisioning failure.
        if "cancel scope" in str(e).lower():
            print(f"[~] Ignoring known MCP session teardown warning: {e}")
            sys.exit(0)
        raise
