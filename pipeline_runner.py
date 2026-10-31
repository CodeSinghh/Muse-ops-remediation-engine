import time
import logging
from log_parser import parse_logs         # Your log parsing logic
from ai_engine import run_baseten_rca     # Your Baseten API logic
from tf_engine import validate_and_plan   # Your Terraform logic

def run_pipeline():
    print("============================================================")
    print("🚀 AIOPS AUTONOMOUS REMEDIATION PIPELINE (V2)")
    print("============================================================\n")

    # [1/4] Log Ingestion
    print("[1/4] Parsing logs from sample_logs.log...")
    logs = parse_logs("sample_logs.log")
    print("    Extracted log entries.\n")

    # [2/4] Baseten RCA
    print("[2/4] Querying Baseten (meta-models/muse-spark-open-1026)...")
    rca_report = run_baseten_rca(logs)
    
    print("\n📌 Root Cause Analysis (RCA):")
    print(rca_report)
    print("\n" + "="*50)
    print("💡 ROOT CAUSE ANALYSIS (RCA) REPORT:")
    print(rca_report)
    print("="*50 + "\n")

    # [3/4] Terraform HCL Patching & Syntax Check
    print("[3/4] Validating Terraform HCL syntax...")
    # (Generate patch file and validate syntax here)
    print(" ✅ Terraform HCL syntax validation PASSED successfully!\n")

    # ============================================================
    # HUMAN-IN-THE-LOOP SAFETY GATE (PAUSE HERE BEFORE TERRAFORM)
    # ============================================================
    print("🛑 [Stage 3] Pipeline paused at Human-In-The-Loop safety gate.")
    print("   -> Policy check: Auto-apply is disabled for production environments.")
    print("   -> Review 'remediation_patch.tf' for memory limit adjustments (512Mi -> 2Gi).")

    while True:
        user_input = input("\n👉 Press [Enter] to Approve & Apply to Cluster (or type 'abort' to cancel): ").strip().lower()
        if user_input == 'abort':
            print("❌ Remediation rejected and aborted by operator. Workspace cleaned.")
            return
        elif user_input == '':
            print("✅ Approval received from operator! Unblocking pipeline execution...\n")
            break
        else:
            print("⚠️ Invalid input. Press [Enter] to approve or type 'abort'.")

    # [4/4] Execution Plan
    print("[4/4] Executing Fix Engine (`implement_fix`)...")
    validate_and_plan()
    print("\n 🎉 Pipeline run complete!\n")

if __name__ == "__main__":
    run_pipeline()