"""
Cloud VM (Compute Engine) — Service-Specific Governance Policy
==============================================================

This module defines the full governance policy for GCP Compute Engine VM
provisioning. It is exposed as an MCP tool via mcp_server.py.

Policy areas:
  - Naming convention
  - Allowed machine types (by environment tier)
  - Required & allowed regions
  - OS image standards
  - Network / security rules (no public IP, OS login, Shielded VM)
  - Disk policy (type, size limits)
  - Startup/shutdown script rules
  - Required metadata labels/tags
  - Required API enablement
  - Allowed deletion behaviour
  - Common rejection reasons with remediation hints
"""

VM_POLICY = {
    #
    # ── NAMING ────────────────────────────────────────────────────────────────
    #
    "naming": {
        "convention": "proj-[env]-[service]-vm (or proj-[env]-[service]-vm-[N] for parallel provisioning)",
        "pattern_regex": r"^proj-(dev|stag|prod)-[a-z0-9\-]+-vm(-\d+)?$",
        "max_length": 63,
        "examples": {
            "dev":               "proj-dev-payments-vm",
            "dev_parallel":     "proj-dev-payments-vm-1, proj-dev-payments-vm-2",
            "stag":             "proj-stag-inventory-vm",
            "prod":             "proj-prod-api-vm",
        },
        "rejection_examples": [
            "python-app-vm               → REJECTED: missing 'proj-[env]-' prefix",
            "proj-dev-VM                 → REJECTED: uppercase letters not allowed",
            "vm-dev-payments             → REJECTED: wrong prefix order",
            "proj-dev-payments-vm-abc    → REJECTED: suffix must be numeric only",
        ],
        "parallel_suffix_note": (
            "When INSTANCE_COUNT > 1, the system automatically appends a numeric suffix "
            "(e.g. -1, -2) to make resource names unique across parallel runs. "
            "APPROVE names ending in -vm-<number>. Do NOT reject them."
        ),
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
    "allowed_zones": [
        "us-central1-a", "us-central1-b", "us-central1-c",
        "us-east1-b", "us-east1-c", "us-east1-d",
    ],

    #
    # ── MACHINE TYPES (tiered by env) ─────────────────────────────────────────
    #
    "machine_types": {
        "dev":  ["e2-micro", "e2-small", "e2-medium"],
        "stag": ["e2-medium", "n1-standard-1", "n1-standard-2"],
        "prod": ["n1-standard-1", "n1-standard-2", "n1-standard-4", "n2-standard-2"],
        "all_allowed": ["e2-micro", "e2-small", "e2-medium",
                        "n1-standard-1", "n1-standard-2", "n1-standard-4",
                        "n2-standard-2"],
    },

    #
    # ── OS IMAGE ──────────────────────────────────────────────────────────────
    #
    "os_image": {
        "required_family": "debian-11",
        "required_project": "debian-cloud",
        "allowed_families": ["debian-11", "debian-12", "ubuntu-2204-lts"],
        "gcloud_flag": "--image-family=debian-11 --image-project=debian-cloud",
        "rejection_reason": "Custom or Windows images are not approved.",
    },

    #
    # ── NETWORKING / SECURITY ─────────────────────────────────────────────────
    #
    "network_security": {
        "allow_public_ip": False,
        "required_flag": "--no-address",
        "rejection_reason": (
            "VMs MUST NOT have a public IP. Always include --no-address. "
            "Use Cloud NAT or IAP tunnel for external connectivity."
        ),
        "os_login_required": True,
        "os_login_flag": "--metadata=enable-oslogin=TRUE",
        "shielded_vm_required": False,   # recommended but not enforced
        "vpc_network": "default",        # or specify a project-managed VPC
    },

    #
    # ── DISK POLICY ───────────────────────────────────────────────────────────
    #
    "disk": {
        "boot_disk_type": "pd-balanced",
        "allowed_boot_disk_types": ["pd-balanced", "pd-ssd", "pd-standard"],
        "min_boot_disk_size_gb": 20,
        "max_boot_disk_size_gb": 200,
        "default_boot_disk_size_gb": 50,
        "auto_delete_on_instance_delete": True,
    },

    #
    # ── REQUIRED LABELS / TAGS ────────────────────────────────────────────────
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
        "compute.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "iam.googleapis.com",
    ],
    "api_enable_command": (
        "gcloud services enable compute.googleapis.com "
        "cloudresourcemanager.googleapis.com iam.googleapis.com"
    ),

    #
    # ── VALID GCLOUD COMMAND TEMPLATE ─────────────────────────────────────────
    #
    "gcloud_template": (
        "gcloud compute instances create proj-[env]-[service]-vm \\\n"
        "  --project=[PROJECT_ID] \\\n"
        "  --zone=[ZONE] \\\n"
        "  --machine-type=[MACHINE_TYPE] \\\n"
        "  --image-family=debian-11 \\\n"
        "  --image-project=debian-cloud \\\n"
        "  --boot-disk-size=50GB \\\n"
        "  --boot-disk-type=pd-balanced \\\n"
        "  --no-address \\\n"
        "  --metadata=enable-oslogin=TRUE \\\n"
        "  --labels=env=[ENV],service=[SERVICE],managed-by=autoinfra"
    ),

    #
    # ── DELETION POLICY ───────────────────────────────────────────────────────
    #
    "deletion": {
        "require_resource_exists_check": True,
        "gcloud_delete_template": (
            "gcloud compute instances delete proj-[env]-[service]-vm "
            "--zone=[ZONE] --project=[PROJECT_ID] --quiet"
        ),
    },

    #
    # ── COMMON REJECTION REASONS ──────────────────────────────────────────────
    #
    "common_rejections": [
        {
            "reason": "Missing --no-address flag",
            "fix": "Add --no-address to the gcloud command.",
        },
        {
            "reason": "Instance name does not match proj-[env]-[service]-vm pattern",
            "fix": "Rename to e.g. proj-dev-payments-vm. Note: proj-dev-payments-vm-1 is APPROVED for parallel provisioning runs.",
        },
        {
            "reason": "Machine type not in allowed list",
            "fix": "Use one of: e2-micro, e2-small, e2-medium, n1-standard-1.",
        },
        {
            "reason": "Region not in allowed list",
            "fix": "Strict Policy Enforcement: You must use us-east1.",
        },
        {
            "reason": "Image family not approved (e.g. windows-server)",
            "fix": "Use --image-family=debian-11 --image-project=debian-cloud.",
        },
        {
            "reason": "Missing required labels",
            "fix": "Add --labels=env=[env],service=[svc],managed-by=autoinfra.",
        },
        {
            "reason": "API not enabled",
            "fix": "Run: gcloud services enable compute.googleapis.com",
        },
    ],
}
