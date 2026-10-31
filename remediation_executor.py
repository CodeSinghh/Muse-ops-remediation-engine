import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RemediationExecutor")

def implement_fix(terraform_file: str = "remediation_patch.tf", auto_apply: bool = False) -> tuple[bool, str]:
    """
    Takes the generated .tf patch, runs formatting, initializes Terraform,
    generates an execution plan, and optionally applies the fix.
    """
    if not os.path.exists(terraform_file):
        logger.error(f"File {terraform_file} does not exist.")
        return False, f"File {terraform_file} not found."

    # Step 1: Format Terraform Code
    logger.info("Running `terraform fmt`...")
    subprocess.run(["terraform", "fmt", terraform_file], capture_output=True)

    # Step 2: Initialize Working Directory
    logger.info("Initializing Terraform (`terraform init`)...")
    init_proc = subprocess.run(["terraform", "init"], capture_output=True, text=True)
    if init_proc.returncode != 0:
        logger.error(f"Terraform init failed:\n{init_proc.stderr}")
        return False, f"Init failed: {init_proc.stderr.strip()}"

    # Step 3: Generate Execution Plan
    logger.info("Generating plan (`terraform plan`)...")
    plan_proc = subprocess.run(["terraform", "plan", "-out=tfplan"], capture_output=True, text=True)
    if plan_proc.returncode != 0:
        logger.error(f"Terraform plan failed:\n{plan_proc.stderr}")
        return False, f"Plan failed: {plan_proc.stderr.strip()}"

    logger.info("Plan created successfully (`tfplan`).")

    # Step 4: Apply Patch (If Auto-Apply Enabled)
    if auto_apply:
        logger.info("Auto-applying remediation patch (`terraform apply`)...")
        apply_proc = subprocess.run(["terraform", "apply", "-auto-approve", "tfplan"], capture_output=True, text=True)
        if apply_proc.returncode == 0:
            logger.info("Fix applied successfully!")
            return True, "Remediation patch applied to live environment."
        else:
            logger.error(f"Terraform apply failed:\n{apply_proc.stderr}")
            return False, f"Apply failed: {apply_proc.stderr.strip()}"
    else:
        logger.info("Auto-apply disabled. Execution plan staged in `tfplan`.")
        return True, "Fix validated and plan staged successfully (`tfplan`)."
        