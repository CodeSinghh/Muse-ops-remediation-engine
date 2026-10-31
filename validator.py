import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AIOps Validator - %(message)s')
logger = logging.getLogger(__name__)

def validate_and_save_patch(tf_code: str, rca_text: str, output_filename="remediation_patch.tf") -> bool:
    """
    Saves the extracted Terraform patch to disk and runs local syntax validation.
    """
    try:
        if not tf_code:
            logger.error("No terraform patch provided to validator.")
            return False

        # Save to disk
        with open(output_filename, "w") as tf_file:
            tf_file.write(tf_code)
        logger.info(f"Successfully saved Terraform patch to {output_filename}")

        # Print RCA report
        print("\n" + "="*50)
        print("💡 ROOT CAUSE ANALYSIS (RCA) REPORT:")
        print("="*50)
        print(rca_text)
        print("="*50 + "\n")

        # Run local Terraform validation checks
        logger.info("Running local Terraform validation checks...")
        subprocess.run(["terraform", "fmt", output_filename], capture_output=True, text=True)
        subprocess.run(["terraform", "init", "-backend=false"], capture_output=True, text=True)
        val_result = subprocess.run(["terraform", "validate"], capture_output=True, text=True)
        
        if val_result.returncode == 0:
            logger.info("✅ Terraform HCL syntax validation PASSED successfully!")
            return True
        else:
            logger.warning("⚠️ Terraform validation warning/error detected:")
            print(val_result.stderr)
            return False

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False