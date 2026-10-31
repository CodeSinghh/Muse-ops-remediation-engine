import logging
from parser import parse_log_stream
from agent import generate_remediation
from normalizer import clean_and_normalize_output
from validator import validate_and_save_patch
from remediation_executor import implement_fix
from metrics_tracker import get_total_metrics

# Fixed logging format string (added separator before message)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - AIOps Pipeline - %(message)s")

def run_pipeline():
    print("\n" + "=" * 60)
    print("🚀 AIOPS AUTONOMOUS REMEDIATION PIPELINE (V2)")
    print("=" * 60)

    # 1. Parse high-signal events
    log_file = "sample_logs.log"
    print(f"\n[1/4] Parsing logs from {log_file}...")
    log_data = parse_log_stream(log_file)
    print(f"    Extracted {len(log_data)} log entries.")

    # 2. Query Baseten
    print("\n[2/4] Querying Baseten (meta-models/muse-spark-open-1026)...")
    raw_output = generate_remediation(log_file)
    
    if not raw_output:
        print("❌ Failed to receive response from Baseten.")
        return

    # Normalize raw model output into structured dictionary
    parsed_data = clean_and_normalize_output(raw_output)
    rca = parsed_data.get("rca", "No RCA provided")
    tf_code = parsed_data.get("terraform_patch", "")

    if not tf_code:
        print("❌ Normalizer failed to extract terraform patch.")
        return

    print(f"\n📌 Root Cause Analysis (RCA):\n{rca}")

    # 3. Validate HCL Syntax & Save Patch
    print("\n[3/4] Validating Terraform HCL syntax...")
    tf_file = "remediation_patch.tf"
    is_valid = validate_and_save_patch(tf_code, rca, output_filename=tf_file)
    
    if not is_valid:
        print("❌ Validation Failed.")
        return

    # ============================================================
    # HUMAN-IN-THE-LOOP SAFETY GATE (Interactive Terminal Pause)
    # ============================================================
    print("\n🛑 [Stage 3] Pipeline paused at Human-In-The-Loop safety gate.")
    print("   -> Policy check: Auto-apply is disabled for production environments.")
    print(f"   -> Review '{tf_file}' for memory limit adjustments.")

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

    # 4. Implement Fix
    print("[4/4] Executing Fix Engine (`implement_fix`)...")
    success, fix_msg = implement_fix(terraform_file=tf_file, auto_apply=False)
    print(f"    Result: {fix_msg}")

    # Telemetry Output
    print("\n" + "=" * 60)
    metrics = get_total_metrics()
    print(f"📊 Telemetry: {metrics.get('total_tokens', 0):,} tokens consumed | ${metrics.get('total_cost_usd', 0.0):.6f} USD spent across {metrics.get('total_calls', 0)} calls")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    print("Initializing AIOps Autonomous Remediation Engine...")
    run_pipeline()