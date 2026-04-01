"""
ui_policy_defaults.py
─────────────────────
Thin helper that reads VM_POLICY and returns a pre-filled parameter dict
for the AI Assistant's Policy Preview panel in app.py.

Editable vs. locked classification mirrors what the Governance Agent enforces:
  - Locked  → any change would cause a policy rejection
  - Editable → user may override within the allowed range
"""

from policies.vm_policy import VM_POLICY


def get_vm_defaults(env: str = "dev", service: str = "myservice") -> dict:
    """Return default VM parameters for the given env + service name."""
    env = env.lower().strip()
    service = service.lower().strip().replace(" ", "-")

    # Pick policy defaults
    allowed_zones = VM_POLICY["allowed_zones"]
    machine_types_for_env = VM_POLICY["machine_types"].get(env, VM_POLICY["machine_types"]["dev"])
    disk = VM_POLICY["disk"]
    os_img = VM_POLICY["os_image"]

    return {
        # ── Editable fields ─────────────────────────────────────────────────
        "instance_name":   f"proj-{env}-{service}-vm",
        "zone":            allowed_zones[0],          # us-east1-d (first allowed)
        "machine_type":    machine_types_for_env[0],  # first allowed for env tier
        "disk_size_gb":    disk["default_boot_disk_size_gb"],
        "disk_type":       disk["boot_disk_type"],
        "instance_count":  1,

        # ── Locked fields (policy-enforced, read-only in the UI) ────────────
        "image_family":    os_img["required_family"],   # debian-12
        "image_project":   os_img["required_project"],  # debian-cloud
        "no_address":      True,    # --no-address required by policy
        "os_login":        True,    # --metadata=enable-oslogin=TRUE required
        "label_env":       env,
        "label_service":   service,
        "label_managed_by": "autoinfra",   # always autoinfra

        # ── Metadata: allowed ranges for editable fields ─────────────────────
        "_allowed_zones":        VM_POLICY["allowed_zones"],
        "_allowed_machine_types": VM_POLICY["machine_types"].get(
            env, VM_POLICY["machine_types"]["dev"]
        ),
        "_allowed_disk_types":    disk["allowed_boot_disk_types"],
        "_min_disk_gb":           disk["min_boot_disk_size_gb"],
        "_max_disk_gb":           disk["max_boot_disk_size_gb"],
        "_env":                   env,
        "_service":               service,
    }


def build_vm_request_string(params: dict) -> str:
    """
    Build the natural-language request string sent to main.py / GitHub Actions.
    Includes all editable overrides and explicitly calls out policy-locked values
    so the Planner agent has zero ambiguity.
    """
    env        = params["_env"]
    service    = params["_service"]
    name       = params["instance_name"]
    zone       = params["zone"]
    mtype      = params["machine_type"]
    disk_size  = params["disk_size_gb"]
    disk_type  = params["disk_type"]
    count      = params["instance_count"]
    img_family = params["image_family"]
    img_proj   = params["image_project"]

    return (
        f"Create a GCP Compute Engine VM with the following specification:\n"
        f"  Environment      : {env}\n"
        f"  Service          : {service}\n"
        f"  Instance Name    : {name}\n"
        f"  Zone             : {zone}\n"
        f"  Machine Type     : {mtype}\n"
        f"  Boot Disk Size   : {disk_size}GB\n"
        f"  Boot Disk Type   : {disk_type}\n"
        f"  Image Family     : {img_family}\n"
        f"  Image Project    : {img_proj}\n"
        f"  No Public IP     : true (--no-address)\n"
        f"  OS Login         : true (--metadata=enable-oslogin=TRUE)\n"
        f"  Labels           : env={env},service={service},managed-by=autoinfra\n"
        f"  Number of VMs    : {count}\n"
    )
