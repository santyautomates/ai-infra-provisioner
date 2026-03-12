# AI Infrastructure Provisioner: Code Explanation

This document provides a detailed breakdown of the source code for the AI Infrastructure Provisioner.

## 1. Orchestration: `main.py`
**File**: [main.py](../main.py)

The entry point of the application. It manages the sequential execution of three distinct agents:

- **`run_provisioning_flow(user_request)`**: This async function coordinates the three steps.
  - **Step 1: Planning**: Uses the `Infrastructure_Planner` agent. It collects the yields from the runner to build the raw `plan_text`.
  - **Step 2: Governance**: Passes the `plan_text` to the `Governance_Validator` agent. It checks if the final response contains `APPROVED` or `REJECTED`.
  - **Step 3: Execution**: If approved, passes the plan to the `Infrastructure_Executor` agent to physically run the commands.
- **MCP Setup**: Initializes the `McpToolset` pointing to `mcp_server.py` via `stdio`.

## 2. Infrastructure Governance: `mcp_server.py`
**File**: [mcp_server.py](../mcp_server.py)

A **FastMCP** server that provides tools for the agents to interact with "Source of Truth" data.

- **`POLICIES`**: A dictionary containing mock organizational data (allowed regions, naming conventions, machine types).
- **`get_organizational_policies()`**: A tool that returns the `POLICIES` as a JSON string for agents to consume.
- **`list_gcp_resources(resource_type)`**: A critical tool that runs `gcloud ... list` commands as subprocesses to return real-time resource state (e.g., networks, instances) in JSON format. This prevents agent hallucinations.
- **`load_dotenv()`**: Ensures the server process has access to `GOOGLE_CLOUD_PROJECT`.

## 3. The Agents: `agents/`
Each agent is defined with specialized system instructions to enforce their role.

### A. Infrastructure Planner
**File**: [planner/agent.py](../agents/planner/agent.py)
Translates the user's natural language into a detailed `gcloud` plan.
- **Strategy**: It is instructed to *always* call `list_gcp_resources` when a deletion is requested to find the exact name of the target.

### B. Governance Validator
**File**: [governance/agent.py](../agents/governance/agent.py)
Acts as a security filter.
- **Strategy**: It matches the planner's output against naming conventions and *re-verifies* resource existence using the MCP tool before issuing an `APPROVED` status.

### C. Infrastructure Executor
**File**: [executor/agent.py](../agents/executor/agent.py)
A mechanical executor.
- **Strategy**: Its only job is to take the raw gcloud commands from an approved plan and invoke the `run_gcloud` tool.

## 4. Execution Tool: `tools.py`
**File**: [tools.py](../tools.py)

Contains the `run_gcloud` function, which is the only tool allowed to make changes to GCP.
- **`subprocess.run(cmd, shell=True, ...)`**: Securely executes the gcloud CLI.
- **Justification Logging**: Logs the justification provided by the executor for auditing purposes.

## Key Logic Patterns

### Preventing Hallucinations
When you ask to "delete the network", the Planner doesn't guess the name. It calls `list_gcp_resources("networks")`, receives a JSON list of real VPCs, and picks the one that matches the naming convention (e.g., `proj-dev-payment-vpc`).

### Safety First
The `GovernanceAgent` is designed to be pedantic. If the listing tool fails or the name is slightly off, it will **REJECT** the plan, which stops `main.py` from proceeding to the Execution step.
