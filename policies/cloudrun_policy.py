"""
Cloud Run — Service-Specific Governance Policy
===============================================

This module defines the full governance policy for GCP Cloud Run service
provisioning. It is exposed as an MCP tool via mcp_server.py.

Policy areas:
  - Naming convention
  - Allowed regions
  - Container image rules
  - CPU & memory limits (by environment tier)
  - Concurrency & scaling limits
  - Authentication / ingress rules
  - Required labels
  - Required API enablement
  - Valid gcloud command template
  - Deletion policy
  - Common rejection reasons with remediation hints
"""

CLOUDRUN_POLICY = {
    #
    # ── NAMING ────────────────────────────────────────────────────────────────
    #
    "naming": {
        "convention": "proj-[env]-[service]-cloudrun",
        "pattern_regex": r"^proj-(dev|stag|prod)-[a-z0-9\-]+-cloudrun$",
        "max_length": 49,   # Cloud Run service name limit
        "examples": {
            "dev":  "proj-dev-payments-cloudrun",
            "stag": "proj-stag-inventory-cloudrun",
            "prod": "proj-prod-api-cloudrun",
        },
        "rejection_examples": [
            "payments-service          → REJECTED: missing 'proj-[env]-' prefix",
            "proj-dev-PAYMENTS-cloudrun → REJECTED: uppercase letters not allowed",
            "proj-dev-payments-run     → REJECTED: must end with '-cloudrun'",
        ],
    },

    #
    # ── ENVIRONMENTS ──────────────────────────────────────────────────────────
    #
    "allowed_environments": ["dev", "stag", "prod"],

    #
    # ── REGIONS ───────────────────────────────────────────────────────────────
    #
    "allowed_regions": [
        "us-central1",
        "us-east1",
    ],

    #
    # ── CONTAINER IMAGE ───────────────────────────────────────────────────────
    #
    "container_image": {
        "approved_registries": [
            "gcr.io",
            "us-docker.pkg.dev",
            "us-central1-docker.pkg.dev",
            "us-east1-docker.pkg.dev",
        ],
        "approved_public_images": [
            "gcr.io/google-samples/hello-app:1.0",
            "gcr.io/cloudrun/hello",
        ],
        "rejection_reason": (
            "Container images must be pulled from an approved GCP Artifact Registry "
            "or GCR project. Public DockerHub images are not permitted in prod/stag."
        ),
        "dev_exception": "Dev environments may use approved public images for testing only.",
    },

    #
    # ── CPU & MEMORY LIMITS (tiered by env) ───────────────────────────────────
    #
    "resources": {
        "dev": {
            "cpu":    "1",
            "memory": "512Mi",
            "allowed_cpu":    ["1", "2"],
            "allowed_memory": ["256Mi", "512Mi", "1Gi"],
        },
        "stag": {
            "cpu":    "1",
            "memory": "1Gi",
            "allowed_cpu":    ["1", "2"],
            "allowed_memory": ["512Mi", "1Gi", "2Gi"],
        },
        "prod": {
            "cpu":    "2",
            "memory": "2Gi",
            "allowed_cpu":    ["1", "2", "4"],
            "allowed_memory": ["1Gi", "2Gi", "4Gi", "8Gi"],
        },
    },

    #
    # ── CONCURRENCY & SCALING ─────────────────────────────────────────────────
    #
    "scaling": {
        "max_concurrency":         80,     # requests per container instance
        "min_instances": {
            "dev":  0,      # scale to zero allowed in dev
            "stag": 0,
            "prod": 1,      # always-warm in prod to avoid cold starts
        },
        "max_instances": {
            "dev":  5,
            "stag": 10,
            "prod": 100,
        },
    },

    #
    # ── AUTHENTICATION / INGRESS ──────────────────────────────────────────────
    #
    "authentication": {
        "allow_unauthenticated": True,
        "note": (
            "Unauthenticated access is allowed by default for public-facing services. "
            "Internal services should use --no-allow-unauthenticated and set --ingress=internal."
        ),
        "ingress_options": ["all", "internal", "internal-and-cloud-load-balancing"],
        "default_ingress": "all",
        "internal_services_ingress": "internal",
    },

    #
    # ── REQUIRED LABELS ───────────────────────────────────────────────────────
    #
    "required_labels": {
        "env":        "Deployment environment (dev | stag | prod)",
        "service":    "Service name, e.g. 'payments'",
        "managed-by": "Always set to 'autoinfra'",
    },
    "gcloud_labels_example": (
        "--labels=env=dev,service=payments,managed-by=autoinfra"
    ),

    #
    # ── REQUIRED API ENABLEMENT ───────────────────────────────────────────────
    #
    "required_apis": [
        "run.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com",
        "artifactregistry.googleapis.com",
    ],
    "api_enable_command": (
        "gcloud services enable run.googleapis.com "
        "cloudresourcemanager.googleapis.com "
        "iam.googleapis.com "
        "artifactregistry.googleapis.com"
    ),

    #
    # ── VALID GCLOUD COMMAND TEMPLATE ─────────────────────────────────────────
    #
    "gcloud_template": (
        "gcloud run deploy proj-[env]-[service]-cloudrun \\\n"
        "  --project=gen-lang-client-0436480880 \\\n"
        "  --region=us-east1 \\\n"
        "  --image=[APPROVED_IMAGE] \\\n"
        "  --cpu=[CPU] \\\n"
        "  --memory=[MEMORY] \\\n"
        "  --max-instances=[MAX_INSTANCES] \\\n"
        "  --min-instances=[MIN_INSTANCES] \\\n"
        "  --concurrency=80 \\\n"
        "  --allow-unauthenticated \\\n"
        "  --labels=env=[ENV],service=[SERVICE],managed-by=autoinfra \\\n"
        "  --platform=managed"
    ),

    #
    # ── DELETION POLICY ───────────────────────────────────────────────────────
    #
    "deletion": {
        "require_resource_exists_check": True,
        "gcloud_delete_template": (
            "gcloud run services delete proj-[env]-[service]-cloudrun "
            "--region=[REGION] --project=[PROJECT_ID] --quiet"
        ),
    },

    #
    # ── COMMON REJECTION REASONS ──────────────────────────────────────────────
    #
    "common_rejections": [
        {
            "reason": "Service name does not match proj-[env]-[service]-cloudrun pattern",
            "fix": "Rename to e.g. proj-dev-payments-cloudrun.",
        },
        {
            "reason": "Region not in allowed list",
            "fix": "Use us-east1 or us-central1.",
        },
        {
            "reason": "Container image from unapproved registry (e.g. DockerHub)",
            "fix": "Push image to GCR or Artifact Registry first: gcr.io/[PROJECT_ID]/[IMAGE]",
        },
        {
            "reason": "CPU or memory exceeds env tier limit",
            "fix": "Check CLOUDRUN_POLICY['resources'][env] for allowed values.",
        },
        {
            "reason": "Max instances exceeds policy limit for environment",
            "fix": "dev ≤ 5, stag ≤ 10, prod ≤ 100.",
        },
        {
            "reason": "Missing required labels",
            "fix": "Add --labels=env=[env],service=[svc],managed-by=autoinfra.",
        },
        {
            "reason": "Cloud Run API not enabled",
            "fix": "Run: gcloud services enable run.googleapis.com",
        },
    ],
}
