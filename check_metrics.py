import os
import time
import logging
from dotenv import load_dotenv
from openai import OpenAI
from metrics_tracker import record_api_call, get_total_metrics

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AIOps Metrics - %(message)s')
logger = logging.getLogger(__name__)

def run_quick_probe():
    api_key = os.environ.get("BASETEN_API_KEY")
    if not api_key:
        logger.error("❌ BASETEN_API_KEY not found in environment!")
        return

    client = OpenAI(
        base_url="[https://inference.baseten.co/v1](https://inference.baseten.co/v1)",
        api_key=api_key
    )

    print("\n" + "="*55)
    print("🔍 BASETEN ENDPOINT & TOKEN DIAGNOSTIC PROBE")
    print("="*55)
    
    logger.info("Sending diagnostic probe to Baseten...")
    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="meta-models/muse-spark-open-1026",
            messages=[
                {"role": "system", "content": "Respond with 'OK' only."},
                {"role": "user", "content": "Ping."}
            ],
            max_tokens=10,
            temperature=0.0
        )
        latency = round(time.time() - start_time, 2)
        
        usage = response.usage
        if usage:
            # Record probe tokens into total metrics as well
            record_api_call(usage.prompt_tokens, usage.completion_tokens)

        print(f"\n✅ Endpoint Status      : ACTIVE (HTTP 200)")
        print(f"⏱️ API Roundtrip Time  : {latency} seconds")
        print(f"📥 Probe Prompt Tokens : {usage.prompt_tokens if usage else 0}")
        print(f"📤 Probe Output Tokens : {usage.completion_tokens if usage else 0}")

    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return

    # Fetch live accumulated stats
    metrics = get_total_metrics()
    total_calls = metrics["total_calls"]
    total_tokens = metrics["total_tokens"]

    # Estimated cost (~$0.0006 per 1k tokens)
    est_dollars_spent = (total_tokens / 1000) * 0.0006
    remaining_grant = 100.00 - est_dollars_spent

    print("\n" + "="*55)
    print("💰 DYNAMIC LIVE CONSUMPTION SUMMARY")
    print("="*55)
    print(f"🔢 Total API Calls Executed     : {total_calls}")
    print(f"📥 Accumulated Prompt Tokens   : {metrics['prompt_tokens']:,}")
    print(f"📤 Accumulated Output Tokens   : {metrics['completion_tokens']:,}")
    print(f"🧮 Total Tokens Consumed        : {total_tokens:,} tokens")
    print(f"💵 Total Dollars Spent          : ${est_dollars_spent:.6f} USD")
    print(f"💳 Remaining Baseten Balance    : ${remaining_grant:.2f} / $100.00 USD")
    print("="*55 + "\n")

if __name__ == "__main__":
    run_quick_probe()