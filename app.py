import os
import sys
import uuid
import streamlit as st
import requests
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- GitHub Workflow Integration ---
def trigger_github_workflow(github_pat, owner_repo, workflow_id, request_text, count: int = 1):
    """Triggers the GitHub Actions provisioning workflow."""
    url = f"https://api.github.com/repos/{owner_repo}/actions/workflows/{workflow_id}/dispatches"
    
    headers = {
        "Authorization": f"token {github_pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "ref": "main",
        "inputs": {
            "request": request_text,
            "count": str(count),       # Drives the parallel matrix (1–10)
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            instances_msg = f"{count} instance{'s' if count > 1 else ''}"
            return True, f"🚀 GitHub Workflow triggered! Provisioning **{instances_msg}** in parallel. Monitor in the Actions tab."
        else:
            return False, f"Failed to trigger workflow: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"An error occurred while triggering the workflow: {str(e)}"

# Streamlit page config
st.set_page_config(page_title="DevSecOps AI Infra Provisioner", page_icon="🛡️", layout="wide")

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 3.5rem; letter-spacing: -0.05em; margin-bottom: 0.5rem; background: -webkit-linear-gradient(45deg, #10b981, #3b82f6, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DevSecOps AI Infra Provisioner</h1>
    <p style="font-family: 'Inter', sans-serif; color: #64748b; font-size: 1.1rem; max-width: 700px; margin: 1rem auto;">🛡️ <b>DevSecOps</b>-native cloud infrastructure. AI-planned, policy-governed, and provisioned exclusively via <b>GitHub Actions</b>.</p>
</div>
""", unsafe_allow_html=True)

# --- Main App ---

# Replicated Agentic DevOps Sidebar
st.markdown("""
<style>
    /* Ultra-Modern AI Infra UI Styling (Dark & Glassmorphic) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Overall Background & Typography styling is usually controlled by Streamlit's config, 
       but we can enforce a modern aesthetic on our components */
    
    /* Glassmorphic Form Containers */
    div[data-testid="stForm"] {
        border-radius: 12px;
        padding: 24px;
        background: rgba(30, 34, 45, 0.6); /* Translucent dark slate */
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08); /* Subtle light border */
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        color: #e2e8f0;
    }
    
    /* Sleek Gradient Primary Button */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important; /* Indigo to Purple gradient */
        color: white !important;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -10px rgba(139, 92, 246, 0.5); /* Glowing shadow */
    }
    
    /* Tab Styling */
    div[data-testid="stTabs"] button[role="tab"] {
        border-radius: 6px 6px 0 0;
        font-weight: 500;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: rgba(99, 102, 241, 0.1);
        color: #8b5cf6 !important;
        border-bottom-color: #8b5cf6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize session state ---
if "request_history" not in st.session_state:
    st.session_state.request_history = []
if "session_uid" not in st.session_state:
    st.session_state.session_uid = str(uuid.uuid4())[:8]

# --- Sidebar Configuration ---
with st.sidebar:
    # GitHub Integration (collapsible)
    with st.expander("🐙 GitHub Integration", expanded=False):
        st.image("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", width=40)
        default_pat = os.getenv("GITHUB_PAT", "")
        github_pat = st.text_input("Personal Access Token (PAT)", value=default_pat, type="password", help="Required to trigger GitHub Actions workflows. Needs 'workflow' scope.")
        github_repo = st.text_input("Repository (owner/repo)", value="santyautomates/ai-infra-provisioner", help="Target GitHub repository for the workflow dispatch.")
        github_workflow = st.text_input("Workflow Filename", value="provision.yml", help="Filename inside .github/workflows/ to trigger.")
        st.info("💡 Set `GITHUB_PAT` in your `.env` to auto-fill.")

    # Housekeeping (collapsible)
    with st.expander("🧺 Housekeeping", expanded=False):
        st.write("Clean up cache files, logs, and temp artifacts.")
        if st.button("🧹 Run Housekeeping", use_container_width=True):
            try:
                script_path = os.path.join(os.getcwd(), "scripts", "optimize_codebase.sh")
                result = subprocess.run(["bash", script_path], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✨ Codebase optimized successfully!")
                    st.toast("Housekeeping complete!", icon="✅")
                    with st.expander("Show Details"):
                        st.code(result.stdout)
                else:
                    st.error("❌ Housekeeping failed.")
                    with st.expander("Show Errors"):
                        st.code(result.stderr)
            except Exception as e:
                st.error(f"Error running housekeeping: {str(e)}")

    # Request History Panel
    with st.expander("📋 Request History", expanded=False):
        if not st.session_state.request_history:
            st.info("No requests yet this session.")
        else:
            for i, entry in enumerate(reversed(st.session_state.request_history[-5:])):
                status_icon = "✅" if entry["status"] == "success" else "❌"
                st.markdown(f"**{status_icon} {entry['feature']}** `{entry['time']}`")
                st.caption(entry['summary'])
                if i < len(st.session_state.request_history) - 1:
                    st.divider()

st.markdown("### 🛠️ Configuration Panel")
with st.container():
    additional_input = ""
    service = ""

    # Use tabs to categorize features for a cleaner SaaS-like UI
    tab_cloud, tab_devops, tab_agentic, tab_utils = st.tabs(["☁️ Cloud Systems", "🚀 Pipeline & DevOps", "🤖 Agentic Apps", "🔧 Other Tools"])

    def reset_other_features(active_key):
        for key in ['cloud_feat', 'devops_feat', 'agentic_feat', 'utils_feat']:
            if key != active_key and key in st.session_state:
                st.session_state[key] = "Select a Feature"

    with tab_cloud:
        cloud_feature = st.selectbox("Select Cloud Provider", ["Select a Feature", "GCP Configuration", "AWS Configuration", "Azure Configuration"], key="cloud_feat", on_change=reset_other_features, args=("cloud_feat",))
    with tab_devops:
        devops_feature = st.selectbox("Select DevOps Activity", ["Select a Feature", "Create CI/CD Pipeline", "Create Kubernetes Configuration", "Create Dockerfile", "Create Bash Script"], key="devops_feat", on_change=reset_other_features, args=("devops_feat",))
    with tab_agentic:
        agentic_feature = st.selectbox("Select Agentic Service", ["Select a Feature", "Agentic Development"], key="agentic_feat", on_change=reset_other_features, args=("agentic_feat",))
    with tab_utils:
        utils_feature = st.selectbox("Select Utilities", ["Select a Feature", "Cloudflare Configuration", "Developer Configuration"], key="utils_feat", on_change=reset_other_features, args=("utils_feat",))

    feature = "Select a Feature"
    if cloud_feature != "Select a Feature": feature = cloud_feature
    elif devops_feature != "Select a Feature": feature = devops_feature
    elif agentic_feature != "Select a Feature": feature = agentic_feature
    elif utils_feature != "Select a Feature": feature = utils_feature
    additional_input = ""
    service = ""

    # Add secondary dropdowns and inputs based on the primary selection
    if feature == "Agentic Development":
        approach = st.selectbox(
            "Select an Agentic Approach",
            [
                "Select an Approach",  # Default option
                "Microservices Architecture",
                "Serverless Architecture",
                "Monolithic Architecture",
                "Event-Driven Architecture",
                "API-First Development",
                "DevOps and Continuous Delivery",
                "Agile Development",
                "Test-Driven Development (TDD)",
                "Behavior-Driven Development (BDD)",
                "Domain-Driven Design (DDD)"
            ]
        )

        if approach == "Microservices Architecture":
            st.markdown("### Microservices Architecture")
            st.write("Develop software as a suite of small services, each running in its own process and communicating with lightweight mechanisms.")
            app_name = st.text_input("Application Name", "MyMicroserviceApp")
            app_description = st.text_area("Application Description", "Description of the microservice application")
            services = st.text_area("List of Services (comma separated)", "auth-service, user-service, payment-service")
            technologies = st.text_input("Technologies (comma separated)", "Docker, Kubernetes, Spring Boot")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nServices: {services}\nTechnologies: {technologies}"
        elif approach == "Serverless Architecture":
            st.markdown("### Serverless Architecture")
            st.write("Develop software without managing the infrastructure, using cloud services to automatically handle scaling and server management.")
            app_name = st.text_input("Application Name", "MyServerlessApp")
            app_description = st.text_area("Application Description", "Description of the serverless application")
            functions = st.text_area("List of Functions (comma separated)", "login, register, processPayment")
            cloud_provider = st.selectbox("Cloud Provider", ["AWS Lambda", "Google Cloud Functions", "Azure Functions"])
            technologies = st.text_input("Technologies (comma separated)", "Node.js, Python, Go")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nFunctions: {functions}\nCloud Provider: {cloud_provider}\nTechnologies: {technologies}"
        elif approach == "Monolithic Architecture":
            st.markdown("### Monolithic Architecture")
            st.write("Develop software as a single, unified application.")
            app_name = st.text_input("Application Name", "MyMonolithicApp")
            app_description = st.text_area("Application Description", "Description of the monolithic application")
            modules = st.text_area("List of Modules (comma separated)", "auth, user, payment")
            technologies = st.text_input("Technologies (comma separated)", "Java, Spring, Hibernate")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nModules: {modules}\nTechnologies: {technologies}"
        elif approach == "Event-Driven Architecture":
            st.markdown("### Event-Driven Architecture")
            st.write("Develop software where events trigger actions or updates, promoting decoupling and flexibility.")
            app_name = st.text_input("Application Name", "MyEventDrivenApp")
            app_description = st.text_area("Application Description", "Description of the event-driven application")
            events = st.text_area("List of Events (comma separated)", "UserRegistered, OrderPlaced, PaymentProcessed")
            technologies = st.text_input("Technologies (comma separated)", "Kafka, RabbitMQ, AWS SNS")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nEvents: {events}\nTechnologies: {technologies}"
        elif approach == "API-First Development":
            st.markdown("### API-First Development")
            st.write("Develop software by designing the API first, ensuring consistent and reusable interfaces.")
            app_name = st.text_input("Application Name", "MyAPIApp")
            app_description = st.text_area("Application Description", "Description of the API-first application")
            api_endpoints = st.text_area("List of API Endpoints (comma separated)", "/login, /register, /payments")
            technologies = st.text_input("Technologies (comma separated)", "OpenAPI, Swagger, REST, GraphQL")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nAPI Endpoints: {api_endpoints}\nTechnologies: {technologies}"
        elif approach == "DevOps and Continuous Delivery":
            st.markdown("### DevOps and Continuous Delivery")
            st.write("Implement DevOps practices and continuous delivery pipelines for faster and more reliable software delivery.")
            app_name = st.text_input("Application Name", "MyDevOpsApp")
            app_description = st.text_area("Application Description", "Description of the DevOps application")
            ci_cd_tools = st.text_input("CI/CD Tools (comma separated)", "Jenkins, GitHub Actions, GitLab CI")
            monitoring_tools = st.text_input("Monitoring Tools (comma separated)", "Prometheus, Grafana, ELK Stack")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nCI/CD Tools: {ci_cd_tools}\nMonitoring Tools: {monitoring_tools}"
        elif approach == "Agile Development":
            st.markdown("### Agile Development")
            st.write("Develop software using Agile methodologies for iterative development and flexibility.")
            app_name = st.text_input("Application Name", "MyAgileApp")
            app_description = st.text_area("Application Description", "Description of the Agile application")
            agile_framework = st.selectbox("Agile Framework", ["Scrum", "Kanban", "XP"])
            sprint_duration = st.text_input("Sprint Duration", "2 weeks")
            technologies = st.text_input("Technologies (comma separated)", "JIRA, Confluence, Trello")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nAgile Framework: {agile_framework}\nSprint Duration: {sprint_duration}\nTechnologies: {technologies}"
        elif approach == "Test-Driven Development (TDD)":
            st.markdown("### Test-Driven Development (TDD)")
            st.write("Develop software by writing tests before implementing the functionality.")
            app_name = st.text_input("Application Name", "MyTDDApp")
            app_description = st.text_area("Application Description", "Description of the TDD application")
            test_frameworks = st.text_input("Test Frameworks (comma separated)", "JUnit, pytest, Mocha")
            technologies = st.text_input("Technologies (comma separated)", "Java, Python, JavaScript")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nTest Frameworks: {test_frameworks}\nTechnologies: {technologies}"
        elif approach == "Behavior-Driven Development (BDD)":
            st.markdown("### Behavior-Driven Development (BDD)")
            st.write("Develop software by writing specifications in a readable format for all stakeholders.")
            app_name = st.text_input("Application Name", "MyBDDApp")
            app_description = st.text_area("Application Description", "Description of the BDD application")
            bdd_frameworks = st.text_input("BDD Frameworks (comma separated)", "Cucumber, SpecFlow, Behave")
            technologies = st.text_input("Technologies (comma separated)", "Java, C#, Python")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nBDD Frameworks: {bdd_frameworks}\nTechnologies: {technologies}"
        elif approach == "Domain-Driven Design (DDD)":
            st.markdown("### Domain-Driven Design (DDD)")
            st.write("Develop software by focusing on the core domain and domain logic.")
            app_name = st.text_input("Application Name", "MyDDDApp")
            app_description = st.text_area("Application Description", "Description of the DDD application")
            bounded_contexts = st.text_area("Bounded Contexts (comma separated)", "Order, Payment, Inventory")
            technologies = st.text_input("Technologies (comma separated)", "Java, C#, .NET")
            additional_input = f"App Name: {app_name}\nApp Description: {app_description}\nBounded Contexts: {bounded_contexts}\nTechnologies: {technologies}"

    elif feature == "Create Dockerfile":
        base_image = st.text_input("Base Image", "python:3.8-slim")
        packages = st.text_input("Packages to install (comma separated)", "numpy, pandas")
        additional_input = f"Base Image: {base_image}\nPackages: {packages}"
    elif feature == "Create Bash Script":
        script_purpose = st.text_input("Script Purpose", "Deployment script")
        commands = st.text_area("Commands to include", "echo Hello World")
        additional_input = f"Script Purpose: {script_purpose}\nCommands: {commands}"
    elif feature == "Create Kubernetes Configuration":
        deployment_name = st.text_input("Deployment Name", "my-app-deployment")
        container_image = st.text_input("Container Image", "my-app:latest")
        cluster_name = st.text_input("Cluster Name", "my-cluster")
        namespaces = st.text_input("Namespaces (comma separated)", "default, production")
        additional_input = f"Deployment Name: {deployment_name}\nContainer Image: {container_image}\nCluster Name: {cluster_name}\nNamespaces: {namespaces}"

    elif feature == "Create CI/CD Pipeline":
        provider = st.selectbox(
            "Select a CI/CD Provider",
            [
                "Select a Provider",  # Default option
                "GitHub Actions"
            ]
        )

        if provider == "GitHub Actions":
            st.markdown("### GitHub Actions CI/CD Pipeline")
            st.write("Configure your CI/CD pipeline using GitHub Actions.")
            pipeline_name = st.text_input("Pipeline Name", "GitHub Actions Pipeline")
            stages = st.text_area("Stages (comma separated)", "build, test, deploy")
            additional_input = f"Pipeline Name: {pipeline_name}\nProvider: GitHub Actions\nStages: {stages}"

    elif feature == "Azure Configuration":
        service = st.selectbox(
            "Select Azure Service",
            [
                "Select Service",  # Default option
                "Hosting",
                "Networking",
                "IAM",
                "Database",
                "Storage",
                "DevOps",
                "AI & Machine Learning",
                "Monitoring",
                "Security"
            ]
        )
        if service == "Hosting":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure Hosting Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            app_service_name = st.text_input("App Service Name", "my-app-service")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            sku = st.selectbox("Pricing Tier (SKU)", ["F1", "B1", "B2", "B3", "S1", "S2", "S3", "P1v2", "P2v2", "P3v2"])
            os_type = st.selectbox("Operating System", ["Windows", "Linux"])
            runtime_stack = st.selectbox("Runtime Stack", [".NET", "Node", "Python", "Java", "PHP", "Ruby"])
            additional_input = f"Resource Group: {resource_group}\nApp Service Name: {app_service_name}\nRegion: {region}\nPricing Tier: {sku}\nOperating System: {os_type}\nRuntime Stack: {runtime_stack}"
        elif service == "Networking":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure Networking Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            vnet_name = st.text_input("VNet Name", "my-vnet")
            address_space = st.text_input("Address Space", "10.0.0.0/16")
            subnet_name = st.text_input("Subnet Name", "my-subnet")
            subnet_address = st.text_input("Subnet Address", "10.0.1.0/24")
            nsg_name = st.text_input("Network Security Group (NSG) Name", "my-nsg")
            additional_input = f"Resource Group: {resource_group}\nVNet Name: {vnet_name}\nAddress Space: {address_space}\nSubnet Name: {subnet_name}\nSubnet Address: {subnet_address}\nNSG Name: {nsg_name}"
        elif service == "IAM":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure IAM Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            role_assignment_name = st.text_input("Role Assignment Name", "my-role-assignment")
            role_definition = st.selectbox("Role Definition", ["Owner", "Contributor", "Reader", "User Access Administrator"])
            principal_id = st.text_input("Principal ID (User/Service Principal ID)", "user-or-sp-id")
            scope = st.text_input("Scope", "/subscriptions/{subscription-id}/resourceGroups/{resource-group}")
            additional_input = f"Resource Group: {resource_group}\nRole Assignment Name: {role_assignment_name}\nRole Definition: {role_definition}\nPrincipal ID: {principal_id}\nScope: {scope}"
        elif service == "Database":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure Database Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            db_type = st.selectbox("Database Type", ["SQL Database", "Cosmos DB", "MySQL", "PostgreSQL", "MariaDB"])
            if db_type == "SQL Database":
                db_name = st.text_input("Database Name", "my-sql-db")
                server_name = st.text_input("Server Name", "my-sql-server")
                collation = st.text_input("Collation", "SQL_Latin1_General_CP1_CI_AS")
                additional_input = f"Resource Group: {resource_group}\nDatabase Type: SQL Database\nDatabase Name: {db_name}\nServer Name: {server_name}\nCollation: {collation}"
            elif db_type == "Cosmos DB":
                account_name = st.text_input("Account Name", "my-cosmos-account")
                consistency_level = st.selectbox("Consistency Level", ["Strong", "Bounded Staleness", "Session", "Consistent Prefix", "Eventual"])
                additional_input = f"Resource Group: {resource_group}\nDatabase Type: Cosmos DB\nAccount Name: {account_name}\nConsistency Level: {consistency_level}"
            elif db_type == "MySQL":
                server_name = st.text_input("Server Name", "my-mysql-server")
                version = st.selectbox("Version", ["5.6", "5.7", "8.0"])
                additional_input = f"Resource Group: {resource_group}\nDatabase Type: MySQL\nServer Name: {server_name}\nVersion: {version}"
            elif db_type == "PostgreSQL":
                server_name = st.text_input("Server Name", "my-postgresql-server")
                version = st.selectbox("Version", ["9.6", "10", "11", "12", "13"])
                additional_input = f"Resource Group: {resource_group}\nDatabase Type: PostgreSQL\nServer Name: {server_name}\nVersion: {version}"
            elif db_type == "MariaDB":
                server_name = st.text_input("Server Name", "my-mariadb-server")
                version = st.selectbox("Version", ["10.2", "10.3", "10.4", "10.5"])
                additional_input = f"Resource Group: {resource_group}\nDatabase Type: MariaDB\nServer Name: {server_name}\nVersion: {version}"
        elif service == "Storage":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure Storage Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            storage_account_name = st.text_input("Storage Account Name", "mystorageaccount")
            sku = st.selectbox("SKU", ["Standard_LRS", "Standard_GRS", "Standard_RAGRS", "Premium_LRS"])
            access_tier = st.selectbox("Access Tier", ["Hot", "Cool"])
            additional_input = f"Resource Group: {resource_group}\nStorage Account Name: {storage_account_name}\nSKU: {sku}\nAccess Tier: {access_tier}"
        elif service == "DevOps":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure DevOps Configuration</h3></div>""", unsafe_allow_html=True)
            project_name = st.text_input("Project Name", "my-devops-project")
            repo_name = st.text_input("Repository Name", "my-repo")
            pipeline_name = st.text_input("Pipeline Name", "my-pipeline")
            additional_input = f"Project Name: {project_name}\nRepository Name: {repo_name}\nPipeline Name: {pipeline_name}"
        elif service == "AI & Machine Learning":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure AI & Machine Learning Configuration</h3></div>""", unsafe_allow_html=True)
            workspace_name = st.text_input("Workspace Name", "my-ml-workspace")
            resource_group = st.text_input("Resource Group", "my-resource-group")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            additional_input = f"Workspace Name: {workspace_name}\nResource Group: {resource_group}\nRegion: {region}"
        elif service == "Monitoring":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure Monitoring Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            log_analytics_workspace = st.text_input("Log Analytics Workspace", "my-log-analytics")
            alert_rules = st.text_area("Alert Rules (comma separated)", "High CPU,Low Memory")
            additional_input = f"Resource Group: {resource_group}\nLog Analytics Workspace: {log_analytics_workspace}\nAlert Rules: {alert_rules}"
        elif service == "Security":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjA2ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI0MiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkd2eUhya08wSiIgeDE9IjU4Ljk3MiUiIHgyPSIzNy4xOTElIiB5MT0iNy40MTElIiB5Mj0iMTAzLjc2MiUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMxMTRBOEIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwNjY5QkMiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHaWZJT0RjVlIiIHgxPSI1OS43MTklIiB4Mj0iNTIuNjkxJSIgeTE9IjUyLjMxMyUiIHkyPSI1NC44NjQlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLW9wYWNpdHk9Ii4zIi8+PHN0b3Agb2Zmc2V0PSI3LjElIiBzdG9wLW9wYWNpdHk9Ii4yIi8+PHN0b3Agb2Zmc2V0PSIzMi4xJSIgc3RvcC1vcGFjaXR5PSIuMSIvPjxzdG9wIG9mZnNldD0iNjIuMyUiIHN0b3Atb3BhY2l0eT0iLjA1Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLW9wYWNpdHk9IjAiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iU1ZHa1Q1RjdiMmwiIHgxPSIzNy4yNzklIiB4Mj0iNjIuNDczJSIgeTE9IjQuNiUiIHkyPSI5OS45NzklIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjM0NDQkY0Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMjg5MkRGIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHBhdGggZmlsbD0idXJsKCNTVkd2eUhya08wSikiIGQ9Ik04NS4zNDMuMDAzaDc1Ljc1M0w4Mi40NTcgMjMzYTEyLjA4IDEyLjA4IDAgMCAxLTExLjQ0MiA4LjIxNkgxMi4wNkExMi4wNiAxMi4wNiAwIDAgMSAuNjMzIDIyNS4zMDNMNzMuODk4IDguMjE5QTEyLjA4IDEyLjA4IDAgMCAxIDg1LjM0MyAweiIvPjxwYXRoIGZpbGw9IiMwMDc4RDQiIGQ9Ik0xOTUuNDIzIDE1Ni4yODJINzUuMjk3YTUuNTYgNS41NiAwIDAgMC0zLjc5NiA5LjYyN2w3Ny4xOSA3Mi4wNDdhMTIuMTQgMTIuMTQgMCAwIDAgOC4yOCAzLjI2aDY4LjAyeiIvPjxwYXRoIGZpbGw9InVybCgjU1ZHaWZJT0RjVlIpIiBkPSJNODUuMzQzLjAwM2ExMS45OCAxMS45OCAwIDAgMC0xMS40NzEgOC4zNzZMLjcyMyAyMjUuMTA1YTEyLjA0NSAxMi4wNDUgMCAwIDAgMTEuMzcgMTYuMTEyaDYwLjQ3NWExMi45MyAxMi45MyAwIDAgMCA5LjkyMS04LjQzN2wxNC41ODgtNDIuOTkxbDUyLjEwNSA0OC42YTEyLjMzIDEyLjMzIDAgMCAwIDcuNzU3IDIuODI4aDY3Ljc2NmwtMjkuNzIxLTg0LjkzNWwtODYuNjQzLjAyTDE2MS4zNy4wMDN6Ii8+PHBhdGggZmlsbD0idXJsKCNTVkdrVDVGN2IybCkiIGQ9Ik0xODIuMDk4IDguMjA3QTEyLjA2IDEyLjA2IDAgMCAwIDE3MC42Ny4wMDNIODYuMjQ1YzUuMTc1IDAgOS43NzMgMy4zMDEgMTEuNDI4IDguMjA0TDE3MC45NCAyMjUuM2ExMi4wNjIgMTIuMDYyIDAgMCAxLTExLjQyOCAxNS45Mmg4NC40MjlhMTIuMDYyIDEyLjA2MiAwIDAgMCAxMS40MjUtMTUuOTJ6Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Azure Security Configuration</h3></div>""", unsafe_allow_html=True)
            resource_group = st.text_input("Resource Group", "my-resource-group")
            security_center_policy = st.text_area("Security Center Policy", "Enable all security recommendations")
            additional_input = f"Resource Group: {resource_group}\nSecurity Center Policy: {security_center_policy}"

    # AWS Config   
    elif feature == "AWS Configuration":
        service = st.selectbox(
            "Select AWS Service",
            [
                "Select Service",  # Default option
                "Hosting",
                "Networking",
                "IAM",
                "Database",
                "Storage",
                "DevOps",
                "AI & Machine Learning",
                "Monitoring",
                "Security"
            ]
        )
        if service == "Hosting":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkdiR2ZjcnZvViIgeDE9IjAlIiB4Mj0iMTAwJSIgeTE9IjEwMCUiIHkyPSIwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI0M4NTExQiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0Y5MCIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxwYXRoIGZpbGw9InVybCgjU1ZHYkdmY3J2b1YpIiBkPSJNMCAwaDI1NnYyNTZIMHoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJNODYuNCAxNjkuNmg4MHYtODBoLTgwem04Ni40LTgwaDEyLjhWOTZoLTEyLjh2MTIuOGgxMi44djYuNGgtMTIuOHY5LjZoMTIuOHY2LjRoLTEyLjhWMTQ0aDEyLjh2Ni40aC0xMi44djEyLjhoMTIuOHY2LjRoLTEyLjh2LjQzNWE1Ljk3IDUuOTcgMCAwIDEtNS45NjUgNS45NjVoLS40MzV2MTIuOEgxNjBWMTc2aC0xMi44djEyLjhoLTYuNFYxNzZoLTkuNnYxMi44aC02LjRWMTc2SDExMnYxMi44aC02LjRWMTc2SDkyLjh2MTIuOGgtNi40VjE3NmgtLjQzNUE1Ljk3IDUuOTcgMCAwIDEgODAgMTcwLjAzNXYtLjQzNWgtOS42di02LjRIODB2LTEyLjhoLTkuNlYxNDRIODB2LTEyLjhoLTkuNnYtNi40SDgwdi05LjZoLTkuNnYtNi40SDgwVjk2aC05LjZ2LTYuNEg4MHYtLjQzNWE1Ljk3IDUuOTcgMCAwIDEgNS45NjUtNS45NjVoLjQzNVY3MC40aDYuNHYxMi44aDEyLjhWNzAuNGg2LjR2MTIuOGgxMi44VjcwLjRoNi40djEyLjhoOS42VjcwLjRoNi40djEyLjhIMTYwVjcwLjRoNi40djEyLjhoLjQzNWE1Ljk3IDUuOTcgMCAwIDEgNS45NjUgNS45NjV6bS00MS42IDEyMS4yMDNhLjQuNCAwIDAgMS0uMzk3LjM5N0g0NS4xOTdhLjQuNCAwIDAgMS0uMzk3LS4zOTd2LTg1LjYwNmEuNC40IDAgMCAxIC4zOTctLjM5N0g2NHYtNi40SDQ1LjE5N2E2LjgwNSA2LjgwNSAwIDAgMC02Ljc5NyA2Ljc5N3Y4NS42MDZhNi44MDUgNi44MDUgMCAwIDAgNi43OTcgNi43OTdoODUuNjA2YTYuODA1IDYuODA1IDAgMCAwIDYuNzk3LTYuNzk3VjE5NS4yaC02LjR6bTg2LjQtMTY1LjYwNnY4NS42MDZhNi44MDUgNi44MDUgMCAwIDEtNi43OTcgNi43OTdIMTkydi02LjRoMTguODAzYS40LjQgMCAwIDAgLjM5Ny0uMzk3VjQ1LjE5N2EuNC40IDAgMCAwLS4zOTctLjM5N2gtODUuNjA2YS40LjQgMCAwIDAtLjM5Ny4zOTdWNjRoLTYuNFY0NS4xOTdhNi44MDUgNi44MDUgMCAwIDEgNi43OTctNi43OTdoODUuNjA2YTYuODA1IDYuODA1IDAgMCAxIDYuNzk3IDYuNzk3Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS Hosting Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            ec2_instance_type = st.text_input("EC2 Instance Type", "t2.micro")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            additional_input = f"Stack Name: {stack_name}\nEC2 Instance Type: {ec2_instance_type}\nRegion: {region}"
        elif service == "Networking":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkdaREJMdHkyQiIgeDE9IjAlIiB4Mj0iMTAwJSIgeTE9IjEwMCUiIHkyPSIwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzREMjdBOCIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0ExNjZGRiIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxwYXRoIGZpbGw9InVybCgjU1ZHWkRCTHR5MkIpIiBkPSJNMCAwaDI1NnYyNTZIMHoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJtMTk1LjIgMTMyLjM5bC0xNy42LTcuMDR2NjMuODQzYzUuMTQtLjUxMiA5LjI4My0yLjIwMiAxMi4yMjctNS4xOWM1LjQ0LTUuNTMgNS4zNzYtMTMuNjM2IDUuMzczLTEzLjcxNnptLTI0IDU2Ljg0NFYxMjUuMzVsLTE3LjYgNy4wNHYzNy44MzRjLjAyMi42NjIuNzQ5IDE3LjE0MiAxNy42IDE5LjAxMW0zMC40LTE5LjAxMWMuMDEuMzYyLjE3IDEwLjcxLTcuMTUyIDE4LjIwOGMtNC43ODcgNC45MDYtMTEuNTM2IDcuMzkyLTIwLjA0OCA3LjM5MmMtMjEuMDM0IDAtMjYuOTkyLTE2LjY5OC0yNy4yLTI1LjUyM3YtNDAuMDc3YzAtMS4zMDkuNzk3LTIuNDg2IDIuMDEzLTIuOTczbDI0LTkuNmEzLjIgMy4yIDAgMCAxIDIuMzc0IDBsMjQgOS42YTMuMiAzLjIgMCAwIDEgMi4wMTMgMi45NzN6bTkuNjAzLTYuMjkxbC0uMDAzLTQyLjc0M2wtMzYuOC0xNC43MmwtMzYuOCAxNC43MnY0Mi42MzRjLS4wMDYuMjkxLS40MzIgMTkuOTMgMTEuMzA5IDMyLjAxM2M2LjE4MiA2LjM2MSAxNC43NTggOS41ODcgMjUuNDkxIDkuNTg3YzEwLjgwNiAwIDE5LjQyNC0zLjI0OCAyNS42MTMtOS42NTFjMTEuNzI1LTEyLjEzNSAxMS4xOTctMzEuNjQ1IDExLjE5LTMxLjg0bS02LjU4OSAzNi4yODVjLTcuNDQgNy43MDItMTcuNjA2IDExLjYwNi0zMC4yMTQgMTEuNjA2Yy0xMi41NDcgMC0yMi42NzgtMy44OTEtMzAuMTEyLTExLjU2NWMtMTMuNjI5LTE0LjA1Ny0xMy4xMTctMzUuNjI1LTEzLjA4OC0zNi41MzR2LTQ0LjcwMWMwLTEuMzA5Ljc5Ny0yLjQ4NiAyLjAxMy0yLjk3M2w0MC0xNmEzLjIgMy4yIDAgMCAxIDIuMzc0IDBsNDAgMTZhMy4yIDMuMiAwIDAgMSAyLjAxMyAyLjk3M3Y0NC44Yy4wMjkuOC42MDUgMjIuMzMtMTIuOTg2IDM2LjM5NE03My43NzYgMTUxLjAyM0gxMjEuNnY2LjRINzMuNzc2Yy0xOS40NSAwLTM0LjI5OC0xMi45NjYtMzUuMy0zMC44MzJjLS4wNy0uNzMtLjA3Ni0xLjU4LS4wNzYtMi40MzJjMC0yMS45OCAxNS4zNy0zMC4wNzQgMjQuMzMzLTMyLjkyMmE1MCA1MCAwIDAgMS0uMDk2LTMuMTEzYzAtMTcuNDUgMTIuNDQ4LTM1LjcwNiAyOC45NS00Mi40NjRjMTkuMzgtNy45MzYgMzkuODExLTQuMDkzIDU0LjYzNyAxMC4yNjJjNC45OTUgNC44NjcgOC44MDMgMTAuMDY0IDExLjU1OCAxNS43ODljMy44Ni0zLjMxMiA4LjUxOS01LjA5MSAxMy41MS01LjA5MWMxMC41NzcgMCAyMS43NjQgOC4zIDIzLjY4NyAyNC4yMDFjNi45ODYgMS43NiAxNS43NTQgNS40OTggMjEuOTQzIDEzLjQzNGwtNS4wNDQgMy45MzZjLTUuNzAyLTcuMzE1LTE0LjMwNy0xMC4zNjItMjAuNTE4LTExLjYzNWEzLjE5IDMuMTkgMCAwIDEtMi41NTQtMi45NDRjLS44MzUtMTQuMTQ3LTkuNjY0LTIwLjU5Mi0xNy41MTMtMjAuNTkyYy00LjY3OSAwLTguODI2IDIuMjA4LTExLjk5NyA2LjM4NGEzLjE2IDMuMTYgMCAwIDEtMy4wMjQgMS4yMzJhMy4yIDMuMiAwIDAgMS0yLjUyOC0yLjA2NGMtMi40NTQtNi42ODgtNi4zNzEtMTIuNTk1LTExLjk3OC0xOC4wNThjLTEyLjk0LTEyLjUyNS0zMC44MDMtMTUuODY5LTQ3Ljc1My04LjkzMWMtMTQuMjM3IDUuODMtMjQuOTc2IDIxLjU0LTI0Ljk3NiAzNi41NGMwIDEuNzMyLjA5OSAzLjQ0NC4zIDUuMDg2YTMuMjA0IDMuMjA0IDAgMCAxLTIuNDA5IDMuNDljLTguMjYyIDIuMDQ2LTIyLjEyOCA4LjMzNy0yMi4xMjggMjcuNDZjMCAuNjQ2LS4wMDYgMS4yOTYuMDU4IDEuOTQ2Yy44MTIgMTQuNDkgMTIuOTcyIDI0LjkxOCAyOC45MTggMjQuOTE4Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS Networking Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            vpc_id = st.text_input("VPC ID", "vpc-123456")
            subnet_id = st.text_input("Subnet ID", "subnet-123456")
            security_group_id = st.text_input("Security Group ID", "sg-123456")
            additional_input = f"Stack Name: {stack_name}\nVPC ID: {vpc_id}\nSubnet ID: {subnet_id}\nSecurity Group ID: {security_group_id}"
        elif service == "IAM":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkdoRTZzSmNHQyIgeDE9IjAlIiB4Mj0iMTAwJSIgeTE9IjEwMCUiIHkyPSIwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI0JEMDgxNiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iI0ZGNTI1MiIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxwYXRoIGZpbGw9InVybCgjU1ZHaEU2c0pjR0MpIiBkPSJNMCAwaDI1NnYyNTZIMHoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJNNDQuOCAxODguOGgxNjYuNFY2Ny4ySDQ0Ljh6TTIxNy42IDY0djEyOGEzLjIgMy4yIDAgMCAxLTMuMiAzLjJINDEuNmEzLjIgMy4yIDAgMCAxLTMuMi0zLjJWNjRhMy4yIDMuMiAwIDAgMSAzLjItMy4yaDE3Mi44YTMuMiAzLjIgMCAwIDEgMy4yIDMuMm0tNzYuOCA4OS42aDQ4di02LjRoLTQ4em00MS42LTE5LjJoMTZWMTI4aC0xNnptLTQxLjYgMGgyNS42VjEyOGgtMjUuNnptLTQ4IDEyLjhjMC0xLjc2My0xLjQzNC0zLjItMy4yLTMuMmEzLjIwMyAzLjIwMyAwIDAgMC0zLjIgMy4yYzAgMS43NjMgMS40MzQgMy4yIDMuMiAzLjJzMy4yLTEuNDM3IDMuMi0zLjJtNi40IDBjMCA0LjE2Ni0yLjY4NSA3LjY4My02LjQgOS4wMTF2Ni45ODloLTYuNHYtNi45OTJjLTMuNzE1LTEuMzI1LTYuNC00Ljg0Mi02LjQtOS4wMDhjMC01LjI5MyA0LjMwNy05LjYgOS42LTkuNnM5LjYgNC4zMDcgOS42IDkuNm0tMzguNCAyNS41NzhsNTcuNTguMDIybC4wMDctMTIuOEgxMDUuNnYtNi40aDEyLjc4N2wuMDA3LTkuNkgxMDUuNnYtNi40aDEyLjc5N2wuMDAzLTkuNTc4TDYwLjgyIDEyOHptOS42LTUxLjE3NWwzOC40LjAxNlY5OS4yYy4wMDMtNy4zNy04Ljk3LTEzLjgzNC0xOS4yLTEzLjg0aC0uMDEzYy0xMC4yMTQgMC0xOS4xNzQgNi40NjctMTkuMTggMTMuODR6bS0xNiA1NC4zNzFsLjAyLTUxLjE3NGEzLjIgMy4yIDAgMCAxIDMuMi0zLjJsNi4zOC4wMDNsLjAwNi0yMi40MDNjLjAwNy0xMS4xNjIgMTEuNDgyLTIwLjI0IDI1LjU4MS0yMC4yNGguMDEzYzE0LjExOC4wMDYgMjUuNjAzIDkuMDg4IDI1LjYgMjAuMjR2MjIuNDIybDYuNC4wMDRhMy4yIDMuMiAwIDAgMSAzLjIgMy4yTDEyNC43OCAxNzZhMy4yIDMuMiAwIDAgMS0zLjIgMy4ybC02My45OC0uMDI2YTMuMiAzLjIgMCAwIDEtMy4yLTMuMk0xOTIgMTE1LjJoNi40di02LjRIMTkyem0tNTEuMiAwSDE3NnYtNi40aC0zNS4yeiIvPjwvc3ZnPg==\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS IAM Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            role_name = st.text_input("Role Name", "my-role")
            policy_arn = st.text_input("Policy ARN", "arn:aws:iam::aws:policy/AdministratorAccess")
            additional_input = f"Stack Name: {stack_name}\nRole Name: {role_name}\nPolicy ARN: {policy_arn}"
        elif service == "Database":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkdXVE9iUmRjeCIgeDE9IjAlIiB4Mj0iMTAwJSIgeTE9IjEwMCUiIHkyPSIwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzJFMjdBRCIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzUyN0ZGRiIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxwYXRoIGZpbGw9InVybCgjU1ZHV1RPYlJkY3gpIiBkPSJNMCAwaDI1NnYyNTZIMHoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJtNDkuMzI1IDQ0LjhsMjkuNzM3IDI5LjczOGwtNC41MjQgNC41MjRMNDQuOCA0OS4zMjVWNzMuNmgtNi40di0zMmEzLjIgMy4yIDAgMCAxIDMuMi0zLjJoMzJ2Ni40ek0yMTcuNiA0MS42djMyaC02LjRWNDkuMzI1bC0yOS43MzggMjkuNzM3bC00LjUyNC00LjUyNEwyMDYuNjc1IDQ0LjhIMTgyLjR2LTYuNGgzMmEzLjIgMy4yIDAgMCAxIDMuMiAzLjJtLTYuNCAxNDAuOGg2LjR2MzJhMy4yIDMuMiAwIDAgMS0zLjIgMy4yaC0zMnYtNi40aDI0LjI3NWwtMjkuNzM3LTI5LjczOGw0LjUyNC00LjUyNGwyOS43MzggMjkuNzM3em0tMS42LTU2LjkxOGMwLTEwLjYyMS0xMi4yNjItMjEuMTE0LTMyLjgtMjguMDY4bDIuMDUxLTYuMDZDMjAyLjQ1OCA5OS4zNDQgMjE2IDExMS43ODIgMjE2IDEyNS40ODJjMCAxMy43MDItMTMuNTQyIDI2LjE0NC0zNy4xNTIgMzQuMTNsLTIuMDUxLTYuMDYzYzIwLjU0LTYuOTUgMzIuODAzLTE3LjQ0IDMyLjgwMy0yOC4wNjdtLTE2My4wMiAwYzAgMTAuMTc2IDExLjQ3OCAyMC4zOSAzMC43MDYgMjcuMzI4bC0yLjE3MiA2LjAxOWMtMjIuMjAyLTguMDEtMzQuOTM1LTIwLjE2My0zNC45MzUtMzMuMzQ3YzAtMTMuMTgxIDEyLjczMy0yNS4zMzUgMzQuOTM1LTMzLjM0OGwyLjE3MiA2LjAyYy0xOS4yMjggNi45NC0zMC43MDcgMTcuMTU1LTMwLjcwNyAyNy4zMjhtMzIuNDgyIDU1Ljk4TDQ5LjMyNSAyMTEuMkg3My42djYuNGgtMzJhMy4yIDMuMiAwIDAgMS0zLjItMy4ydi0zMmg2LjR2MjQuMjc1bDI5LjczOC0yOS43Mzd6TTEyOCAxMDAuMTE1Yy0yMi44NjcgMC0zNS4yLTUuOTA3LTM1LjItOC4zMmMwLTIuNDE2IDEyLjMzMy04LjMyIDM1LjItOC4zMmMyMi44NjQgMCAzNS4yIDUuOTA0IDM1LjIgOC4zMmMwIDIuNDEzLTEyLjMzNiA4LjMyLTM1LjIgOC4zMm0uMDkzIDI0Ljc4NGMtMjEuODk1IDAtMzUuMjkzLTUuOTgtMzUuMjkzLTkuMjM1di0xNS41NTVjNy44ODIgNC4zNDkgMjEuODYyIDYuNDA2IDM1LjIgNi40MDZzMjcuMzE4LTIuMDU3IDM1LjItNi40MDZ2MTUuNTU1YzAgMy4yNTgtMTMuMzI4IDkuMjM1LTM1LjEwNyA5LjIzNW0wIDI0LjQzNWMtMjEuODk1IDAtMzUuMjkzLTUuOTgtMzUuMjkzLTkuMjM1di0xNS43NGM3Ljc4IDQuNTcyIDIxLjU3NCA2Ljk0IDM1LjI5MyA2Ljk0YzEzLjY0MSAwIDI3LjM1Ny0yLjM2NSAzNS4xMDctNi45MjVWMTQwLjFjMCAzLjI1OC0xMy4zMjggOS4yMzUtMzUuMTA3IDkuMjM1TTEyOCAxNzEuMjU4Yy0yMi43NzQgMC0zNS4yLTYuMTIyLTM1LjItOS4yNjh2LTEzLjE5NmM3Ljc4IDQuNTcyIDIxLjU3NCA2Ljk0IDM1LjI5MyA2Ljk0YzEzLjY0MSAwIDI3LjM1Ny0yLjM2MSAzNS4xMDctNi45MjR2MTMuMThjMCAzLjE0Ni0xMi40MjYgOS4yNjgtMzUuMiA5LjI2OG0wLTk0LjE4M2MtMjAuMDM1IDAtNDEuNiA0LjYwNS00MS42IDE0LjcydjcwLjE5NWMwIDEwLjI4NSAyMC45MjggMTUuNjY4IDQxLjYgMTUuNjY4czQxLjYtNS4zODMgNDEuNi0xNS42NjhWOTEuNzk1YzAtMTAuMTE1LTIxLjU2NS0xNC43Mi00MS42LTE0LjcyIi8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS Database Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            db_type = st.selectbox("Database Type", ["RDS", "DynamoDB", "Aurora", "Redshift", "DocumentDB"])
            if db_type == "RDS":
                db_instance_identifier = st.text_input("DB Instance Identifier", "my-rds-instance")
                db_instance_class = st.text_input("DB Instance Class", "db.t2.micro")
                db_engine = st.selectbox("DB Engine", ["MySQL", "PostgreSQL", "MariaDB", "Oracle", "SQL Server"])
                additional_input = f"Stack Name: {stack_name}\nDatabase Type: RDS\nDB Instance Identifier: {db_instance_identifier}\nDB Instance Class: {db_instance_class}\nDB Engine: {db_engine}"
            elif db_type == "DynamoDB":
                table_name = st.text_input("Table Name", "my-dynamodb-table")
                read_capacity_units = st.number_input("Read Capacity Units", 1)
                write_capacity_units = st.number_input("Write Capacity Units", 1)
                additional_input = f"Stack Name: {stack_name}\nDatabase Type: DynamoDB\nTable Name: {table_name}\nRead Capacity Units: {read_capacity_units}\nWrite Capacity Units: {write_capacity_units}"
            elif db_type == "Aurora":
                cluster_identifier = st.text_input("Cluster Identifier", "my-aurora-cluster")
                db_instance_class = st.text_input("DB Instance Class", "db.r5.large")
                engine_mode = st.selectbox("Engine Mode", ["provisioned", "serverless"])
                additional_input = f"Stack Name: {stack_name}\nDatabase Type: Aurora\nCluster Identifier: {cluster_identifier}\nDB Instance Class: {db_instance_class}\nEngine Mode: {engine_mode}"
            elif db_type == "Redshift":
                cluster_identifier = st.text_input("Cluster Identifier", "my-redshift-cluster")
                node_type = st.text_input("Node Type", "dc2.large")
                number_of_nodes = st.number_input("Number of Nodes", 1)
                additional_input = f"Stack Name: {stack_name}\nDatabase Type: Redshift\nCluster Identifier: {cluster_identifier}\nNode Type: {node_type}\nNumber of Nodes: {number_of_nodes}"
            elif db_type == "DocumentDB":
                cluster_identifier = st.text_input("Cluster Identifier", "my-docdb-cluster")
                db_instance_class = st.text_input("DB Instance Class", "db.r5.large")
                additional_input = f"Stack Name: {stack_name}\nDatabase Type: DocumentDB\nCluster Identifier: {cluster_identifier}\nDB Instance Class: {db_instance_class}"
        elif service == "Storage":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDI1NiI+PGRlZnM+PGxpbmVhckdyYWRpZW50IGlkPSJTVkdUSFo0d2RaViIgeDE9IjAlIiB4Mj0iMTAwJSIgeTE9IjEwMCUiIHkyPSIwJSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzFCNjYwRiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzZDQUUzRSIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxwYXRoIGZpbGw9InVybCgjU1ZHVEhaNHdkWlYpIiBkPSJNMCAwaDI1NnYyNTZIMHoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJtMTk0LjY3NSAxMzcuMjU2bDEuMjI5LTguNjUyYzExLjMzIDYuNzg3IDExLjQ3OCA5LjU5IDExLjQ3NSA5LjY2N2MtLjAyLjAxNi0xLjk1MiAxLjYyOS0xMi43MDQtMS4wMTVtLTYuMjE4LTEuNzI4Yy0xOS41ODQtNS45MjYtNDYuODU3LTE4LjQzOC01Ny44OTQtMjMuNjU0YzAtLjA0NS4wMTMtLjA4Ni4wMTMtLjEzMWMwLTQuMjQtMy40NS03LjY5LTcuNjkzLTcuNjljLTQuMjM3IDAtNy42ODcgMy40NS03LjY4NyA3LjY5czMuNDUgNy42OSA3LjY4NyA3LjY5YzEuODYyIDAgMy41NTItLjY5NSA0Ljg4Ni0xLjhjMTIuOTg2IDYuMTQ4IDQwLjA0OCAxOC40NzggNTkuNzc2IDI0LjMwMmwtNy44MDEgNTUuMDU5cS0uMDMzLjIyNS0uMDMyLjQ1MWMwIDQuODQ4LTIxLjQ2MyAxMy43NTQtNTYuNTMyIDEzLjc1NGMtMzUuNDQgMC01Ny4xMy04LjkwNi01Ny4xMy0xMy43NTRxMC0uMjItLjAyOC0uNDM1bC0xNi4zLTExOS4wNjJjMTQuMTA4IDkuNzEyIDQ0LjQ1NCAxNC44NSA3My40NzggMTQuODVjMjguOTc5IDAgNTkuMjczLTUuMTIgNzMuNDEtMTQuODAyek00OCA2NS41MjhjLjIzLTQuMjEgMjQuNDI4LTIwLjczIDc1LjItMjAuNzNjNTAuNzY0IDAgNzQuOTY2IDE2LjUxNiA3NS4yIDIwLjczdjEuNDM3Yy0yLjc4NCA5LjQ0My0zNC4xNDQgMTkuNDM0LTc1LjIgMTkuNDM0Yy00MS4xMjcgMC03Mi41MDMtMTAuMDIzLTc1LjItMTkuNDc5em0xNTYuOC4wN2MwLTExLjA4Ny0zMS43OS0yNy4yLTgxLjYtMjcuMmMtNDkuODEyIDAtODEuNiAxNi4xMTMtODEuNiAyNy4ybC4zIDIuNDE0bDE3Ljc1NCAxMjkuNjc2Yy40MjYgMTQuNTAzIDM5LjEgMTkuOTEgNjMuNTI2IDE5LjkxYzMwLjMxIDAgNjIuNTEyLTYuOTY5IDYyLjkyOC0xOS45bDcuNjY4LTU0LjA3YzQuMjY1IDEuMDIgNy43NzYgMS41NDIgMTAuNTk1IDEuNTQyYzMuNzg1IDAgNi4zNDUtLjkyNSA3Ljg5Ny0yLjc3NGMxLjI3NC0xLjUxNyAxLjc2LTMuMzU0IDEuMzk2LTUuMzFjLS44My00LjQyOC02LjA4Ny05LjIwMi0xNi43OTQtMTUuMzExbDcuNjAzLTUzLjYzOXoiLz48L3N2Zz4=\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS Storage Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            bucket_name = st.text_input("Bucket Name", "my-bucket")
            storage_class = st.selectbox("Storage Class", ["STANDARD", "INTELLIGENT_TIERING", "STANDARD_IA", "ONEZONE_IA", "GLACIER", "DEEP_ARCHIVE"])
            additional_input = f"Stack Name: {stack_name}\nBucket Name: {bucket_name}\nStorage Class: {storage_class}"
        elif service == "DevOps":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjY4ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDE1MyI+PHBhdGggZmlsbD0iIzI1MkYzRSIgZD0iTTcyLjM5MiA1NS40MzhjMCAzLjEzNy4zNCA1LjY4LjkzMyA3LjU0NWE0NS40IDQ1LjQgMCAwIDAgMi43MTIgNi4xMDNjLjQyNC42NzguNTkzIDEuMzU2LjU5MyAxLjk1YzAgLjg0Ny0uNTA4IDEuNjk1LTEuNjEgMi41NDNsLTUuMzQgMy41NmMtLjc2My41MDktMS41MjYuNzYzLTIuMjA1Ljc2M2MtLjg0NyAwLTEuNjk1LS40MjQtMi41NDMtMS4xODdhMjYgMjYgMCAwIDEtMy4wNTEtMy45ODRjLS44NDgtMS40NC0xLjY5Ni0zLjA1Mi0yLjYyOC01LjAwMXEtOS45MTkgMTEuNjk3LTI0LjkyMiAxMS42OThjLTcuMTIgMC0xMi44LTIuMDM1LTE2Ljk1NC02LjEwM2MtNC4xNTMtNC4wNy02LjI3Mi05LjQ5NS02LjI3Mi0xNi4yNzZjMC03LjIwNSAyLjU0My0xMy4wNTQgNy43MTQtMTcuNDYyYzUuMTctNC40MDggMTIuMDM3LTYuNjEyIDIwLjc2OC02LjYxMmMyLjg4MiAwIDUuODQ5LjI1NCA4Ljk4NS42NzhjMy4xMzcuNDI0IDYuMzU4IDEuMTAyIDkuNzQ5IDEuODY1VjI5LjMzYzAtNi40NDMtMS4zNTctMTAuOTM1LTMuOTg1LTEzLjU2M2MtMi43MTItMi42MjgtNy4yOS0zLjktMTMuODE3LTMuOWMtMi45NjcgMC02LjAxOC4zNC05LjE1NSAxLjEwM3MtNi4xODggMS42OTUtOS4xNTUgMi44ODJjLTEuMzU2LjU5My0yLjM3My45MzItMi45NjcgMS4xMDJzLTEuMDE3LjI1NC0xLjM1Ni4yNTRjLTEuMTg3IDAtMS43OC0uODQ4LTEuNzgtMi42Mjh2LTQuMTU0YzAtMS4zNTYuMTctMi4zNzMuNTkzLTIuOTY2Yy40MjQtLjU5NCAxLjE4Ny0xLjE4NyAyLjM3NC0xLjc4cTQuNDUtMi4yOSAxMC42OC0zLjgxNUMzMy45MDguNzYzIDM4LjMxNi4yNTUgNDIuOTc4LjI1NWMxMC4wODggMCAxNy40NjMgMi4yODggMjIuMjEgNi44NjZjNC42NjIgNC41NzcgNy4wMzYgMTEuNTI4IDcuMDM2IDIwLjg1M3YyNy40NjR6TTM3Ljk3NiA2OC4zMjNjMi43OTggMCA1LjY4LS41MDggOC43MzEtMS41MjZjMy4wNTItMS4wMTcgNS43NjUtMi44ODIgOC4wNTMtNS40MjVjMS4zNTctMS42MSAyLjM3NC0zLjM5IDIuODgyLTUuNDI1Yy41MDktMi4wMzQuODQ4LTQuNDkzLjg0OC03LjM3NXYtMy41NmE3MSA3MSAwIDAgMC03Ljc5OS0xLjQ0MWE2NCA2NCAwIDAgMC03Ljk2OC0uNTA5Yy01LjY4IDAtOS44MzMgMS4xMDItMTIuNjMgMy4zOTFzLTQuMTU0IDUuNTEtNC4xNTQgOS43NDhjMCAzLjk4NCAxLjAxNyA2Ljk1MSAzLjEzNiA4Ljk4NmMyLjAzNSAyLjExOSA1LjAwMiAzLjEzNiA4LjkwMSAzLjEzNm02OC4wNjkgOS4xNTVjLTEuNTI2IDAtMi41NDMtLjI1NC0zLjIyMS0uODQ4Yy0uNjc4LS41MDgtMS4yNzItMS42OTUtMS43OC0zLjMwNUw4MS4xMjQgNy43OTljLS41MS0xLjY5Ni0uNzY0LTIuNzk4LS43NjQtMy4zOTFjMC0xLjM1Ni42NzgtMi4xMiAyLjAzNS0yLjEyaDguMzA3YzEuNjEgMCAyLjcxMy4yNTUgMy4zMDYuODQ4Yy42NzguNTA5IDEuMTg3IDEuNjk2IDEuNjk1IDMuMzA2bDE0LjI0MSA1Ni4xMTdsMTMuMjI0LTU2LjExN2MuNDI0LTEuNjk1LjkzMy0yLjc5NyAxLjYxLTMuMzA2Yy42NzktLjUwOCAxLjg2Ni0uODQ3IDMuMzkyLS44NDdoNi43ODFjMS42MSAwIDIuNzEzLjI1NCAzLjM5Ljg0N2MuNjc5LjUwOSAxLjI3MiAxLjY5NiAxLjYxMSAzLjMwNmwxMy4zOTQgNTYuNzk1TDE2OC4wMSA2LjQ0MmMuNTA4LTEuNjk1IDEuMTAyLTIuNzk3IDEuNjk1LTMuMzA2Yy42NzgtLjUwOCAxLjc4LS44NDcgMy4zMDYtLjg0N2g3Ljg4M2MxLjM1NyAwIDIuMTIuNjc4IDIuMTIgMi4xMTljMCAuNDI0LS4wODUuODQ4LS4xNyAxLjM1NnMtLjI1NCAxLjE4Ny0uNTkzIDIuMTJsLTIwLjQzIDY1LjUyNXEtLjc2MiAyLjU0NC0xLjc4IDMuMzA2Yy0uNjc4LjUwOS0xLjc4Ljg0OC0zLjIyLjg0OGgtNy4yOWMtMS42MTEgMC0yLjcxMy0uMjU0LTMuMzkyLS44NDhjLS42NzgtLjU5My0xLjI3MS0xLjY5NS0xLjYxLTMuMzlsLTEzLjE0LTU0LjY3NmwtMTMuMDU0IDU0LjU5Yy0uNDIzIDEuNjk2LS45MzIgMi43OTgtMS42MSAzLjM5MWMtLjY3OC41OTQtMS44NjUuODQ4LTMuMzkuODQ4em0xMDguOTI3IDIuMjg5Yy00LjQwOCAwLTguODE2LS41MDktMTMuMDU0LTEuNTI2Yy00LjIzOS0xLjAxNy03LjU0NC0yLjEyLTkuNzQ4LTMuMzljLTEuMzU3LS43NjQtMi4yOS0xLjYxMS0yLjYyOC0yLjM3NGE2IDYgMCAwIDEtLjUwOS0yLjM3NFY2NS43OGMwLTEuNzguNjc4LTIuNjI4IDEuOTUtMi42MjhhNC44IDQuOCAwIDAgMSAxLjUyNi4yNTVjLjUwOC4xNyAxLjI3MS41MDggMi4xMTkuODQ3YTQ2IDQ2IDAgMCAwIDkuMzI0IDIuOTY3YTUxIDUxIDAgMCAwIDEwLjA4OCAxLjAxN2M1LjM0IDAgOS40OTQtLjkzMiAxMi4zNzYtMi43OTdzNC40MDgtNC41NzcgNC40MDgtOC4wNTNjMC0yLjM3My0uNzYzLTQuMzIzLTIuMjg5LTUuOTM0cy00LjQwOC0zLjA1MS04LjU2MS00LjQwOGwtMTIuMjkyLTMuODE0Yy02LjE4OC0xLjk1LTEwLjc2NS00LjgzMi0xMy41NjMtOC42NDdjLTIuNzk3LTMuNzMtNC4yMzgtNy44ODMtNC4yMzgtMTIuMjkxcTAtNS4zNCAyLjI4OS05LjQxYzEuNTI1LTIuNzEyIDMuNTYtNS4wODUgNi4xMDMtNi45NWMyLjU0My0xLjk1IDUuNDI1LTMuMzkxIDguODE2LTQuNDA4YzMuMzktMS4wMTcgNi45NS0xLjQ0MSAxMC42OC0xLjQ0MWMxLjg2NSAwIDMuODE1LjA4NSA1LjY4LjMzOWMxLjk1LjI1NCAzLjczLjU5MyA1LjUxLjkzMmMxLjY5NS40MjQgMy4zMDYuODQ4IDQuODMyIDEuMzU3cTIuMjg4Ljc2MiAzLjU2IDEuNTI1YzEuMTg3LjY3OSAyLjAzNCAxLjM1NyAyLjU0MyAyLjEycS43NjMgMS4wMTcuNzYzIDIuNzk3djMuOTg0YzAgMS43OC0uNjc4IDIuNzEzLTEuOTUgMi43MTNjLS42NzggMC0xLjc4LS4zNC0zLjIyLTEuMDE4cS03LjI1LTMuMzA2LTE2LjI3Ni0zLjMwNmMtNC44MzIgMC04LjY0Ny43NjMtMTEuMjc1IDIuMzc0Yy0yLjYyNyAxLjYxLTMuOTg0IDQuMDY5LTMuOTg0IDcuNTQ0YzAgMi4zNzQuODQ4IDQuNDA4IDIuNTQzIDYuMDE5czQuODMyIDMuMjIxIDkuMzI1IDQuNjYybDEyLjAzNyAzLjgxNWM2LjEwMyAxLjk1IDEwLjUxMSA0LjY2MiAxMy4xMzkgOC4xMzdzMy45IDcuNDYgMy45IDExLjg2OGMwIDMuNjQ1LS43NjQgNi45NTEtMi4yMDUgOS44MzNjLTEuNTI1IDIuODgyLTMuNTYgNS40MjUtNi4xODggNy40NmMtMi42MjggMi4xMTktNS43NjQgMy42NDUtOS40MDkgNC43NDdjLTMuODE1IDEuMTg3LTcuNzk5IDEuNzgtMTIuMTIyIDEuNzgiLz48cGF0aCBmaWxsPSIjRjkwIiBkPSJNMjMwLjk5MyAxMjAuOTY0Yy0yNy44ODggMjAuNTk5LTY4LjQwOCAzMS41MzQtMTAzLjI0NyAzMS41MzRjLTQ4LjgyNyAwLTkyLjgyMS0xOC4wNTYtMTI2LjA1LTQ4LjA2NGMtMi42MjgtMi4zNzMtLjI1NS01LjU5NCAyLjg4MS0zLjczYzM1Ljk0MiAyMC44NTQgODAuMjc2IDMzLjQ4NCAxMjYuMTM2IDMzLjQ4NGMzMC45NCAwIDY0LjkzMi02LjQ0MiA5Ni4yMTItMTkuNjY2YzQuNjYyLTIuMTIgOC42NDYgMy4wNTIgNC4wNjggNi40NDJtMTEuNjE0LTEzLjIyNGMtMy41Ni00LjU3Ny0yMy41NjYtMi4yMDQtMzIuNjM2LTEuMTAyYy0yLjcxMy4zNC0zLjEzNy0yLjAzNC0uNjc4LTMuODE0YzE1LjkzNi0xMS4xOSA0Mi4xMy03Ljk2OCA0NS4xODEtNC4yMzljMy4wNTIgMy44MTUtLjg0OCAzMC4wMDgtMTUuNzY3IDQyLjU1NGMtMi4yODggMS45NS00LjQ5Mi45MzMtMy40NzUtMS42MWMzLjM5LTguMzkzIDEwLjkzNS0yNy4yOTYgNy4zNzUtMzEuNzg5Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS DevOps Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            pipeline_name = st.text_input("Pipeline Name", "my-pipeline")
            repository_name = st.text_input("Repository Name", "my-repo")
            additional_input = f"Stack Name: {stack_name}\nPipeline Name: {pipeline_name}\nRepository Name: {repository_name}"
        elif service == "AI & Machine Learning":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjY4ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDE1MyI+PHBhdGggZmlsbD0iIzI1MkYzRSIgZD0iTTcyLjM5MiA1NS40MzhjMCAzLjEzNy4zNCA1LjY4LjkzMyA3LjU0NWE0NS40IDQ1LjQgMCAwIDAgMi43MTIgNi4xMDNjLjQyNC42NzguNTkzIDEuMzU2LjU5MyAxLjk1YzAgLjg0Ny0uNTA4IDEuNjk1LTEuNjEgMi41NDNsLTUuMzQgMy41NmMtLjc2My41MDktMS41MjYuNzYzLTIuMjA1Ljc2M2MtLjg0NyAwLTEuNjk1LS40MjQtMi41NDMtMS4xODdhMjYgMjYgMCAwIDEtMy4wNTEtMy45ODRjLS44NDgtMS40NC0xLjY5Ni0zLjA1Mi0yLjYyOC01LjAwMXEtOS45MTkgMTEuNjk3LTI0LjkyMiAxMS42OThjLTcuMTIgMC0xMi44LTIuMDM1LTE2Ljk1NC02LjEwM2MtNC4xNTMtNC4wNy02LjI3Mi05LjQ5NS02LjI3Mi0xNi4yNzZjMC03LjIwNSAyLjU0My0xMy4wNTQgNy43MTQtMTcuNDYyYzUuMTctNC40MDggMTIuMDM3LTYuNjEyIDIwLjc2OC02LjYxMmMyLjg4MiAwIDUuODQ5LjI1NCA4Ljk4NS42NzhjMy4xMzcuNDI0IDYuMzU4IDEuMTAyIDkuNzQ5IDEuODY1VjI5LjMzYzAtNi40NDMtMS4zNTctMTAuOTM1LTMuOTg1LTEzLjU2M2MtMi43MTItMi42MjgtNy4yOS0zLjktMTMuODE3LTMuOWMtMi45NjcgMC02LjAxOC4zNC05LjE1NSAxLjEwM3MtNi4xODggMS42OTUtOS4xNTUgMi44ODJjLTEuMzU2LjU5My0yLjM3My45MzItMi45NjcgMS4xMDJzLTEuMDE3LjI1NC0xLjM1Ni4yNTRjLTEuMTg3IDAtMS43OC0uODQ4LTEuNzgtMi42Mjh2LTQuMTU0YzAtMS4zNTYuMTctMi4zNzMuNTkzLTIuOTY2Yy40MjQtLjU5NCAxLjE4Ny0xLjE4NyAyLjM3NC0xLjc4cTQuNDUtMi4yOSAxMC42OC0zLjgxNUMzMy45MDguNzYzIDM4LjMxNi4yNTUgNDIuOTc4LjI1NWMxMC4wODggMCAxNy40NjMgMi4yODggMjIuMjEgNi44NjZjNC42NjIgNC41NzcgNy4wMzYgMTEuNTI4IDcuMDM2IDIwLjg1M3YyNy40NjR6TTM3Ljk3NiA2OC4zMjNjMi43OTggMCA1LjY4LS41MDggOC43MzEtMS41MjZjMy4wNTItMS4wMTcgNS43NjUtMi44ODIgOC4wNTMtNS40MjVjMS4zNTctMS42MSAyLjM3NC0zLjM5IDIuODgyLTUuNDI1Yy41MDktMi4wMzQuODQ4LTQuNDkzLjg0OC03LjM3NXYtMy41NmE3MSA3MSAwIDAgMC03Ljc5OS0xLjQ0MWE2NCA2NCAwIDAgMC03Ljk2OC0uNTA5Yy01LjY4IDAtOS44MzMgMS4xMDItMTIuNjMgMy4zOTFzLTQuMTU0IDUuNTEtNC4xNTQgOS43NDhjMCAzLjk4NCAxLjAxNyA2Ljk1MSAzLjEzNiA4Ljk4NmMyLjAzNSAyLjExOSA1LjAwMiAzLjEzNiA4LjkwMSAzLjEzNm02OC4wNjkgOS4xNTVjLTEuNTI2IDAtMi41NDMtLjI1NC0zLjIyMS0uODQ4Yy0uNjc4LS41MDgtMS4yNzItMS42OTUtMS43OC0zLjMwNUw4MS4xMjQgNy43OTljLS41MS0xLjY5Ni0uNzY0LTIuNzk4LS43NjQtMy4zOTFjMC0xLjM1Ni42NzgtMi4xMiAyLjAzNS0yLjEyaDguMzA3YzEuNjEgMCAyLjcxMy4yNTUgMy4zMDYuODQ4Yy42NzguNTA5IDEuMTg3IDEuNjk2IDEuNjk1IDMuMzA2bDE0LjI0MSA1Ni4xMTdsMTMuMjI0LTU2LjExN2MuNDI0LTEuNjk1LjkzMy0yLjc5NyAxLjYxLTMuMzA2Yy42NzktLjUwOCAxLjg2Ni0uODQ3IDMuMzkyLS44NDdoNi43ODFjMS42MSAwIDIuNzEzLjI1NCAzLjM5Ljg0N2MuNjc5LjUwOSAxLjI3MiAxLjY5NiAxLjYxMSAzLjMwNmwxMy4zOTQgNTYuNzk1TDE2OC4wMSA2LjQ0MmMuNTA4LTEuNjk1IDEuMTAyLTIuNzk3IDEuNjk1LTMuMzA2Yy42NzgtLjUwOCAxLjc4LS44NDcgMy4zMDYtLjg0N2g3Ljg4M2MxLjM1NyAwIDIuMTIuNjc4IDIuMTIgMi4xMTljMCAuNDI0LS4wODUuODQ4LS4xNyAxLjM1NnMtLjI1NCAxLjE4Ny0uNTkzIDIuMTJsLTIwLjQzIDY1LjUyNXEtLjc2MiAyLjU0NC0xLjc4IDMuMzA2Yy0uNjc4LjUwOS0xLjc4Ljg0OC0zLjIyLjg0OGgtNy4yOWMtMS42MTEgMC0yLjcxMy0uMjU0LTMuMzkyLS44NDhjLS42NzgtLjU5My0xLjI3MS0xLjY5NS0xLjYxLTMuMzlsLTEzLjE0LTU0LjY3NmwtMTMuMDU0IDU0LjU5Yy0uNDIzIDEuNjk2LS45MzIgMi43OTgtMS42MSAzLjM5MWMtLjY3OC41OTQtMS44NjUuODQ4LTMuMzkuODQ4em0xMDguOTI3IDIuMjg5Yy00LjQwOCAwLTguODE2LS41MDktMTMuMDU0LTEuNTI2Yy00LjIzOS0xLjAxNy03LjU0NC0yLjEyLTkuNzQ4LTMuMzljLTEuMzU3LS43NjQtMi4yOS0xLjYxMS0yLjYyOC0yLjM3NGE2IDYgMCAwIDEtLjUwOS0yLjM3NFY2NS43OGMwLTEuNzguNjc4LTIuNjI4IDEuOTUtMi42MjhhNC44IDQuOCAwIDAgMSAxLjUyNi4yNTVjLjUwOC4xNyAxLjI3MS41MDggMi4xMTkuODQ3YTQ2IDQ2IDAgMCAwIDkuMzI0IDIuOTY3YTUxIDUxIDAgMCAwIDEwLjA4OCAxLjAxN2M1LjM0IDAgOS40OTQtLjkzMiAxMi4zNzYtMi43OTdzNC40MDgtNC41NzcgNC40MDgtOC4wNTNjMC0yLjM3My0uNzYzLTQuMzIzLTIuMjg5LTUuOTM0cy00LjQwOC0zLjA1MS04LjU2MS00LjQwOGwtMTIuMjkyLTMuODE0Yy02LjE4OC0xLjk1LTEwLjc2NS00LjgzMi0xMy41NjMtOC42NDdjLTIuNzk3LTMuNzMtNC4yMzgtNy44ODMtNC4yMzgtMTIuMjkxcTAtNS4zNCAyLjI4OS05LjQxYzEuNTI1LTIuNzEyIDMuNTYtNS4wODUgNi4xMDMtNi45NWMyLjU0My0xLjk1IDUuNDI1LTMuMzkxIDguODE2LTQuNDA4YzMuMzktMS4wMTcgNi45NS0xLjQ0MSAxMC42OC0xLjQ0MWMxLjg2NSAwIDMuODE1LjA4NSA1LjY4LjMzOWMxLjk1LjI1NCAzLjczLjU5MyA1LjUxLjkzMmMxLjY5NS40MjQgMy4zMDYuODQ4IDQuODMyIDEuMzU3cTIuMjg4Ljc2MiAzLjU2IDEuNTI1YzEuMTg3LjY3OSAyLjAzNCAxLjM1NyAyLjU0MyAyLjEycS43NjMgMS4wMTcuNzYzIDIuNzk3djMuOTg0YzAgMS43OC0uNjc4IDIuNzEzLTEuOTUgMi43MTNjLS42NzggMC0xLjc4LS4zNC0zLjIyLTEuMDE4cS03LjI1LTMuMzA2LTE2LjI3Ni0zLjMwNmMtNC44MzIgMC04LjY0Ny43NjMtMTEuMjc1IDIuMzc0Yy0yLjYyNyAxLjYxLTMuOTg0IDQuMDY5LTMuOTg0IDcuNTQ0YzAgMi4zNzQuODQ4IDQuNDA4IDIuNTQzIDYuMDE5czQuODMyIDMuMjIxIDkuMzI1IDQuNjYybDEyLjAzNyAzLjgxNWM2LjEwMyAxLjk1IDEwLjUxMSA0LjY2MiAxMy4xMzkgOC4xMzdzMy45IDcuNDYgMy45IDExLjg2OGMwIDMuNjQ1LS43NjQgNi45NTEtMi4yMDUgOS44MzNjLTEuNTI1IDIuODgyLTMuNTYgNS40MjUtNi4xODggNy40NmMtMi42MjggMi4xMTktNS43NjQgMy42NDUtOS40MDkgNC43NDdjLTMuODE1IDEuMTg3LTcuNzk5IDEuNzgtMTIuMTIyIDEuNzgiLz48cGF0aCBmaWxsPSIjRjkwIiBkPSJNMjMwLjk5MyAxMjAuOTY0Yy0yNy44ODggMjAuNTk5LTY4LjQwOCAzMS41MzQtMTAzLjI0NyAzMS41MzRjLTQ4LjgyNyAwLTkyLjgyMS0xOC4wNTYtMTI2LjA1LTQ4LjA2NGMtMi42MjgtMi4zNzMtLjI1NS01LjU5NCAyLjg4MS0zLjczYzM1Ljk0MiAyMC44NTQgODAuMjc2IDMzLjQ4NCAxMjYuMTM2IDMzLjQ4NGMzMC45NCAwIDY0LjkzMi02LjQ0MiA5Ni4yMTItMTkuNjY2YzQuNjYyLTIuMTIgOC42NDYgMy4wNTIgNC4wNjggNi40NDJtMTEuNjE0LTEzLjIyNGMtMy41Ni00LjU3Ny0yMy41NjYtMi4yMDQtMzIuNjM2LTEuMTAyYy0yLjcxMy4zNC0zLjEzNy0yLjAzNC0uNjc4LTMuODE0YzE1LjkzNi0xMS4xOSA0Mi4xMy03Ljk2OCA0NS4xODEtNC4yMzljMy4wNTIgMy44MTUtLjg0OCAzMC4wMDgtMTUuNzY3IDQyLjU1NGMtMi4yODggMS45NS00LjQ5Mi45MzMtMy40NzUtMS42MWMzLjM5LTguMzkzIDEwLjkzNS0yNy4yOTYgNy4zNzUtMzEuNzg5Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS AI & Machine Learning Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            sagemaker_notebook_instance_name = st.text_input("SageMaker Notebook Instance Name", "my-notebook")
            instance_type = st.text_input("Instance Type", "ml.t2.medium")
            additional_input = f"Stack Name: {stack_name}\nSageMaker Notebook Instance Name: {sagemaker_notebook_instance_name}\nInstance Type: {instance_type}"
        elif service == "Monitoring":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjY4ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDE1MyI+PHBhdGggZmlsbD0iIzI1MkYzRSIgZD0iTTcyLjM5MiA1NS40MzhjMCAzLjEzNy4zNCA1LjY4LjkzMyA3LjU0NWE0NS40IDQ1LjQgMCAwIDAgMi43MTIgNi4xMDNjLjQyNC42NzguNTkzIDEuMzU2LjU5MyAxLjk1YzAgLjg0Ny0uNTA4IDEuNjk1LTEuNjEgMi41NDNsLTUuMzQgMy41NmMtLjc2My41MDktMS41MjYuNzYzLTIuMjA1Ljc2M2MtLjg0NyAwLTEuNjk1LS40MjQtMi41NDMtMS4xODdhMjYgMjYgMCAwIDEtMy4wNTEtMy45ODRjLS44NDgtMS40NC0xLjY5Ni0zLjA1Mi0yLjYyOC01LjAwMXEtOS45MTkgMTEuNjk3LTI0LjkyMiAxMS42OThjLTcuMTIgMC0xMi44LTIuMDM1LTE2Ljk1NC02LjEwM2MtNC4xNTMtNC4wNy02LjI3Mi05LjQ5NS02LjI3Mi0xNi4yNzZjMC03LjIwNSAyLjU0My0xMy4wNTQgNy43MTQtMTcuNDYyYzUuMTctNC40MDggMTIuMDM3LTYuNjEyIDIwLjc2OC02LjYxMmMyLjg4MiAwIDUuODQ5LjI1NCA4Ljk4NS42NzhjMy4xMzcuNDI0IDYuMzU4IDEuMTAyIDkuNzQ5IDEuODY1VjI5LjMzYzAtNi40NDMtMS4zNTctMTAuOTM1LTMuOTg1LTEzLjU2M2MtMi43MTItMi42MjgtNy4yOS0zLjktMTMuODE3LTMuOWMtMi45NjcgMC02LjAxOC4zNC05LjE1NSAxLjEwM3MtNi4xODggMS42OTUtOS4xNTUgMi44ODJjLTEuMzU2LjU5My0yLjM3My45MzItMi45NjcgMS4xMDJzLTEuMDE3LjI1NC0xLjM1Ni4yNTRjLTEuMTg3IDAtMS43OC0uODQ4LTEuNzgtMi42Mjh2LTQuMTU0YzAtMS4zNTYuMTctMi4zNzMuNTkzLTIuOTY2Yy40MjQtLjU5NCAxLjE4Ny0xLjE4NyAyLjM3NC0xLjc4cTQuNDUtMi4yOSAxMC42OC0zLjgxNUMzMy45MDguNzYzIDM4LjMxNi4yNTUgNDIuOTc4LjI1NWMxMC4wODggMCAxNy40NjMgMi4yODggMjIuMjEgNi44NjZjNC42NjIgNC41NzcgNy4wMzYgMTEuNTI4IDcuMDM2IDIwLjg1M3YyNy40NjR6TTM3Ljk3NiA2OC4zMjNjMi43OTggMCA1LjY4LS41MDggOC43MzEtMS41MjZjMy4wNTItMS4wMTcgNS43NjUtMi44ODIgOC4wNTMtNS40MjVjMS4zNTctMS42MSAyLjM3NC0zLjM5IDIuODgyLTUuNDI1Yy41MDktMi4wMzQuODQ4LTQuNDkzLjg0OC03LjM3NXYtMy41NmE3MSA3MSAwIDAgMC03Ljc5OS0xLjQ0MWE2NCA2NCAwIDAgMC03Ljk2OC0uNTA5Yy01LjY4IDAtOS44MzMgMS4xMDItMTIuNjMgMy4zOTFzLTQuMTU0IDUuNTEtNC4xNTQgOS43NDhjMCAzLjk4NCAxLjAxNyA2Ljk1MSAzLjEzNiA4Ljk4NmMyLjAzNSAyLjExOSA1LjAwMiAzLjEzNiA4LjkwMSAzLjEzNm02OC4wNjkgOS4xNTVjLTEuNTI2IDAtMi41NDMtLjI1NC0zLjIyMS0uODQ4Yy0uNjc4LS41MDgtMS4yNzItMS42OTUtMS43OC0zLjMwNUw4MS4xMjQgNy43OTljLS41MS0xLjY5Ni0uNzY0LTIuNzk4LS43NjQtMy4zOTFjMC0xLjM1Ni42NzgtMi4xMiAyLjAzNS0yLjEyaDguMzA3YzEuNjEgMCAyLjcxMy4yNTUgMy4zMDYuODQ4Yy42NzguNTA5IDEuMTg3IDEuNjk2IDEuNjk1IDMuMzA2bDE0LjI0MSA1Ni4xMTdsMTMuMjI0LTU2LjExN2MuNDI0LTEuNjk1LjkzMy0yLjc5NyAxLjYxLTMuMzA2Yy42NzktLjUwOCAxLjg2Ni0uODQ3IDMuMzkyLS44NDdoNi43ODFjMS42MSAwIDIuNzEzLjI1NCAzLjM5Ljg0N2MuNjc5LjUwOSAxLjI3MiAxLjY5NiAxLjYxMSAzLjMwNmwxMy4zOTQgNTYuNzk1TDE2OC4wMSA2LjQ0MmMuNTA4LTEuNjk1IDEuMTAyLTIuNzk3IDEuNjk1LTMuMzA2Yy42NzgtLjUwOCAxLjc4LS44NDcgMy4zMDYtLjg0N2g3Ljg4M2MxLjM1NyAwIDIuMTIuNjc4IDIuMTIgMi4xMTljMCAuNDI0LS4wODUuODQ4LS4xNyAxLjM1NnMtLjI1NCAxLjE4Ny0uNTkzIDIuMTJsLTIwLjQzIDY1LjUyNXEtLjc2MiAyLjU0NC0xLjc4IDMuMzA2Yy0uNjc4LjUwOS0xLjc4Ljg0OC0zLjIyLjg0OGgtNy4yOWMtMS42MTEgMC0yLjcxMy0uMjU0LTMuMzkyLS44NDhjLS42NzgtLjU5My0xLjI3MS0xLjY5NS0xLjYxLTMuMzlsLTEzLjE0LTU0LjY3NmwtMTMuMDU0IDU0LjU5Yy0uNDIzIDEuNjk2LS45MzIgMi43OTgtMS42MSAzLjM5MWMtLjY3OC41OTQtMS44NjUuODQ4LTMuMzkuODQ4em0xMDguOTI3IDIuMjg5Yy00LjQwOCAwLTguODE2LS41MDktMTMuMDU0LTEuNTI2Yy00LjIzOS0xLjAxNy03LjU0NC0yLjEyLTkuNzQ4LTMuMzljLTEuMzU3LS43NjQtMi4yOS0xLjYxMS0yLjYyOC0yLjM3NGE2IDYgMCAwIDEtLjUwOS0yLjM3NFY2NS43OGMwLTEuNzguNjc4LTIuNjI4IDEuOTUtMi42MjhhNC44IDQuOCAwIDAgMSAxLjUyNi4yNTVjLjUwOC4xNyAxLjI3MS41MDggMi4xMTkuODQ3YTQ2IDQ2IDAgMCAwIDkuMzI0IDIuOTY3YTUxIDUxIDAgMCAwIDEwLjA4OCAxLjAxN2M1LjM0IDAgOS40OTQtLjkzMiAxMi4zNzYtMi43OTdzNC40MDgtNC41NzcgNC40MDgtOC4wNTNjMC0yLjM3My0uNzYzLTQuMzIzLTIuMjg5LTUuOTM0cy00LjQwOC0zLjA1MS04LjU2MS00LjQwOGwtMTIuMjkyLTMuODE0Yy02LjE4OC0xLjk1LTEwLjc2NS00LjgzMi0xMy41NjMtOC42NDdjLTIuNzk3LTMuNzMtNC4yMzgtNy44ODMtNC4yMzgtMTIuMjkxcTAtNS4zNCAyLjI4OS05LjQxYzEuNTI1LTIuNzEyIDMuNTYtNS4wODUgNi4xMDMtNi45NWMyLjU0My0xLjk1IDUuNDI1LTMuMzkxIDguODE2LTQuNDA4YzMuMzktMS4wMTcgNi45NS0xLjQ0MSAxMC42OC0xLjQ0MWMxLjg2NSAwIDMuODE1LjA4NSA1LjY4LjMzOWMxLjk1LjI1NCAzLjczLjU5MyA1LjUxLjkzMmMxLjY5NS40MjQgMy4zMDYuODQ4IDQuODMyIDEuMzU3cTIuMjg4Ljc2MiAzLjU2IDEuNTI1YzEuMTg3LjY3OSAyLjAzNCAxLjM1NyAyLjU0MyAyLjEycS43NjMgMS4wMTcuNzYzIDIuNzk3djMuOTg0YzAgMS43OC0uNjc4IDIuNzEzLTEuOTUgMi43MTNjLS42NzggMC0xLjc4LS4zNC0zLjIyLTEuMDE4cS03LjI1LTMuMzA2LTE2LjI3Ni0zLjMwNmMtNC44MzIgMC04LjY0Ny43NjMtMTEuMjc1IDIuMzc0Yy0yLjYyNyAxLjYxLTMuOTg0IDQuMDY5LTMuOTg0IDcuNTQ0YzAgMi4zNzQuODQ4IDQuNDA4IDIuNTQzIDYuMDE5czQuODMyIDMuMjIxIDkuMzI1IDQuNjYybDEyLjAzNyAzLjgxNWM2LjEwMyAxLjk1IDEwLjUxMSA0LjY2MiAxMy4xMzkgOC4xMzdzMy45IDcuNDYgMy45IDExLjg2OGMwIDMuNjQ1LS43NjQgNi45NTEtMi4yMDUgOS44MzNjLTEuNTI1IDIuODgyLTMuNTYgNS40MjUtNi4xODggNy40NmMtMi42MjggMi4xMTktNS43NjQgMy42NDUtOS40MDkgNC43NDdjLTMuODE1IDEuMTg3LTcuNzk5IDEuNzgtMTIuMTIyIDEuNzgiLz48cGF0aCBmaWxsPSIjRjkwIiBkPSJNMjMwLjk5MyAxMjAuOTY0Yy0yNy44ODggMjAuNTk5LTY4LjQwOCAzMS41MzQtMTAzLjI0NyAzMS41MzRjLTQ4LjgyNyAwLTkyLjgyMS0xOC4wNTYtMTI2LjA1LTQ4LjA2NGMtMi42MjgtMi4zNzMtLjI1NS01LjU5NCAyLjg4MS0zLjczYzM1Ljk0MiAyMC44NTQgODAuMjc2IDMzLjQ4NCAxMjYuMTM2IDMzLjQ4NGMzMC45NCAwIDY0LjkzMi02LjQ0MiA5Ni4yMTItMTkuNjY2YzQuNjYyLTIuMTIgOC42NDYgMy4wNTIgNC4wNjggNi40NDJtMTEuNjE0LTEzLjIyNGMtMy41Ni00LjU3Ny0yMy41NjYtMi4yMDQtMzIuNjM2LTEuMTAyYy0yLjcxMy4zNC0zLjEzNy0yLjAzNC0uNjc4LTMuODE0YzE1LjkzNi0xMS4xOSA0Mi4xMy03Ljk2OCA0NS4xODEtNC4yMzljMy4wNTIgMy44MTUtLjg0OCAzMC4wMDgtMTUuNzY3IDQyLjU1NGMtMi4yODggMS45NS00LjQ5Mi45MzMtMy40NzUtMS42MWMzLjM5LTguMzkzIDEwLjkzNS0yNy4yOTYgNy4zNzUtMzEuNzg5Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS Monitoring Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            cloudwatch_alarm_name = st.text_input("CloudWatch Alarm Name", "my-alarm")
            metric_name = st.text_input("Metric Name", "CPUUtilization")
            threshold = st.number_input("Threshold", 80)
            additional_input = f"Stack Name: {stack_name}\nCloudWatch Alarm Name: {cloudwatch_alarm_name}\nMetric Name: {metric_name}\nThreshold: {threshold}"
        elif service == "Security":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxLjY4ZW0iIGhlaWdodD0iMWVtIiB2aWV3Qm94PSIwIDAgMjU2IDE1MyI+PHBhdGggZmlsbD0iIzI1MkYzRSIgZD0iTTcyLjM5MiA1NS40MzhjMCAzLjEzNy4zNCA1LjY4LjkzMyA3LjU0NWE0NS40IDQ1LjQgMCAwIDAgMi43MTIgNi4xMDNjLjQyNC42NzguNTkzIDEuMzU2LjU5MyAxLjk1YzAgLjg0Ny0uNTA4IDEuNjk1LTEuNjEgMi41NDNsLTUuMzQgMy41NmMtLjc2My41MDktMS41MjYuNzYzLTIuMjA1Ljc2M2MtLjg0NyAwLTEuNjk1LS40MjQtMi41NDMtMS4xODdhMjYgMjYgMCAwIDEtMy4wNTEtMy45ODRjLS44NDgtMS40NC0xLjY5Ni0zLjA1Mi0yLjYyOC01LjAwMXEtOS45MTkgMTEuNjk3LTI0LjkyMiAxMS42OThjLTcuMTIgMC0xMi44LTIuMDM1LTE2Ljk1NC02LjEwM2MtNC4xNTMtNC4wNy02LjI3Mi05LjQ5NS02LjI3Mi0xNi4yNzZjMC03LjIwNSAyLjU0My0xMy4wNTQgNy43MTQtMTcuNDYyYzUuMTctNC40MDggMTIuMDM3LTYuNjEyIDIwLjc2OC02LjYxMmMyLjg4MiAwIDUuODQ5LjI1NCA4Ljk4NS42NzhjMy4xMzcuNDI0IDYuMzU4IDEuMTAyIDkuNzQ5IDEuODY1VjI5LjMzYzAtNi40NDMtMS4zNTctMTAuOTM1LTMuOTg1LTEzLjU2M2MtMi43MTItMi42MjgtNy4yOS0zLjktMTMuODE3LTMuOWMtMi45NjcgMC02LjAxOC4zNC05LjE1NSAxLjEwM3MtNi4xODggMS42OTUtOS4xNTUgMi44ODJjLTEuMzU2LjU5My0yLjM3My45MzItMi45NjcgMS4xMDJzLTEuMDE3LjI1NC0xLjM1Ni4yNTRjLTEuMTg3IDAtMS43OC0uODQ4LTEuNzgtMi42Mjh2LTQuMTU0YzAtMS4zNTYuMTctMi4zNzMuNTkzLTIuOTY2Yy40MjQtLjU5NCAxLjE4Ny0xLjE4NyAyLjM3NC0xLjc4cTQuNDUtMi4yOSAxMC42OC0zLjgxNUMzMy45MDguNzYzIDM4LjMxNi4yNTUgNDIuOTc4LjI1NWMxMC4wODggMCAxNy40NjMgMi4yODggMjIuMjEgNi44NjZjNC42NjIgNC41NzcgNy4wMzYgMTEuNTI4IDcuMDM2IDIwLjg1M3YyNy40NjR6TTM3Ljk3NiA2OC4zMjNjMi43OTggMCA1LjY4LS41MDggOC43MzEtMS41MjZjMy4wNTItMS4wMTcgNS43NjUtMi44ODIgOC4wNTMtNS40MjVjMS4zNTctMS42MSAyLjM3NC0zLjM5IDIuODgyLTUuNDI1Yy41MDktMi4wMzQuODQ4LTQuNDkzLjg0OC03LjM3NXYtMy41NmE3MSA3MSAwIDAgMC03Ljc5OS0xLjQ0MWE2NCA2NCAwIDAgMC03Ljk2OC0uNTA5Yy01LjY4IDAtOS44MzMgMS4xMDItMTIuNjMgMy4zOTFzLTQuMTU0IDUuNTEtNC4xNTQgOS43NDhjMCAzLjk4NCAxLjAxNyA2Ljk1MSAzLjEzNiA4Ljk4NmMyLjAzNSAyLjExOSA1LjAwMiAzLjEzNiA4LjkwMSAzLjEzNm02OC4wNjkgOS4xNTVjLTEuNTI2IDAtMi41NDMtLjI1NC0zLjIyMS0uODQ4Yy0uNjc4LS41MDgtMS4yNzItMS42OTUtMS43OC0zLjMwNUw4MS4xMjQgNy43OTljLS41MS0xLjY5Ni0uNzY0LTIuNzk4LS43NjQtMy4zOTFjMC0xLjM1Ni42NzgtMi4xMiAyLjAzNS0yLjEyaDguMzA3YzEuNjEgMCAyLjcxMy4yNTUgMy4zMDYuODQ4Yy42NzguNTA5IDEuMTg3IDEuNjk2IDEuNjk1IDMuMzA2bDE0LjI0MSA1Ni4xMTdsMTMuMjI0LTU2LjExN2MuNDI0LTEuNjk1LjkzMy0yLjc5NyAxLjYxLTMuMzA2Yy42NzktLjUwOCAxLjg2Ni0uODQ3IDMuMzkyLS44NDdoNi43ODFjMS42MSAwIDIuNzEzLjI1NCAzLjM5Ljg0N2MuNjc5LjUwOSAxLjI3MiAxLjY5NiAxLjYxMSAzLjMwNmwxMy4zOTQgNTYuNzk1TDE2OC4wMSA2LjQ0MmMuNTA4LTEuNjk1IDEuMTAyLTIuNzk3IDEuNjk1LTMuMzA2Yy42NzgtLjUwOCAxLjc4LS44NDcgMy4zMDYtLjg0N2g3Ljg4M2MxLjM1NyAwIDIuMTIuNjc4IDIuMTIgMi4xMTljMCAuNDI0LS4wODUuODQ4LS4xNyAxLjM1NnMtLjI1NCAxLjE4Ny0uNTkzIDIuMTJsLTIwLjQzIDY1LjUyNXEtLjc2MiAyLjU0NC0xLjc4IDMuMzA2Yy0uNjc4LjUwOS0xLjc4Ljg0OC0zLjIyLjg0OGgtNy4yOWMtMS42MTEgMC0yLjcxMy0uMjU0LTMuMzkyLS44NDhjLS42NzgtLjU5My0xLjI3MS0xLjY5NS0xLjYxLTMuMzlsLTEzLjE0LTU0LjY3NmwtMTMuMDU0IDU0LjU5Yy0uNDIzIDEuNjk2LS45MzIgMi43OTgtMS42MSAzLjM5MWMtLjY3OC41OTQtMS44NjUuODQ4LTMuMzkuODQ4em0xMDguOTI3IDIuMjg5Yy00LjQwOCAwLTguODE2LS41MDktMTMuMDU0LTEuNTI2Yy00LjIzOS0xLjAxNy03LjU0NC0yLjEyLTkuNzQ4LTMuMzljLTEuMzU3LS43NjQtMi4yOS0xLjYxMS0yLjYyOC0yLjM3NGE2IDYgMCAwIDEtLjUwOS0yLjM3NFY2NS43OGMwLTEuNzguNjc4LTIuNjI4IDEuOTUtMi42MjhhNC44IDQuOCAwIDAgMSAxLjUyNi4yNTVjLjUwOC4xNyAxLjI3MS41MDggMi4xMTkuODQ3YTQ2IDQ2IDAgMCAwIDkuMzI0IDIuOTY3YTUxIDUxIDAgMCAwIDEwLjA4OCAxLjAxN2M1LjM0IDAgOS40OTQtLjkzMiAxMi4zNzYtMi43OTdzNC40MDgtNC41NzcgNC40MDgtOC4wNTNjMC0yLjM3My0uNzYzLTQuMzIzLTIuMjg5LTUuOTM0cy00LjQwOC0zLjA1MS04LjU2MS00LjQwOGwtMTIuMjkyLTMuODE0Yy02LjE4OC0xLjk1LTEwLjc2NS00LjgzMi0xMy41NjMtOC42NDdjLTIuNzk3LTMuNzMtNC4yMzgtNy44ODMtNC4yMzgtMTIuMjkxcTAtNS4zNCAyLjI4OS05LjQxYzEuNTI1LTIuNzEyIDMuNTYtNS4wODUgNi4xMDMtNi45NWMyLjU0My0xLjk1IDUuNDI1LTMuMzkxIDguODE2LTQuNDA4YzMuMzktMS4wMTcgNi45NS0xLjQ0MSAxMC42OC0xLjQ0MWMxLjg2NSAwIDMuODE1LjA4NSA1LjY4LjMzOWMxLjk1LjI1NCAzLjczLjU5MyA1LjUxLjkzMmMxLjY5NS40MjQgMy4zMDYuODQ4IDQuODMyIDEuMzU3cTIuMjg4Ljc2MiAzLjU2IDEuNTI1YzEuMTg3LjY3OSAyLjAzNCAxLjM1NyAyLjU0MyAyLjEycS43NjMgMS4wMTcuNzYzIDIuNzk3djMuOTg0YzAgMS43OC0uNjc4IDIuNzEzLTEuOTUgMi43MTNjLS42NzggMC0xLjc4LS4zNC0zLjIyLTEuMDE4cS03LjI1LTMuMzA2LTE2LjI3Ni0zLjMwNmMtNC44MzIgMC04LjY0Ny43NjMtMTEuMjc1IDIuMzc0Yy0yLjYyNyAxLjYxLTMuOTg0IDQuMDY5LTMuOTg0IDcuNTQ0YzAgMi4zNzQuODQ4IDQuNDA4IDIuNTQzIDYuMDE5czQuODMyIDMuMjIxIDkuMzI1IDQuNjYybDEyLjAzNyAzLjgxNWM2LjEwMyAxLjk1IDEwLjUxMSA0LjY2MiAxMy4xMzkgOC4xMzdzMy45IDcuNDYgMy45IDExLjg2OGMwIDMuNjQ1LS43NjQgNi45NTEtMi4yMDUgOS44MzNjLTEuNTI1IDIuODgyLTMuNTYgNS40MjUtNi4xODggNy40NmMtMi42MjggMi4xMTktNS43NjQgMy42NDUtOS40MDkgNC43NDdjLTMuODE1IDEuMTg3LTcuNzk5IDEuNzgtMTIuMTIyIDEuNzgiLz48cGF0aCBmaWxsPSIjRjkwIiBkPSJNMjMwLjk5MyAxMjAuOTY0Yy0yNy44ODggMjAuNTk5LTY4LjQwOCAzMS41MzQtMTAzLjI0NyAzMS41MzRjLTQ4LjgyNyAwLTkyLjgyMS0xOC4wNTYtMTI2LjA1LTQ4LjA2NGMtMi42MjgtMi4zNzMtLjI1NS01LjU5NCAyLjg4MS0zLjczYzM1Ljk0MiAyMC44NTQgODAuMjc2IDMzLjQ4NCAxMjYuMTM2IDMzLjQ4NGMzMC45NCAwIDY0LjkzMi02LjQ0MiA5Ni4yMTItMTkuNjY2YzQuNjYyLTIuMTIgOC42NDYgMy4wNTIgNC4wNjggNi40NDJtMTEuNjE0LTEzLjIyNGMtMy41Ni00LjU3Ny0yMy41NjYtMi4yMDQtMzIuNjM2LTEuMTAyYy0yLjcxMy4zNC0zLjEzNy0yLjAzNC0uNjc4LTMuODE0YzE1LjkzNi0xMS4xOSA0Mi4xMy03Ljk2OCA0NS4xODEtNC4yMzljMy4wNTIgMy44MTUtLjg0OCAzMC4wMDgtMTUuNzY3IDQyLjU1NGMtMi4yODggMS45NS00LjQ5Mi45MzMtMy40NzUtMS42MWMzLjM5LTguMzkzIDEwLjkzNS0yNy4yOTYgNy4zNzUtMzEuNzg5Ii8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">AWS Security Configuration</h3></div>""", unsafe_allow_html=True)
            stack_name = st.text_input("Stack Name", "my-stack")
            kms_key_id = st.text_input("KMS Key ID", "my-kms-key")
            security_policy_name = st.text_input("Security Policy Name", "my-security-policy")
            additional_input = f"Stack Name: {stack_name}\nKMS Key ID: {kms_key_id}\nSecurity Policy Name: {security_policy_name}"

        # Add more services as needed

    # Add GCP Configuration options           
    elif feature == "GCP Configuration":
        service = st.selectbox(
            "Select GCP Service",
            [
                "Select Service",
                "Compute Engine",
                "Cloud Run",
                "Kubernetes Engine (GKE)",
                "Cloud Functions",
                "App Engine",
                "VPC Network",
                "Cloud Load Balancing",
                "Cloud Storage",
                "Cloud SQL",
                "Spanner",
                "Firestore",
                "Bigtable",
                "BigQuery",
                "Pub/Sub",
                "Artifact Registry",
                "Cloud Build",
                "Secret Manager",
                "IAM",
                "Vertex AI",
                "Cloud Monitoring"
            ]
        )
        
        if service == "Compute Engine":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiNhZWNiZmE7fS5jbHMtMntmaWxsOiM2NjlkZjY7fS5jbHMtM3tmaWxsOiM0Mjg1ZjQ7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfQ29tcHV0ZUVuZ2luZV9Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48cmVjdCBjbGFzcz0iY2xzLTEiIHg9IjkiIHk9IjkiIHdpZHRoPSI2IiBoZWlnaHQ9IjYiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjExIiB5PSIyIiB3aWR0aD0iMiIgaGVpZ2h0PSI0Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSI3IiB5PSIyIiB3aWR0aD0iMiIgaGVpZ2h0PSI0Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIxNSIgeT0iMiIgd2lkdGg9IjIiIGhlaWdodD0iNCIvPjxyZWN0IGNsYXNzPSJjbHMtMyIgeD0iMTEiIHk9IjE4IiB3aWR0aD0iMiIgaGVpZ2h0PSI0Ii8+PHJlY3QgY2xhc3M9ImNscy0zIiB4PSI3IiB5PSIxOCIgd2lkdGg9IjIiIGhlaWdodD0iNCIvPjxyZWN0IGNsYXNzPSJjbHMtMyIgeD0iMTUiIHk9IjE4IiB3aWR0aD0iMiIgaGVpZ2h0PSI0Ii8+PHJlY3QgY2xhc3M9ImNscy0zIiB4PSIxOSIgeT0iMTAiIHdpZHRoPSIyIiBoZWlnaHQ9IjQiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDggMzIpIHJvdGF0ZSgtOTApIi8+PHJlY3QgY2xhc3M9ImNscy0zIiB4PSIxOSIgeT0iMTQiIHdpZHRoPSIyIiBoZWlnaHQ9IjQiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDQgMzYpIHJvdGF0ZSgtOTApIi8+PHJlY3QgY2xhc3M9ImNscy0zIiB4PSIxOSIgeT0iNiIgd2lkdGg9IjIiIGhlaWdodD0iNCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTIgMjgpIHJvdGF0ZSgtOTApIi8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIzIiB5PSIxMCIgd2lkdGg9IjIiIGhlaWdodD0iNCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTggMTYpIHJvdGF0ZSgtOTApIi8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIzIiB5PSIxNCIgd2lkdGg9IjIiIGhlaWdodD0iNCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTEyIDIwKSByb3RhdGUoLTkwKSIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iMyIgeT0iNiIgd2lkdGg9IjIiIGhlaWdodD0iNCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTQgMTIpIHJvdGF0ZSgtOTApIi8+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNSw1VjE5SDE5VjVaTTE3LDE3SDdWN0gxN1oiLz48cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iOSAxNSAxNSAxNSAxMiAxMiA5IDE1Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjEyIDEyIDE1IDE1IDE1IDkgMTIgMTIiLz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Compute Engine Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            instance_name = st.text_input("Instance Name", "my-vm-instance")
            zone = st.selectbox("Zone", ["us-central1-a", "us-central1-b", "us-central1-c", "us-east1-b", "us-east1-c", "us-east1-d", "us-west1-a", "us-west1-b", "us-west1-c", "europe-west1-b", "europe-west1-c", "europe-west4-a", "europe-west4-b", "europe-west4-c", "asia-northeast1-a", "asia-northeast1-b", "asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"])
            
            # Intuitive T-Shirt Sizing
            t_shirt_map = {"Small (e2-micro)": "e2-micro", "Medium (e2-small)": "e2-small", "Large (e2-medium)": "e2-medium", "X-Large (n1-standard-1)": "n1-standard-1"}
            size_choice = st.selectbox("Instance Size (T-Shirt)", list(t_shirt_map.keys()), index=2)
            machine_type = t_shirt_map[size_choice]
            
            image = st.selectbox("Source Image", ["debian-11", "ubuntu-2204-lts", "rhel-9", "windows-server-2022-dc"])
            instance_count = st.number_input(
                "Number of Instances",
                min_value=1, max_value=10, value=1, step=1,
                help="Provision N identical VMs in parallel via GitHub Actions matrix strategy (1–10)"
            )
            st.session_state["vm_instance_count"] = int(instance_count)
            additional_input = f"Project ID: {project_id}\nInstance Name: {instance_name}\nZone: {zone}\nMachine Type: {machine_type}\nSource Image: {image}\nNumber of Instances: {instance_count}"

            
        elif service == "Cloud Run":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiNhZWNiZmE7fS5jbHMtMSwuY2xzLTJ7ZmlsbC1ydWxlOmV2ZW5vZGQ7fS5jbHMtMntmaWxsOiM0Mjg1ZjQ7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfQ2xvdWRSdW5fQ29sb3I8L3RpdGxlPjxnIGRhdGEtbmFtZT0iUHJvZHVjdCBJY29ucyI+PGcgPjxwb2x5Z29uIGNsYXNzPSJjbHMtMSIgcG9pbnRzPSI4LjkgMi42MyAxMi4wMiAxMiAyMS4zOCAxMiA4LjkgMi42MyIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSIyMS4zOCAxMiAxMi4wMiAxMiA4LjkgMjEuMzggMjEuMzggMTIiLz48cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMy40NCAyMS4zOCA2LjU3IDE5LjgxIDguOSAxMiA1Ljc4IDEyIDMuNDQgMjEuMzgiLz48cG9seWdvbiBjbGFzcz0iY2xzLTEiIHBvaW50cz0iMy40NCAyLjYzIDUuNzggMTIgOC45IDEyIDYuNTcgNC4xOSAzLjQ0IDIuNjMiLz48L2c+PC9nPjwvc3ZnPg==\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud Run Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            service_name = st.text_input("Service Name", "my-cloud-run-service")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            image = st.selectbox("Container Image URL", ["gcr.io/google-samples/hello-app:1.0", "nginx", "alpine", "node:18-alpine", "python:3.11-slim"])
            
            # Intuitive T-Shirt Sizing for Memory
            t_shirt_map = {"Small (256Mi)": "256Mi", "Medium (512Mi)": "512Mi", "Large (1Gi)": "1Gi", "X-Large (2Gi)": "2Gi"}
            size_choice = st.selectbox("Memory Size (T-Shirt)", list(t_shirt_map.keys()), index=1)
            memory = t_shirt_map[size_choice]
            
            port = st.text_input("Container Port", "8080")
            auth = st.selectbox("Authentication", ["Allow unauthenticated invocations", "Require authentication"])
            additional_input = f"Project ID: {project_id}\nService Name: {service_name}\nRegion: {region}\nImage: {image}\nMemory: {memory}\nPort: {port}\nAuth: {auth}"

        elif service == "Kubernetes Engine (GKE)":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM0Mjg1ZjQ7fS5jbHMtMSwuY2xzLTIsLmNscy00e2ZpbGwtcnVsZTpldmVub2RkO30uY2xzLTJ7ZmlsbDojNjY5ZGY2O30uY2xzLTMsLmNscy00e2ZpbGw6I2FlY2JmYTt9PC9zdHlsZT48L2RlZnM+PHRpdGxlPkljb25fMjRweF9LOEVuZ2luZV9Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48ZyA+PHBvbHlnb24gY2xhc3M9ImNscy0xIiBwb2ludHM9IjE0LjY4IDEzLjA2IDE5LjIzIDE1LjY5IDE5LjIzIDE2LjY4IDE0LjI5IDEzLjgzIDE0LjY4IDEzLjA2Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjkuOTggMTMuNjUgNC43NyAxNi42NiA0LjQ1IDE1Ljg2IDkuNTMgMTIuOTIgOS45OCAxMy42NSIvPjxyZWN0IGNsYXNzPSJjbHMtMyIgeD0iMTEuNTUiIHk9IjMuMjkiIHdpZHRoPSIwLjg2IiBoZWlnaHQ9IjUuNzgiLz48cGF0aCBjbGFzcz0iY2xzLTQiIGQ9Ik0zLjI1LDdWMTdMMTIsMjJsOC43NC01VjdMMTIsMlptMTUuNjMsOC44OUwxMiwxOS43OCw1LjEyLDE1Ljg5VjguMTFMMTIsNC4yMmw2Ljg3LDMuODl2Ny43OFoiLz48cG9seWdvbiBjbGFzcz0iY2xzLTQiIHBvaW50cz0iMTEuOTggMTEuNSAxNS45NiA5LjIxIDExLjk4IDYuOTEgOC4wMSA5LjIxIDExLjk4IDExLjUiLz48cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMTEuNTIgMTIuMyA3LjY2IDEwLjAxIDcuNjYgMTQuNiAxMS41MiAxNi44OSAxMS41MiAxMi4zIi8+PHBvbHlnb24gY2xhc3M9ImNscy0xIiBwb2ludHM9IjEyLjQ4IDEyLjMgMTIuNDggMTYuODkgMTYuMzQgMTQuNiAxNi4zNCAxMC4wMSAxMi40OCAxMi4zIi8+PC9nPjwvZz48L3N2Zz4=\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">GKE Cluster Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            cluster_name = st.text_input("Cluster Name", "my-gke-cluster")
            zone = st.selectbox("Zone/Region", ["us-central1-a", "us-central1-b", "us-central1-c", "us-east1-b", "us-east1-c", "us-east1-d", "us-west1-a", "us-west1-b", "us-west1-c", "europe-west1-b", "europe-west1-c", "europe-west4-a", "europe-west4-b", "europe-west4-c", "asia-northeast1-a", "asia-northeast1-b", "asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"])
            node_count = st.number_input("Number of Nodes", min_value=1, value=3)
            
            # Intuitive T-Shirt Sizing
            t_shirt_map = {"Small (e2-micro)": "e2-micro", "Medium (e2-small)": "e2-small", "Large (e2-medium)": "e2-medium", "X-Large (n1-standard-1)": "n1-standard-1"}
            size_choice = st.selectbox("Node Size (T-Shirt)", list(t_shirt_map.keys()), index=2)
            machine_type = t_shirt_map[size_choice]
            
            additional_input = f"Project ID: {project_id}\nCluster Name: {cluster_name}\nZone/Region: {zone}\nNode Count: {node_count}\nMachine Type: {machine_type}"

        elif service == "Cloud Functions":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM2NjlkZjY7fS5jbHMtMntmaWxsOiM0Mjg1ZjQ7fS5jbHMtM3tmaWxsOiNhZWNiZmE7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfRnVuY3Rpb25zX0NvbG9yPC90aXRsZT48ZyBkYXRhLW5hbWU9IlByb2R1Y3QgSWNvbnMiPjxnIGRhdGEtbmFtZT0iY29sb3JlZC0zMi9mdW5jdGlvbnMiPjxnID48cG9seWdvbiBjbGFzcz0iY2xzLTEiIHBvaW50cz0iMiAxNS41NiA1IDE4IDUgNiAyIDguNDMgMiAxNS41NiIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSIyIDEwIDUgOCA1IDYgMiAxMCIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSI1IDE4IDUgMTYgMiAxNCA1IDE4Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjggMjAgMiAxNCAyIDE4IDYgMjIgOCAyMCIvPjwvZz48L2c+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjUuOTkgMi4wMSAyIDYgMi4wMSAxMCA3Ljk5IDQuMDEgNS45OSAyLjAxIi8+PGcgZGF0YS1uYW1lPSJjb2xvcmVkLTMyL2Z1bmN0aW9ucyI+PGcgZGF0YS1uYW1lPSJTaGFwZSI+PHBvbHlnb24gY2xhc3M9ImNscy0xIiBwb2ludHM9IjIyIDguNDUgMTkgNi4wMSAxOSAxOC4wMSAyMiAxNS41OSAyMiA4LjQ1Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjIyIDE0LjAxIDE5IDE2LjAxIDE5IDE4LjAxIDIyIDE0LjAxIi8+PHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjE5IDYuMDEgMTkgOC4wMSAyMiAxMC4wMSAxOSA2LjAxIi8+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjE2IDQuMDEgMjIgMTAuMDEgMjIgNi4wMSAxOCAyLjAxIDE2IDQuMDEiLz48L2c+PC9nPjxwb2x5Z29uIGNsYXNzPSJjbHMtMyIgcG9pbnRzPSIxOC4wMSAyMiAyMiAxOC4wMSAyMS45OSAxNC4wMSAxNi4wMSAyMCAxOC4wMSAyMiIvPjxjaXJjbGUgaWQ9Ik92YWwiIGNsYXNzPSJjbHMtMyIgY3g9IjgiIGN5PSIxMiIgcj0iMSIvPjxjaXJjbGUgaWQ9Ik92YWwtMiIgZGF0YS1uYW1lPSJPdmFsIiBjbGFzcz0iY2xzLTMiIGN4PSIxMiIgY3k9IjEyIiByPSIxIi8+PGNpcmNsZSBpZD0iT3ZhbC0zIiBkYXRhLW5hbWU9Ik92YWwiIGNsYXNzPSJjbHMtMyIgY3g9IjE1Ljk5IiBjeT0iMTIiIHI9IjEiLz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud Functions Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            function_name = st.text_input("Function Name", "my-function")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            
            # Intuitive T-Shirt Sizing for Memory
            t_shirt_map = {"Small (128MB)": "128MB", "Medium (256MB)": "256MB", "Large (512MB)": "512MB", "X-Large (1024MB)": "1024MB"}
            size_choice = st.selectbox("Memory Size (T-Shirt)", list(t_shirt_map.keys()), index=1)
            memory = t_shirt_map[size_choice]
            
            runtime = st.selectbox("Runtime", ["nodejs20", "python311", "go121", "java17"])
            trigger = st.selectbox("Trigger", ["HTTP", "Pub/Sub", "Cloud Storage"])
            additional_input = f"Project ID: {project_id}\nFunction Name: {function_name}\nRegion: {region}\nMemory: {memory}\nRuntime: {runtime}\nTrigger: {trigger}"

        elif service == "App Engine":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM0Mjg1ZjQ7fS5jbHMtMSwuY2xzLTIsLmNscy0ze2ZpbGwtcnVsZTpldmVub2RkO30uY2xzLTJ7ZmlsbDojYWVjYmZhO30uY2xzLTN7ZmlsbDojNjY5ZGY2O308L3N0eWxlPjwvZGVmcz48dGl0bGU+SWNvbl8yNHB4X0FwcEVuZ2luZV9Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48ZyA+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMTQuMywxMGwtMS4yMiwxLjIyQTEuNzEsMS43MSwwLDAsMSwxMiwxNC4yM2ExLjc0LDEuNzQsMCwwLDEtMS4zMy0uNjRMOS40NSwxNC44MUEzLjQzLDMuNDMsMCwxLDAsMTQuMywxMFoiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik0xMiw2LjI2YTYuMjUsNi4yNSwwLDEsMCw2LjI1LDYuMjVBNi4yNSw2LjI1LDAsMCwwLDEyLDYuMjZNMTIsMTdhNC40NSw0LjQ1LDAsMSwxLDQuNDQtNC40NEE0LjQ0LDQuNDQsMCwwLDEsMTIsMTciLz48cGF0aCBjbGFzcz0iY2xzLTMiIGQ9Ik0yMS42MiwxMS45bC0yLjU2LS44MWE3LjEsNy4xLDAsMCwxLC4xNywxLjUzLDcuNjIsNy42MiwwLDAsMS0uMDgsMS4wOGgyLjQ3YS40NC40NCwwLDAsMCwuMzgtLjQydi0xYS40NC40NCwwLDAsMC0uMzgtLjQyIi8+PHBhdGggY2xhc3M9ImNscy0zIiBkPSJNMTIsNS41MmE3LjQ4LDcuNDgsMCwwLDEsMS41LjE1bC0uOTItMi41NWMtLjA3LS4yMi0uMjEtLjM4LS40Mi0uMzhoLS4zOGEuNDUuNDUsMCwwLDAtLjQyLjM4bC0uOCwyLjU0QTcuNjQsNy42NCwwLDAsMSwxMiw1LjUyIi8+PHBhdGggY2xhc3M9ImNscy0zIiBkPSJNNC43NywxMi42MmE3LjEsNy4xLDAsMCwxLC4xNy0xLjUzbC0yLjU2LjgxYS40NC40NCwwLDAsMC0uMzguNDJ2MWEuNDQuNDQsMCwwLDAsLjM4LjQySDQuODVhNy42Miw3LjYyLDAsMCwxLS4wOC0xLjA4Ii8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNMTIsMTBhMi41LDIuNSwwLDEsMCwyLjUsMi41QTIuNSwyLjUsMCwwLDAsMTIsMTBabTAsMy43NWExLjI1LDEuMjUsMCwxLDEsMS4yNS0xLjI1QTEuMjUsMS4yNSwwLDAsMSwxMiwxMy43NloiLz48L2c+PC9nPjwvc3ZnPg==\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">App Engine Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            
            # Intuitive T-Shirt Sizing for Instance Class
            t_shirt_map = {"Small (F1)": "F1", "Medium (F2)": "F2", "Large (F4)": "F4"}
            size_choice = st.selectbox("Instance Size (T-Shirt)", list(t_shirt_map.keys()), index=0)
            instance_class = t_shirt_map[size_choice]
            
            env = st.selectbox("Environment", ["Standard", "Flexible"])
            additional_input = f"Project ID: {project_id}\nRegion: {region}\nInstance Class: {instance_class}\nEnvironment: {env}"

        elif service == "VPC Network":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiNhZWNiZmE7fS5jbHMtMntmaWxsOiM2NjlkZjY7fS5jbHMtM3tmaWxsOiM0Mjg1ZjQ7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfVmlydHVhbFByaXZhdGVDbG91ZF9Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48cmVjdCBjbGFzcz0iY2xzLTEiIHg9IjE2IiB5PSIyIiB3aWR0aD0iNiIgaGVpZ2h0PSI2Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIxOSIgeT0iMiIgd2lkdGg9IjMiIGhlaWdodD0iNiIvPjxyZWN0IGNsYXNzPSJjbHMtMSIgeD0iMTYiIHk9IjE2IiB3aWR0aD0iNiIgaGVpZ2h0PSI2Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIxOSIgeT0iMTYiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiLz48cmVjdCBjbGFzcz0iY2xzLTEiIHg9IjIiIHk9IjIiIHdpZHRoPSI2IiBoZWlnaHQ9IjYiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjUiIHk9IjIiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiLz48cmVjdCBjbGFzcz0iY2xzLTEiIHg9IjIiIHk9IjE2IiB3aWR0aD0iNiIgaGVpZ2h0PSI2Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSI1IiB5PSIxNiIgd2lkdGg9IjMiIGhlaWdodD0iNiIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iOCIgeT0iNCIgd2lkdGg9IjgiIGhlaWdodD0iMiIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iOCIgeT0iMTgiIHdpZHRoPSI4IiBoZWlnaHQ9IjIiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjE4IiB5PSI4IiB3aWR0aD0iMiIgaGVpZ2h0PSI4Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSI0IiB5PSI4IiB3aWR0aD0iMiIgaGVpZ2h0PSI4Ii8+PHJlY3QgY2xhc3M9ImNscy0zIiB4PSI0IiB5PSI4IiB3aWR0aD0iMiIgaGVpZ2h0PSIyIi8+PHJlY3QgY2xhc3M9ImNscy0zIiB4PSIxOCIgeT0iOCIgd2lkdGg9IjIiIGhlaWdodD0iMiIvPjxyZWN0IGNsYXNzPSJjbHMtMyIgeD0iOCIgeT0iNCIgd2lkdGg9IjIiIGhlaWdodD0iMiIvPjxyZWN0IGNsYXNzPSJjbHMtMyIgeD0iOCIgeT0iMTgiIHdpZHRoPSIyIiBoZWlnaHQ9IjIiLz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">VPC Network Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            vpc_name = st.text_input("VPC Name", "my-custom-vpc")
            subnet_mode = st.selectbox("Subnet Mode", ["Custom", "Auto"])
            additional_input = f"Project ID: {project_id}\nVPC Name: {vpc_name}\nSubnet Mode: {subnet_mode}"

        elif service == "Cloud Load Balancing":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOm5vbmU7fS5jbHMtMntmaWxsOiM2NjlkZjY7fS5jbHMtM3tmaWxsOiM0Mjg1ZjQ7fS5jbHMtNHtmaWxsOiNhZWNiZmE7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfTG9hZEJhbGFuY2luZ19Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48ZyBkYXRhLW5hbWU9ImNvbG9yZWQtMzIvbG9hZC1iYWxhbmNpbmciPjxyZWN0IGNsYXNzPSJjbHMtMSIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ii8+PGcgPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iMTgiIHk9IjEyIiB3aWR0aD0iMiIgaGVpZ2h0PSI0Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIxMSIgeT0iMTIiIHdpZHRoPSIyIiBoZWlnaHQ9IjQiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjQiIHk9IjEyIiB3aWR0aD0iMiIgaGVpZ2h0PSI0Ii8+PHBvbHlnb24gaWQ9IkZpbGwtMiIgY2xhc3M9ImNscy0zIiBwb2ludHM9IjEzIDExIDExIDExIDExIDcgMTMgNyAxMyAxMSIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iNCIgeT0iMTEiIHdpZHRoPSIxNiIgaGVpZ2h0PSIyIi8+PHJlY3QgY2xhc3M9ImNscy00IiB4PSI2IiB5PSIyIiB3aWR0aD0iMTIiIGhlaWdodD0iNSIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iMTIiIHk9IjIiIHdpZHRoPSI2IiBoZWlnaHQ9IjUiLz48cmVjdCBjbGFzcz0iY2xzLTQiIHg9IjE2IiB5PSIxNiIgd2lkdGg9IjYiIGhlaWdodD0iNiIvPjxyZWN0IGNsYXNzPSJjbHMtNCIgeD0iMiIgeT0iMTYiIHdpZHRoPSI2IiBoZWlnaHQ9IjYiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjUiIHk9IjE2IiB3aWR0aD0iMyIgaGVpZ2h0PSI2Ii8+PHJlY3QgY2xhc3M9ImNscy00IiB4PSI5IiB5PSIxNiIgd2lkdGg9IjYiIGhlaWdodD0iNiIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iMTIiIHk9IjE2IiB3aWR0aD0iMyIgaGVpZ2h0PSI2Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIxOSIgeT0iMTYiIHdpZHRoPSIzIiBoZWlnaHQ9IjYiLz48L2c+PC9nPjwvZz48L3N2Zz4=\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud Load Balancing Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            lb_name = st.text_input("Load Balancer Name", "my-lb")
            type = st.selectbox("Type", ["HTTP(S)", "TCP/UDP", "Internal"])
            additional_input = f"Project ID: {project_id}\nLoad Balancer Name: {lb_name}\nType: {type}"

        elif service == "Cloud Storage":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiNhZWNiZmE7fS5jbHMtMntmaWxsOiM2NjlkZjY7fS5jbHMtM3tmaWxsOiM0Mjg1ZjQ7fS5jbHMtNHtmaWxsOiNmZmY7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfQ2xvdWRTdG9yYWdlX0NvbG9yPC90aXRsZT48ZyBkYXRhLW5hbWU9IlByb2R1Y3QgSWNvbnMiPjxyZWN0IGNsYXNzPSJjbHMtMSIgeD0iMiIgeT0iNCIgd2lkdGg9IjIwIiBoZWlnaHQ9IjciLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjIwIiB5PSI0IiB3aWR0aD0iMiIgaGVpZ2h0PSI3Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjIyIDQgMjAgNCAyMCAxMSAyMiA0Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIyIiB5PSI0IiB3aWR0aD0iMiIgaGVpZ2h0PSI3Ii8+PHJlY3QgY2xhc3M9ImNscy00IiB4PSI2IiB5PSI3IiB3aWR0aD0iNiIgaGVpZ2h0PSIxIi8+PHJlY3QgY2xhc3M9ImNscy00IiB4PSIxNSIgeT0iNiIgd2lkdGg9IjMiIGhlaWdodD0iMyIgcng9IjEuNSIvPjxyZWN0IGNsYXNzPSJjbHMtMSIgeD0iMiIgeT0iMTMiIHdpZHRoPSIyMCIgaGVpZ2h0PSI3Ii8+PHJlY3QgY2xhc3M9ImNscy0yIiB4PSIyMCIgeT0iMTMiIHdpZHRoPSIyIiBoZWlnaHQ9IjciLz48cG9seWdvbiBjbGFzcz0iY2xzLTMiIHBvaW50cz0iMjIgMTMgMjAgMTMgMjAgMjAgMjIgMTMiLz48cmVjdCBjbGFzcz0iY2xzLTIiIHg9IjIiIHk9IjEzIiB3aWR0aD0iMiIgaGVpZ2h0PSI3Ii8+PHJlY3QgY2xhc3M9ImNscy00IiB4PSI2IiB5PSIxNiIgd2lkdGg9IjYiIGhlaWdodD0iMSIvPjxyZWN0IGNsYXNzPSJjbHMtNCIgeD0iMTUiIHk9IjE1IiB3aWR0aD0iMyIgaGVpZ2h0PSIzIiByeD0iMS41Ii8+PC9nPjwvc3ZnPg==\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud Storage Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            bucket_name = st.text_input("Bucket Name", "my-unique-bucket-name")
            location = st.text_input("Location", "us-central1")
            storage_class = st.selectbox("Storage Class", ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"])
            public_access = st.selectbox("Public Access", ["Not Public", "Public"])
            additional_input = f"Project ID: {project_id}\nBucket Name: {bucket_name}\nLocation: {location}\nStorage Class: {storage_class}\nPublic Access: {public_access}"

        elif service == "Cloud SQL":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiNhZWNiZmE7fS5jbHMtMSwuY2xzLTIsLmNscy0ze2ZpbGwtcnVsZTpldmVub2RkO30uY2xzLTJ7ZmlsbDojNjY5ZGY2O30uY2xzLTN7ZmlsbDojNDI4NWY0O308L3N0eWxlPjwvZGVmcz48dGl0bGU+SWNvbl8yNHB4X1NRTF9Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48ZyA+PHBvbHlnb24gY2xhc3M9ImNscy0xIiBwb2ludHM9IjQuNjcgMTAuNDQgNC42NyAxMy40NSAxMiAxNy4zNSAxMiAxNC4zNCA0LjY3IDEwLjQ0Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0xIiBwb2ludHM9IjQuNjcgMTUuMDkgNC42NyAxOC4xIDEyIDIyIDEyIDE4Ljk5IDQuNjcgMTUuMDkiLz48cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMTIgMTcuMzUgMTkuMzMgMTMuNDUgMTkuMzMgMTAuNDQgMTIgMTQuMzQgMTIgMTcuMzUiLz48cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMTIgMjIgMTkuMzMgMTguMSAxOS4zMyAxNS4wOSAxMiAxOC45OSAxMiAyMiIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMyIgcG9pbnRzPSIxOS4zMyA4LjkxIDE5LjMzIDUuOSAxMiAyIDEyIDUuMDEgMTkuMzMgOC45MSIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSIxMiAyIDQuNjcgNS45IDQuNjcgOC45MSAxMiA1LjAxIDEyIDIiLz48cG9seWdvbiBjbGFzcz0iY2xzLTEiIHBvaW50cz0iNC42NyA1Ljg3IDQuNjcgOC44OSAxMiAxMi43OSAxMiA5Ljc3IDQuNjcgNS44NyIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSIxMiAxMi43OSAxOS4zMyA4Ljg5IDE5LjMzIDUuODcgMTIgOS43NyAxMiAxMi43OSIvPjwvZz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud SQL Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            instance_id = st.text_input("Instance ID", "my-database-instance")
            db_version = st.selectbox("Database Version", ["POSTGRES_15", "POSTGRES_14", "MYSQL_8_0", "SQLSERVER_2019_STANDARD"])
            
            # Intuitive T-Shirt Sizing for DB Tier
            t_shirt_map = {"Small (db-f1-micro)": "db-f1-micro", "Medium (db-g1-small)": "db-g1-small", "Large (db-custom-1-3840)": "db-custom-1-3840"}
            size_choice = st.selectbox("Database Size (T-Shirt)", list(t_shirt_map.keys()), index=0)
            tier = t_shirt_map[size_choice]
            
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            additional_input = f"Project ID: {project_id}\nInstance ID: {instance_id}\nDB Version: {db_version}\nTier: {tier}\nRegion: {region}"

        elif service == "Spanner":
            st.markdown("### Cloud Spanner Configuration")
            project_id = st.text_input("Project ID", "my-gcp-project")
            instance_id = st.text_input("Instance ID", "my-spanner-instance")
            config = st.text_input("Instance Config (Region)", "regional-us-central1")
            
            # Intuitive T-Shirt Sizing for Processing Units
            t_shirt_map = {"Small (100 PU)": 100, "Medium (500 PU)": 500, "Large (1000 PU)": 1000}
            size_choice = st.selectbox("Compute Capacity (T-Shirt)", list(t_shirt_map.keys()), index=2)
            nodes = t_shirt_map[size_choice]
            
            additional_input = f"Project ID: {project_id}\nInstance ID: {instance_id}\nConfig: {config}\nProcessing Units: {nodes}"

        elif service == "Firestore":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM2NjlkZjY7fS5jbHMtMntmaWxsOiNhZWNiZmE7fS5jbHMtM3tmaWxsOiM0Mjg1ZjQ7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfRmlyZXN0b3JlX0NvbG9yPC90aXRsZT48ZyBkYXRhLW5hbWU9IlByb2R1Y3QgSWNvbnMiPjxnIGRhdGEtbmFtZT0iY29sb3JlZC0zMi9maXJlc3RvcmUiPjxnID48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0yMSwxMywxMiw5djRsOSw0Wm0wLTdMMTIsMlY2bDksNFoiLz48cG9seWdvbiBpZD0iUmVjdGFuZ2xlLTciIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSIzIDYgMTIgMiAxMiA2IDMgMTAgMyA2Ii8+PHBvbHlnb24gaWQ9IlJlY3RhbmdsZS03LTIiIGRhdGEtbmFtZT0iUmVjdGFuZ2xlLTciIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSIzIDEzIDEyIDkgMTIgMTMgMyAxNyAzIDEzIi8+PHBvbHlnb24gaWQ9IlJlY3RhbmdsZS03LTMiIGRhdGEtbmFtZT0iUmVjdGFuZ2xlLTciIGNsYXNzPSJjbHMtMyIgcG9pbnRzPSIxMiAxOCAxNS4zNyAxNi41IDE5Ljg4IDE4LjUgMTIgMjIgMTIgMTgiLz48L2c+PC9nPjwvZz48L3N2Zz4=\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Firestore Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            location = st.text_input("Location", "nam5 (us-central)")
            mode = st.selectbox("Database Mode", ["Native Mode", "Datastore Mode"])
            additional_input = f"Project ID: {project_id}\nLocation: {location}\nMode: {mode}"

        elif service == "Bigtable":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM2NjlkZjY7fS5jbHMtMSwuY2xzLTIsLmNscy0ze2ZpbGwtcnVsZTpldmVub2RkO30uY2xzLTJ7ZmlsbDojYWVjYmZhO30uY2xzLTN7ZmlsbDojNDI4NWY0O308L3N0eWxlPjwvZGVmcz48dGl0bGU+SWNvbl8yNHB4X0JpZ1RhYmxlX0NvbG9yPC90aXRsZT48ZyBkYXRhLW5hbWU9IlByb2R1Y3QgSWNvbnMiPjxnID48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xNi4yMiw2LjQ1LDEyLDMuOTRhMi44NiwyLjg2LDAsMCwxLTEuMjUtMS43MXMuMTYtLjMyLjM4LS4yLDMuNSwyLjA2LDUuMjUsMy4xYy42My4zNy4yNCwyLC4yNCwyQS43Ny43NywwLDAsMCwxNi4yMiw2LjQ1WiIvPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTE3LjQ5LDEyLjY5YS4zNS4zNSwwLDAsMS0uMTYuMzNsLTEsLjY4VjUuNzVjMC0uMjcuMTctLjU2LS4wNi0uN2wuOTIuNjhhLjczLjczLDAsMCwxLC4zNS42NVoiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMiwxMy42YS4zNi4zNiwwLDAsMS0uMi0uMDZMOC4zNCwxMS40OHYuOUwxMiwxNC41NmwuMjktLjU3cy0uMjItLjM5LS4yOS0uMzlaIi8+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMTIuMiwxNS40YS4zNi4zNiwwLDAsMS0uNCwwTDguMzQsMTMuMzRWMTRhLjQyLjQyLDAsMCwwLC4xOS4zNWwzLjI4LDJhLjM3LjM3LDAsMCwwLC4zOCwwLDIsMiwwLDAsMCwuMi0uNTJsLS4xOS0uMzlaIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNMTIsMTIuNzNsMy42Ni0yLjE4di0uNDNhLjM5LjM5LDAsMCwwLS4xOS0uMzRsLTMuMjgtMmEuMzcuMzcsMCwwLDAtLjM4LDBsLTMuMjgsMmEuNDEuNDEsMCwwLDAtLjE5LjM0di40M0wxMiwxMi43M1oiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMiwxMS44Myw4LjUzLDkuNzhhLjQxLjQxLDAsMCwwLS4xOS4zNHYuNDNMMTIsMTIuNzNsLjI4LS41NkwxMiwxMS44M1oiLz48cGF0aCBjbGFzcz0iY2xzLTMiIGQ9Ik0xMiwxMy42djFsMy42Ni0yLjE4di0uOUwxMi4yLDEzLjU0YS42NS42NSwwLDAsMS0uMi4wNloiLz48cGF0aCBjbGFzcz0iY2xzLTMiIGQ9Ik0xMi4yLDE1LjRhLjM2LjM2LDAsMCwxLS4yLjA2YzAsLjI4LDAsLjksMCwuOWEuNS41LDAsMCwwLC4yMS0uMDVsMy4yOC0yYS4zOS4zOSwwLDAsMCwuMTktLjM1di0uNjZMMTIuMiwxNS40WiIvPjxwYXRoIGNsYXNzPSJjbHMtMyIgZD0iTTE1LjQ3LDkuNzgsMTIsMTEuODN2LjlsMy42Ni0yLjE4di0uNDNhLjM5LjM5LDAsMCwwLS4xOS0uMzRaIi8+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNy43OCwxNy41MywxMS45MywyMGEyLjcyLDIuNzIsMCwwLDEsMS4yOCwxLjguMTguMTgsMCwwLDEtLjI4LjE4TDcuNDgsMTguNzVjLS41My0uMzItLjA3LTEuODgtLjA3LTEuODhBLjc3Ljc3LDAsMCwwLDcuNzgsMTcuNTNaIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNNi41MSwxNy43M1YxMS4xN2EuNDEuNDEsMCwwLDEsLjE5LS4zM2wxLS41OXY3LjkxYzAsLjI3LDAsLjY5LjIxLjgzbC0xLjA2LS42NkEuNzUuNzUsMCwwLDEsNi41MSwxNy43M1oiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMC4xNiw1LjQ2YS43NS43NSwwLDAsMC0uNzQsMEw1LjIyLDhhMi42MywyLjYzLDAsMCwxLTIuMDguMjYuMjMuMjMsMCwwLDEsMC0uNGMuMTgtLjA5LDYuMzItMy43NCw2LjMyLTMuNzQuMjMtLjE0Ljc0LDEuMzkuNzQsMS4zOVoiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik0xMC4xNSw0LjA4bDUuMzIsMy4xNWEuMzcuMzcsMCwwLDEsLjIuMzFWOC43Mkw5LDQuNzZhLjc1Ljc1LDAsMCwwLS43NCwwbDEuMTgtLjY5YS43MS43MSwwLDAsMSwuNzMsMFoiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMy44MiwxOC40OWEuNzMuNzMsMCwwLDAsLjc0LDBMMTguNzYsMTZhMi42MywyLjYzLDAsMCwxLDIuMS0uMjUuMjEuMjEsMCwwLDEsMCwuMzhsLTYuMzMsMy43NWMtLjIyLjE0LS43NC0xLjQtLjc0LTEuNFoiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik04LjUxLDE2Ljc1YS41Ni41NiwwLDAsMS0uMTctLjMzVjE1LjI2TDE1LDE5LjE5YS42OS42OSwwLDAsMCwuNzMsMGwtMS4xOC43YS43LjcsMCwwLDEtLjc0LDBaIi8+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNNi4yNiw5LjgxYS43Ni43NiwwLDAsMC0uMzcuNjV2NWEyLjc1LDIuNzUsMCwwLDEtLjg3LDIsLjE4LjE4LDAsMCwxLS4zLS4xM1Y5Ljc3YzAtLjI4LDEuNTQsMCwxLjU0LDBaIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNOS43Nyw2LjUyYS4zNC4zNCwwLDAsMSwuMzYsMGwxLC41OUw1LjA1LDEwLjY3YS43Ny43NywwLDAsMC0uMzcuNjZWOS45NGEuNzIuNzIsMCwwLDEsLjM4LS42NFoiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xOC4xNywxMy40NHYtNWEyLjgxLDIuODEsMCwwLDEsLjg0LTJzLjMzLS4xMS4zMS4yMSwwLDcuMzcsMCw3LjM3Yy0uMzEuMzctMS42MSwwLTEuNjEsMEEuODEuODEsMCwwLDAsMTguMTcsMTMuNDRaIi8+PHBhdGggY2xhc3M9ImNscy0yIiBkPSJNMTksMTQuNjFsLTQuNzQsMi44NWEuMzUuMzUsMCwwLDEtLjM3LDBsLTEtLjU3TDE5LDEzLjIyYS43Ny43NywwLDAsMCwuMzctLjY2VjE0QzE5LjM1LDE0LjIzLDE5LDE0LjYxLDE5LDE0LjYxWiIvPjwvZz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Bigtable Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            instance_id = st.text_input("Instance ID", "my-bigtable-instance")
            cluster_id = st.text_input("Cluster ID", "my-bigtable-cluster")
            zone = st.selectbox("Zone", ["us-central1-a", "us-central1-b", "us-central1-c", "us-east1-b", "us-east1-c", "us-east1-d", "us-west1-a", "us-west1-b", "us-west1-c", "europe-west1-b", "europe-west1-c", "europe-west4-a", "europe-west4-b", "europe-west4-c", "asia-northeast1-a", "asia-northeast1-b", "asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"])
            
            # Intuitive T-Shirt Sizing for Bigtable Nodes
            t_shirt_map = {"Small (1 Node)": 1, "Medium (3 Nodes)": 3, "Large (5 Nodes)": 5}
            size_choice = st.selectbox("Cluster Size (T-Shirt)", list(t_shirt_map.keys()), index=0)
            nodes = t_shirt_map[size_choice]
            
            additional_input = f"Project ID: {project_id}\nInstance ID: {instance_id}\nCluster ID: {cluster_id}\nZone: {zone}\nNodes: {nodes}"

        elif service == "BigQuery":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiNhZWNiZmE7fS5jbHMtMSwuY2xzLTIsLmNscy0ze2ZpbGwtcnVsZTpldmVub2RkO30uY2xzLTJ7ZmlsbDojNjY5ZGY2O30uY2xzLTN7ZmlsbDojNDI4NWY0O308L3N0eWxlPjwvZGVmcz48dGl0bGU+SWNvbl8yNHB4X0JpZ1F1ZXJ5X0NvbG9yPC90aXRsZT48ZyBkYXRhLW5hbWU9IlByb2R1Y3QgSWNvbnMiPjxnID48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik02LjczLDEwLjgzdjIuNjNBNC45MSw0LjkxLDAsMCwwLDguNDQsMTUuMlYxMC44M1oiLz48cGF0aCBjbGFzcz0iY2xzLTIiIGQ9Ik05Ljg5LDguNDF2Ny41M0E3LjYyLDcuNjIsMCwwLDAsMTEsMTYsOCw4LDAsMCwwLDEyLDE2VjguNDFaIi8+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMTMuNjQsMTEuODZ2My4yOWE1LDUsMCwwLDAsMS43LTEuODJWMTEuODZaIi8+PHBhdGggY2xhc3M9ImNscy0zIiBkPSJNMTcuNzQsMTYuMzJsLTEuNDIsMS40MmEuNDIuNDIsMCwwLDAsMCwuNmwzLjU0LDMuNTRhLjQyLjQyLDAsMCwwLC41OSwwbDEuNDMtMS40M2EuNDIuNDIsMCwwLDAsMC0uNTlsLTMuNTQtMy41NGEuNDIuNDIsMCwwLDAtLjYsMCIvPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTExLDJhOSw5LDAsMSwwLDksOSw5LDksMCwwLDAtOS05bTAsMTUuNjlBNi42OCw2LjY4LDAsMSwxLDE3LjY5LDExLDYuNjgsNi42OCwwLDAsMSwxMSwxNy42OSIvPjwvZz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">BigQuery Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            dataset_id = st.text_input("Dataset ID", "my_dataset")
            location = st.text_input("Location", "US")
            additional_input = f"Project ID: {project_id}\nDataset ID: {dataset_id}\nLocation: {location}"

        elif service == "Pub/Sub":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMjRweCIgaGVpZ2h0PSIyNHB4IiB2aWV3Qm94PSIwIDAgMjQgMjQiPjxkZWZzPjxzdHlsZT4uY2xzLTF7ZmlsdGVyOnVybCgjbHVtaW5vc2l0eS1ub2NsaXApO30uY2xzLTJ7ZmlsbDojNjY5ZGY2O30uY2xzLTN7bWFzazp1cmwoI21hc2spO30uY2xzLTR7ZmlsbDojNDI4NWY0O30uY2xzLTV7ZmlsbDojYWVjYmZhO308L3N0eWxlPjxmaWx0ZXIgaWQ9Imx1bWlub3NpdHktbm9jbGlwIiB4PSI0LjY0IiB5PSI0LjE5IiB3aWR0aD0iMTQuNzMiIGhlaWdodD0iMTIuNzYiIGZpbHRlclVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgY29sb3ItaW50ZXJwb2xhdGlvbi1maWx0ZXJzPSJzUkdCIj48ZmVGbG9vZCBmbG9vZC1jb2xvcj0iI2ZmZiIgcmVzdWx0PSJiZyIvPjxmZUJsZW5kIGluPSJTb3VyY2VHcmFwaGljIiBpbjI9ImJnIi8+PC9maWx0ZXI+PG1hc2sgaWQ9Im1hc2siIHg9IjQuNjQiIHk9IjQuMTkiIHdpZHRoPSIxNC43MyIgaGVpZ2h0PSIxMi43NiIgbWFza1VuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PGNpcmNsZSBjbGFzcz0iY2xzLTEiIGN4PSIxMiIgY3k9IjEyLjIzIiByPSIzLjU4Ii8+PC9tYXNrPjwvZGVmcz48dGl0bGU+SWNvbl8yNHB4X1B1Yi1TdWJfQ29sb3I8L3RpdGxlPjxnIGRhdGEtbmFtZT0iUHJvZHVjdCBJY29ucyI+PGNpcmNsZSBjbGFzcz0iY2xzLTIiIGN4PSIxOC45NyIgY3k9IjguMjEiIHI9IjEuNzIiLz48Y2lyY2xlIGNsYXNzPSJjbHMtMiIgY3g9IjUuMDMiIGN5PSI4LjIxIiByPSIxLjcyIi8+PGNpcmNsZSBjbGFzcz0iY2xzLTIiIGN4PSIxMiIgY3k9IjIwLjI4IiByPSIxLjcyIi8+PGcgY2xhc3M9ImNscy0zIj48cmVjdCBjbGFzcz0iY2xzLTQiIHg9IjE0LjY5IiB5PSIxMC4yMiIgd2lkdGg9IjEuNTkiIGhlaWdodD0iOC4wNCIgdHJhbnNmb3JtPSJtYXRyaXgoMC41LCAtMC44NywgMC44NywgMC41LCAtNC41OSwgMjAuNTMpIi8+PHJlY3QgY2xhc3M9ImNscy00IiB4PSI0LjQ5IiB5PSIxMy40NSIgd2lkdGg9IjguMDQiIGhlaWdodD0iMS41OSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTUuOTggNi4xNykgcm90YXRlKC0zMCkiLz48cmVjdCBjbGFzcz0iY2xzLTQiIHg9IjExLjIiIHk9IjQuMTkiIHdpZHRoPSIxLjU5IiBoZWlnaHQ9IjguMDQiLz48L2c+PGNpcmNsZSBjbGFzcz0iY2xzLTUiIGN4PSIxMiIgY3k9IjEyLjIzIiByPSIyLjc4Ii8+PGNpcmNsZSBjbGFzcz0iY2xzLTUiIGN4PSI1LjAzIiBjeT0iMTYuMjUiIHI9IjIuMTkiLz48Y2lyY2xlIGNsYXNzPSJjbHMtNSIgY3g9IjE4Ljk3IiBjeT0iMTYuMjUiIHI9IjIuMTkiLz48Y2lyY2xlIGNsYXNzPSJjbHMtNSIgY3g9IjEyIiBjeT0iNC4xOSIgcj0iMi4xOSIvPjwvZz48L3N2Zz4=\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Pub/Sub Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            topic_name = st.text_input("Topic Name", "my-topic")
            subscription_name = st.text_input("Subscription Name", "my-sub")
            additional_input = f"Project ID: {project_id}\nTopic Name: {topic_name}\nSubscription Name: {subscription_name}"

        elif service == "Artifact Registry":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIGJhc2VQcm9maWxlPSJ0aW55IiBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIKCSB4PSIwcHgiIHk9IjBweCIgd2lkdGg9IjI0cHgiIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAwIDI0IDI0IiBvdmVyZmxvdz0idmlzaWJsZSIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+CjxnID4KCTxyZWN0IHk9IjAiIGZpbGw9Im5vbmUiIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIvPgoJPHBvbHlnb24gZmlsbC1ydWxlPSJldmVub2RkIiBmaWxsPSIjNUM4NURFIiBwb2ludHM9IjYsMi40IDAuOCw1LjQgMC44LDE5LjEgNiwyMi4xIDYsMTkuNSAzLDE3LjggMyw2LjcgNiw1IAkiLz4KCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIwLjgsOCAwLjgsMTYuNSAzLDE3LjggMyw2LjcgCSIvPgoJPHBvbHlnb24gZmlsbC1ydWxlPSJldmVub2RkIiBmaWxsPSIjMzM2N0Q2IiBwb2ludHM9IjAuOCw4IDMsNy41IDMsNi43IAkiLz4KCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzVDODVERSIgcG9pbnRzPSIxOCwyLjQgMTgsNSAyMSw2LjcgMjEsMTcuOCAxOCwxOS41IDE4LDIyLjEgMjMuMiwxOS4xIDIzLjIsNS40IAkiLz4KCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIyMSwxNy44IDIzLjIsMTYuNSAyMy4yLDggMjEsNi43IAkiLz4KCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIyMSw3LjUgMjMuMiw4IDIxLDYuNyAJIi8+Cgk8cG9seWdvbiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGZpbGw9IiMzMzY3RDYiIHBvaW50cz0iMjEsMTcuMSAyMSwxNy44IDIzLjIsMTYuNSAJIi8+Cgk8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg2Ljg2MDAwMCwgNi41MDAwMDApIj4KCQk8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg0LjU0MDAwMCwgMC4wMDAwMDApIj4KCQkJPHBvbHlnb24gZmlsbC1ydWxlPSJldmVub2RkIiBmaWxsPSIjNUM4NURFIiBwb2ludHM9IjAuNiwtMSAtMi40LDAuNiAwLjYsMi4yIDMuNiwwLjYgCQkJIi8+CgkJCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIxLDUuOSAzLjksNC4zIDMuOSwxLjIgMSwyLjggCQkJIi8+CgkJCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIwLjMsMi44IC0yLjcsMS4yIC0yLjcsNC4zIDAuMyw1LjkgCQkJIi8+CgkJPC9nPgoJCTxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAuMDAwMDAwLCA3Ljk3NjE5MCkiPgoJCQk8cG9seWdvbiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGZpbGw9IiM1Qzg1REUiIHBvaW50cz0iMS43LC0zLjEgLTEuMiwtMS41IDEuNywwLjEgNC41LC0xLjUgCQkJIi8+CgkJCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIxLjksMy44IDQuOCwyLjIgNC44LC0xIDEuOSwwLjYgCQkJIi8+CgkJCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSIxLjQsMC42IC0xLjUsLTEgLTEuNSwyLjIgMS40LDMuOCAJCQkiLz4KCQk8L2c+CgkJPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoOS4zNjAwMDAsIDcuOTc2MTkwKSI+CgkJCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzVDODVERSIgcG9pbnRzPSItMC43LC0zLjEgLTMuNiwtMS41IC0wLjcsMC4xIDIuMiwtMS41IAkJCSIvPgoJCQk8cG9seWdvbiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGZpbGw9IiMzMzY3RDYiIHBvaW50cz0iLTAuNCwzLjggMi41LDIuMiAyLjUsLTEgLTAuNCwwLjYgCQkJIi8+CgkJCTxwb2x5Z29uIGZpbGwtcnVsZT0iZXZlbm9kZCIgZmlsbD0iIzMzNjdENiIgcG9pbnRzPSItMSwwLjYgLTMuOSwtMSAtMy45LDIuMiAtMSwzLjggCQkJIi8+CgkJPC9nPgoJPC9nPgo8L2c+Cjwvc3ZnPgo=\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Artifact Registry Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            repository_name = st.text_input("Repository Name", "my-docker-repo")
            location = st.text_input("Location", "us-central1")
            format = st.selectbox("Format", ["DOCKER", "MAVEN", "NPM", "PYTHON"])
            additional_input = f"Project ID: {project_id}\nRepository Name: {repository_name}\nLocation: {location}\nFormat: {format}"

        elif service == "Cloud Build":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM0Mjg1ZjQ7fS5jbHMtMntmaWxsOiM2NjlkZjY7fS5jbHMtM3tmaWxsOiNhZWNiZmE7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfQ2xvdWRCdWlsZF9Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48ZyA+PGcgPjxnID48cG9seWdvbiBjbGFzcz0iY2xzLTEiIHBvaW50cz0iMTIuMTUgMTYuMjQgMTUuNjcgMTQuMjEgMTUuNjcgMTAuMTUgMTQuNDkgOS40NiAxMC45NyAxNS41NiAxMi4xNSAxNi4yNCIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMiIgcG9pbnRzPSI4LjYzIDEwLjE1IDguNjMgMTQuMjEgOS44MSAxNC44OSAxMy4zNCA4LjggMTIuMTUgOC4xMSA4LjYzIDEwLjE1Ii8+PC9nPjwvZz48L2c+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjExLjQ2IDE3LjQ1IDcuMjQgMTUuMDEgNy4yNCAxMC4xNSAzLjQ5IDcuOTggMy40OSAxNy4xOCAxMS40NiAyMS43OCAxMS40NiAxNy40NSIvPjxwb2x5Z29uIGNsYXNzPSJjbHMtMyIgcG9pbnRzPSI3LjkzIDguOTUgMTIuMTUgNi41MSAxNi4zNyA4Ljk1IDIwLjEzIDYuNzggMTIuMTUgMi4xNyA0LjE3IDYuNzggNy45MyA4Ljk1Ii8+PHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjE3LjA2IDE1LjAxIDEyLjg0IDE3LjQ1IDEyLjg0IDIxLjc4IDIwLjgyIDE3LjE4IDIwLjgyIDcuOTggMTcuMDYgMTAuMTUgMTcuMDYgMTUuMDEiLz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud Build Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            trigger_name = st.text_input("Trigger Name", "my-build-trigger")
            repo = st.text_input("Source Repository", "github.com/my-org/my-repo")
            additional_input = f"Project ID: {project_id}\nTrigger Name: {trigger_name}\nRepository: {repo}"

        elif service == "Secret Manager":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjRweCIgaGVpZ2h0PSIyNHB4IiB2aWV3Qm94PSIwIDAgMjQgMjQiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CiAgICA8ZyBzdHJva2U9Im5vbmUiIHN0cm9rZS13aWR0aD0iMSIgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj4KICAgICAgICA8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgyLjAwMDAwMCwgNi4wMDAwMDApIiBmaWxsPSIjNDI4NUY0IiBmaWxsLXJ1bGU9Im5vbnplcm8iPgogICAgICAgICAgICA8cGF0aCBkPSJNMjAsOS40MTQ2OTEyNWUtMTQgTDIwLDExLjg4Njc5MjUgTDE2LjAzNzczNTgsMTEuODg2NzkyNSBDMTUuOTMzNTMxMiwxMS44ODY3OTI1IDE1Ljg0OTA1NjYsMTEuODAyMzE3OSAxNS44NDkwNTY2LDExLjY5ODExMzIgTDE1Ljg0OTA1NjYsMTAuNTY2MDM3NyBDMTUuODQ5MDU2NiwxMC40NjE4MzMxIDE1LjkzMzUzMTIsMTAuMzc3MzU4NSAxNi4wMzc3MzU4LDEwLjM3NzM1ODUgTDE4LjQ5MDA1NjYsMTAuMzc3IEwxOC40OTAwNTY2LDEuNTA5IEwxNi4wMzc3MzU4LDEuNTA5NDMzOTYgQzE1LjkzMzUzMTIsMS41MDk0MzM5NiAxNS44NDkwNTY2LDEuNDI0OTU5MzkgMTUuODQ5MDU2NiwxLjMyMDc1NDcyIEwxNS44NDkwNTY2LDAuMTg4Njc5MjQ1IEMxNS44NDkwNTY2LDAuMDg0NDc0NTc1NSAxNS45MzM1MzEyLDkuNDExMDU0MzRlLTE0IDE2LjAzNzczNTgsOS40MTQ2OTEyNWUtMTQgTDIwLDkuNDE0NjkxMjVlLTE0IFogTTQuMzA5MTAxLDkuNDE0NjkxMjVlLTE0IEM0LjQxMzMwNTY3LDkuMzg3Nzg2OWUtMTQgNC40OTc3ODAyNCwwLjA4NDQ3NDU3NTUgNC40OTc3ODAyNCwwLjE4ODY3OTI0NSBMNC40OTc3ODAyNCwxLjMyMDc1NDcyIEM0LjQ5Nzc4MDI0LDEuNDI0OTU5MzkgNC40MTMzMDU2NywxLjUwOTQzMzk2IDQuMzA5MTAxLDEuNTA5NDMzOTYgTDEuNTA5LDEuNTA5IEwxLjUwOSwxMC4zNzcgTDQuMjkyNDUyODMsMTAuMzc3MzU4NSBDNC4zOTY2NTc1LDEwLjM3NzM1ODUgNC40ODExMzIwOCwxMC40NjE4MzMxIDQuNDgxMTMyMDgsMTAuNTY2MDM3NyBMNC40ODExMzIwOCwxMS42OTgxMTMyIEM0LjQ4MTEzMjA4LDExLjgwMjMxNzkgNC4zOTY2NTc1LDExLjg4Njc5MjUgNC4yOTI0NTI4MywxMS44ODY3OTI1IEwyLjE0MDUwOTk5ZS0xMywxMS44ODY3OTI1IEwyLjE0MDUwOTk5ZS0xMyw5LjQxNDY5MTI1ZS0xNCBMNC4zMDkxMDEsOS40MTQ2OTEyNWUtMTQgWiBNMTUuNDI3MTA5OCwzLjg2NzkyNDUzIEwxNS40MjcxMDk4LDUuMzI0MDU2NiBMMTUuNDg3OTMwNSw1LjM0ODUyOTQxIEwxNi44MzgxNDk0LDQuODcxMzA5NjYgTDE3LjExNzkyNDUsNS42OTExNDg3MiBMMTUuNzU1NTQxNCw2LjE1NjEzMjA4IEwxNS43MTkwNDksNi4yNTQwMjMzMSBMMTYuNjU1Njg3NCw3LjUxNDM3MjkyIEwxNS45NTAxNjc2LDguMDI4MzAxODkgTDE1LjAzNzg1NzUsNi43Njc5NTIyOCBMMTQuOTUyNzA4NSw2Ljc2Nzk1MjI4IEwxNC4wNDAzOTg0LDguMDI4MzAxODkgTDEzLjMzNDg3ODYsNy41MTQzNzI5MiBMMTQuMjU5MzUyOSw2LjI1NDAyMzMxIEwxNC4yMzUwMjQ2LDYuMTU2MTMyMDggTDEyLjg3MjY0MTUsNS42OTExNDg3MiBMMTMuMTUyNDE2Niw0Ljg3MTMwOTY2IEwxNC40OTA0NzE0LDUuMzQ4NTI5NDEgTDE0LjU2MzQ1NjIsNS4zMjQwNTY2IEwxNC41NjM0NTYyLDMuODY3OTI0NTMgTDE1LjQyNzEwOTgsMy44Njc5MjQ1MyBaIE01LjE5NTk3NzczLDMuODY3OTI0NTMgTDUuMTk1OTc3NzMsNS4zMDk2Mzk0NSBMNS4yNTY3OTg0LDUuMzMzODY5OTYgTDYuNjA3MDE3MzUsNC44NjEzNzUxNSBMNi44ODY3OTI0NSw1LjY3MzA5NyBMNS41MjQ0MDkzNiw2LjEzMzQ3NjU2IEw1LjQ4NzkxNjk2LDYuMjMwMzk4NTcgTDYuNDI0NTU1MzMsNy40NzgyNjk0NyBMNS43MTkwMzU1Miw3Ljk4NzExMDAzIEw0LjgwNjcyNTQxLDYuNzM5MjM5MTMgTDQuNzIxNTc2NDcsNi43MzkyMzkxMyBMMy44MDkyNjYzNyw3Ljk4NzExMDAzIEwzLjEwMzc0NjU1LDcuNDc4MjY5NDcgTDQuMDI4MjIwNzksNi4yMzAzOTg1NyBMNC4wMDM4OTI1Miw2LjEzMzQ3NjU2IEwyLjY0MTUwOTQzLDUuNjczMDk3IEwyLjkyMTI4NDUzLDQuODYxMzc1MTUgTDQuMjU5MzM5MzUsNS4zMzM4Njk5NiBMNC4zMzIzMjQxNiw1LjMwOTYzOTQ1IEw0LjMzMjMyNDE2LDMuODY3OTI0NTMgTDUuMTk1OTc3NzMsMy44Njc5MjQ1MyBaIE0xMC4yOTAzMTczLDMuODY3OTI0NTMgTDEwLjI5MDMxNzMsNS4zMDk2Mzk0NSBMMTAuMzUxMTM4LDUuMzMzODY5OTYgTDExLjcwMTM1Nyw0Ljg2MTM3NTE1IEwxMS45ODExMzIxLDUuNjczMDk3IEwxMC42MTg3NDksNi4xMzM0NzY1NiBMMTAuNTgyMjU2Niw2LjIzMDM5ODU3IEwxMS41MTg4OTUsNy40NzgyNjk0NyBMMTAuODEzMzc1MSw3Ljk4NzExMDAzIEw5LjkwMTA2NTA0LDYuNzM5MjM5MTMgTDkuODE1OTE2MDksNi43MzkyMzkxMyBMOC45MDM2MDU5OSw3Ljk4NzExMDAzIEw4LjE5ODA4NjE4LDcuNDc4MjY5NDcgTDkuMTIyNTYwNDIsNi4yMzAzOTg1NyBMOS4wOTgyMzIxNSw2LjEzMzQ3NjU2IEw3LjczNTg0OTA2LDUuNjczMDk3IEw4LjAxNTYyNDE2LDQuODYxMzc1MTUgTDkuMzUzNjc4OTcsNS4zMzM4Njk5NiBMOS40MjY2NjM3OCw1LjMwOTYzOTQ1IEw5LjQyNjY2Mzc4LDMuODY3OTI0NTMgTDEwLjI5MDMxNzMsMy44Njc5MjQ1MyBaIiA+PC9wYXRoPgogICAgICAgIDwvZz4KICAgIDwvZz4KPC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Secret Manager Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            secret_id = st.text_input("Secret ID", "my-api-key")
            additional_input = f"Project ID: {project_id}\nSecret ID: {secret_id}"
            
        elif service == "IAM":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM2NjlkZjY7fS5jbHMtMSwuY2xzLTJ7ZmlsbC1ydWxlOmV2ZW5vZGQ7fS5jbHMtMntmaWxsOiM0Mjg1ZjQ7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfSUFNX0NvbG9yPC90aXRsZT48ZyBkYXRhLW5hbWU9IlByb2R1Y3QgSWNvbnMiPjxnID48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik0xMiwyLDMuNzksNS40MnY1LjYzYzAsNS4wNiwzLjUsOS44LDguMjEsMTEsNC43MS0xLjE1LDguMjEtNS44OSw4LjIxLTEwLjk1VjUuNDJabTAsMy43OWEyLjYzLDIuNjMsMCwxLDEtMS44Ni43N0EyLjYzLDIuNjMsMCwwLDEsMTIsNS43OVptNC4xMSwxMS4xNUE4LjY0LDguNjQsMCwwLDEsMTIsMTkuODdhOC42NCw4LjY0LDAsMCwxLTQuMTEtMi45M1YxNC42OWMwLTEuNjcsMi43NC0yLjUyLDQuMTEtMi41MnM0LjExLjg1LDQuMTEsMi41MnYyLjI1WiIvPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTEyLDJWNS43OWEyLjYzLDIuNjMsMCwxLDEsMCw1LjI2djEuMTJjMS4zNywwLDQuMTEuODUsNC4xMSwyLjUydjIuMjVBOC42NCw4LjY0LDAsMCwxLDEyLDE5Ljg3VjIyYzQuNzEtMS4xNSw4LjIxLTUuODksOC4yMS0xMC45NVY1LjQyWiIvPjwvZz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">IAM Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            principal = st.text_input("Principal (user:email@example.com / serviceAccount:...)", "user:admin@example.com")
            role = st.text_input("Role", "roles/viewer")
            additional_input = f"Project ID: {project_id}\nPrincipal: {principal}\nRole: {role}"

        elif service == "Vertex AI":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0cHgiIGhlaWdodD0iMjRweCI+PHBhdGggZD0iTTIwLDEzLjg5QS43Ny43NywwLDAsMCwxOSwxMy43M2wtNyw1LjE0di4yMmEuNzIuNzIsMCwxLDEsMCwxLjQzdjBhLjc0Ljc0LDAsMCwwLC40NS0uMTVsNy40MS01LjQ3QS43Ni43NiwwLDAsMCwyMCwxMy44OVoiIHN0eWxlPSJmaWxsOiM2NjlkZjYiLz48cGF0aCBkPSJNMTIsMjAuNTJhLjcyLjcyLDAsMCwxLDAtMS40M2gwdi0uMjJMNSwxMy43M2EuNzYuNzYsMCwwLDAtMSwuMTYuNzQuNzQsMCwwLDAsLjE2LDFsNy40MSw1LjQ3YS43My43MywwLDAsMCwuNDQuMTV2MFoiIHN0eWxlPSJmaWxsOiNhZWNiZmEiLz48cGF0aCBkPSJNMTIsMTguMzRhMS40NywxLjQ3LDAsMSwwLDEuNDcsMS40N0ExLjQ3LDEuNDcsMCwwLDAsMTIsMTguMzRabTAsMi4xOGEuNzIuNzIsMCwxLDEsLjcyLS43MUEuNzEuNzEsMCwwLDEsMTIsMjAuNTJaIiBzdHlsZT0iZmlsbDojNDI4NWY0Ii8+PHBhdGggZD0iTTYsNi4xMWEuNzYuNzYsMCwwLDEtLjc1LS43NVYzLjQ4YS43Ni43NiwwLDEsMSwxLjUxLDBWNS4zNkEuNzYuNzYsMCwwLDEsNiw2LjExWiIgc3R5bGU9ImZpbGw6I2FlY2JmYSIvPjxjaXJjbGUgY3g9IjUuOTgiIGN5PSIxMiIgcj0iMC43NiIgc3R5bGU9ImZpbGw6I2FlY2JmYSIvPjxjaXJjbGUgY3g9IjUuOTgiIGN5PSI5Ljc5IiByPSIwLjc2IiBzdHlsZT0iZmlsbDojYWVjYmZhIi8+PGNpcmNsZSBjeD0iNS45OCIgY3k9IjcuNTciIHI9IjAuNzYiIHN0eWxlPSJmaWxsOiNhZWNiZmEiLz48cGF0aCBkPSJNMTgsOC4zMWEuNzYuNzYsMCwwLDEtLjc1LS43NlY1LjY3YS43NS43NSwwLDEsMSwxLjUsMFY3LjU1QS43NS43NSwwLDAsMSwxOCw4LjMxWiIgc3R5bGU9ImZpbGw6IzQyODVmNCIvPjxjaXJjbGUgY3g9IjE4LjAyIiBjeT0iMTIuMDEiIHI9IjAuNzYiIHN0eWxlPSJmaWxsOiM0Mjg1ZjQiLz48Y2lyY2xlIGN4PSIxOC4wMiIgY3k9IjkuNzYiIHI9IjAuNzYiIHN0eWxlPSJmaWxsOiM0Mjg1ZjQiLz48Y2lyY2xlIGN4PSIxOC4wMiIgY3k9IjMuNDgiIHI9IjAuNzYiIHN0eWxlPSJmaWxsOiM0Mjg1ZjQiLz48cGF0aCBkPSJNMTIsMTVhLjc2Ljc2LDAsMCwxLS43NS0uNzVWMTIuMzRhLjc2Ljc2LDAsMCwxLDEuNTEsMHYxLjg5QS43Ni43NiwwLDAsMSwxMiwxNVoiIHN0eWxlPSJmaWxsOiM2NjlkZjYiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjE2LjQ1IiByPSIwLjc2IiBzdHlsZT0iZmlsbDojNjY5ZGY2Ii8+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMC4xNCIgcj0iMC43NiIgc3R5bGU9ImZpbGw6IzY2OWRmNiIvPjxjaXJjbGUgY3g9IjEyIiBjeT0iNy45MiIgcj0iMC43NiIgc3R5bGU9ImZpbGw6IzY2OWRmNiIvPjxwYXRoIGQ9Ik0xNSwxMC41NGEuNzYuNzYsMCwwLDEtLjc1LS43NVY3LjkxYS43Ni43NiwwLDEsMSwxLjUxLDBWOS43OUEuNzYuNzYsMCwwLDEsMTUsMTAuNTRaIiBzdHlsZT0iZmlsbDojNDI4NWY0Ii8+PGNpcmNsZSBjeD0iMTUuMDEiIGN5PSI1LjY5IiByPSIwLjc2IiBzdHlsZT0iZmlsbDojNDI4NWY0Ii8+PGNpcmNsZSBjeD0iMTUuMDEiIGN5PSIxNC4xOSIgcj0iMC43NiIgc3R5bGU9ImZpbGw6IzQyODVmNCIvPjxjaXJjbGUgY3g9IjE1LjAxIiBjeT0iMTEuOTciIHI9IjAuNzYiIHN0eWxlPSJmaWxsOiM0Mjg1ZjQiLz48Y2lyY2xlIGN4PSI4Ljk5IiBjeT0iMTQuMTkiIHI9IjAuNzYiIHN0eWxlPSJmaWxsOiNhZWNiZmEiLz48Y2lyY2xlIGN4PSI4Ljk5IiBjeT0iNy45MiIgcj0iMC43NiIgc3R5bGU9ImZpbGw6I2FlY2JmYSIvPjxjaXJjbGUgY3g9IjguOTkiIGN5PSI1LjY5IiByPSIwLjc2IiBzdHlsZT0iZmlsbDojYWVjYmZhIi8+PHBhdGggZD0iTTksMTIuNzNBLjc2Ljc2LDAsMCwxLDguMjQsMTJWMTAuMWEuNzUuNzUsMCwxLDEsMS41LDBWMTJBLjc1Ljc1LDAsMCwxLDksMTIuNzNaIiBzdHlsZT0iZmlsbDojYWVjYmZhIi8+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Vertex AI Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            region = st.selectbox("Region", ["us-central1", "us-east1", "us-west1", "europe-west1", "europe-west4", "asia-northeast1", "asia-southeast1"])
            action = st.selectbox("Action", ["Create Notebook Instance", "Create Model Endpoint", "Create Dataset"])
            additional_input = f"Project ID: {project_id}\nRegion: {region}\nAction: {action}"

        elif service == "Cloud Monitoring":
            st.markdown("""<div style=\"display: flex; align-items: center; gap: 10px; margin-bottom: 15px;\"><img src=\"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNHB4IiBoZWlnaHQ9IjI0cHgiIHZpZXdCb3g9IjAgMCAyNCAyNCI+PGRlZnM+PHN0eWxlPi5jbHMtMXtmaWxsOiM2NjlkZjY7fS5jbHMtMntmaWxsOiM0Mjg1ZjQ7fTwvc3R5bGU+PC9kZWZzPjx0aXRsZT5JY29uXzI0cHhfTW9uaXRvcmluZ19Db2xvcjwvdGl0bGU+PGcgZGF0YS1uYW1lPSJQcm9kdWN0IEljb25zIj48cmVjdCBjbGFzcz0iY2xzLTEiIHg9IjEwLjgzIiB5PSIxNS44NCIgd2lkdGg9IjIuMzMiIGhlaWdodD0iMi42NCIvPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTE4LjQ4LDEzLjg3YS41Ni41NiwwLDAsMS0uNC0uMTdMMTQsOS40N2wtMi43NCwyLjg5YS41Ny41NywwLDAsMS0uNzYuMDVMOC40MiwxMC43M2wtMi4yLDIuOTJhLjU2LjU2LDAsMCwxLS40NS4yMkgydjEuNzFhLjc1Ljc1LDAsMCwwLC43NC43NUgyMS4yNmEuNzUuNzUsMCwwLDAsLjc0LS43NVYxMy44N1oiLz48cGF0aCBjbGFzcz0iY2xzLTEiIGQ9Ik01LjUsMTIuNzYsNy44OCw5LjZhLjU1LjU1LDAsMCwxLC4zNy0uMjIuNjMuNjMsMCwwLDEsLjQyLjEybDIuMTIsMS43MiwyLjgtMi45NGEuNTQuNTQsMCwwLDEsLjQtLjE3aDBhLjU0LjU0LDAsMCwxLC40LjE3bDQuMzMsNC40OEgyMlY2YS43NC43NCwwLDAsMC0uNzQtLjc0SDIuNzRBLjc0Ljc0LDAsMCwwLDIsNnY2LjgxWiIvPjxyZWN0IGNsYXNzPSJjbHMtMiIgeD0iOC42NyIgeT0iMTguMTgiIHdpZHRoPSI2LjY3IiBoZWlnaHQ9IjAuNjEiIHJ4PSIwLjMiLz48L2c+PC9zdmc+\" width=\"32\" height=\"32\"><h3 style=\"margin: 0;\">Cloud Monitoring Configuration</h3></div>""", unsafe_allow_html=True)
            project_id = st.text_input("Project ID", "my-gcp-project")
            workspace_name = st.text_input("Workspace Name", project_id)
            alert_policy = st.text_input("Alert Policy Name", "High CPU Alert")
            additional_input = f"Project ID: {project_id}\nWorkspace Name: {workspace_name}\nAlert Policy Name: {alert_policy}"

    # Remove Dry Run from the middle if preferred, but for now we keep the layout consistent.

    # --- Dry Run Toggle ---
    dry_run = st.toggle("🧪 Dry Run (Preview commands only — no deployment)", value=False,
                        help="When enabled, the pipeline will plan and validate but NOT execute any real cloud commands.")

    # --- Pre-flight Checklist ---
    if feature != "Select a Feature" and additional_input:
        with st.expander("🛫 Pre-flight Checklist", expanded=True):
            st.markdown("**Review before submitting:**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("✅ Feature selected: `{}`".format(feature))
                if service and service != "Select Service":
                    st.markdown("✅ Service: `{}`".format(service))
                if "us-central1" in additional_input or "europe-west1" in additional_input or "asia-northeast1" in additional_input:
                    st.markdown("✅ Region: policy-compliant")
                elif "Region" in additional_input:
                    st.markdown("⚠️  Verify region is in: `us-central1`, `europe-west1`, `asia-northeast1`")
            with col_b:
                if feature == "GCP Configuration":
                    st.markdown("⚠️  VM will get `--no-address` (no public IP)")
                    st.markdown("ℹ️  Image: `debian-11 / debian-cloud`")
                st.markdown("ℹ️  Session ID: `{}`".format(st.session_state.session_uid))

    github_button = st.button("🚀 Deploy via GitHub Actions", type="primary", use_container_width=True, key="deploy_gh_btn")

user_request = ""
if feature != "Select a Feature":
    if feature == "Agentic Development":
        internal_guidance = "Guide the development over several steps, including planning, design, implementation, and testing. Ensure to create complete and well-documented applications."
        user_request = f"Agentic Development:\n{additional_input}\n{internal_guidance}"
    elif feature == "Create Dockerfile":
        internal_guidance = "Ensure to include best practices for Dockerfile creation, such as minimizing layers, using a small base image, and cleaning up unnecessary files."
        user_request = f"Create a Dockerfile with options: {additional_input}. {internal_guidance}"
    elif feature == "Create Bash Script":
        internal_guidance = "The script should handle errors gracefully, use descriptive comments, and include execution permissions."
        user_request = f"Create a basic deployment script with details: {additional_input}. {internal_guidance}"
    elif feature == "Create Kubernetes Configuration":
        internal_guidance = "Ensure the configuration includes resource limits, readiness and liveness probes, and follows Kubernetes best practices."
        user_request = f"Create a Kubernetes config for a web application with details: {additional_input}. {internal_guidance}"
    elif feature == "Create CI/CD Pipeline":
        internal_guidance = "The GitHub Actions pipeline should include stages for building, testing, and deploying the application, with rollback support."
        user_request = f"Create a GitHub Actions CI/CD pipeline with details: {additional_input}. {internal_guidance}"
    elif feature == "Azure Configuration":
        internal_guidance = "Include detailed resource definitions, dependencies, and parameterized templates for flexibility."
        user_request = f"Create an Azure Resource Manager template for {service} with details: {additional_input}. {internal_guidance}"
    elif feature == "AWS Configuration":
        internal_guidance = "Ensure the template includes IAM roles and policies, and follows AWS best practices for security and scalability."
        user_request = f"Create a CloudFormation template for {service} with details: {additional_input}. {internal_guidance}"
    elif feature == "GCP Configuration":
        internal_guidance = "Draft standard gcloud CLI commands to create these resources. Do not use Deployment Manager or Terraform. Ensure all commands are valid and follow GCP best practices."
        user_request = f"Create the following GCP {service} via gcloud commands with details: {additional_input}. {internal_guidance}"

    if not user_request:
        st.warning("Please define your requirements first.")
        st.stop()

    if github_button:
        if not github_pat:
            st.error("\u26a0\ufe0f Please provide a GitHub Personal Access Token in the sidebar.")
            st.stop()

        st.toast("\U0001f4e4 Dispatching to GitHub Actions...", icon="\u2699\ufe0f")
        _count = int(st.session_state.get("vm_instance_count", 1))
        success, message = trigger_github_workflow(github_pat, github_repo, github_workflow, user_request, count=_count)
        if success:
            st.success(message)
            st.balloons()
        else:
            st.error(message)
        st.stop()

    # --- Save to history ---
    import datetime
    st.session_state.request_history.append({
        "feature": feature,
        "summary": user_request[:80] + "..." if len(user_request) > 80 else user_request,
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "status": "pending"
    })

    if dry_run:
        st.info("\U0001f9ea **Dry Run Mode** \u2014 No resources will be provisioned.")
        with st.expander("\U0001f4cb Request that would be sent to GitHub Actions:"):
            st.code(user_request, language="text")
        st.stop()
