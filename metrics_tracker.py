import os
import json

METRICS_FILE = ".metrics_log.json"

# Pricing per 1M tokens
COST_PER_MILLION_PROMPT = 0.15
COST_PER_MILLION_COMPLETION = 0.60

def record_api_call(prompt_tokens, completion_tokens, model_name="meta-models/muse-spark-open-1026"):
    """Records token usage and calculates accumulated cost to a local json file."""
    data = {
        "total_calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost": 0.0,
        "model": model_name
    }
    
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            pass

    data["total_calls"] += 1
    data["prompt_tokens"] += prompt_tokens
    data["completion_tokens"] += completion_tokens
    data["total_tokens"] = data["prompt_tokens"] + data["completion_tokens"]
    data["model"] = model_name

    prompt_cost = (prompt_tokens / 1_000_000) * COST_PER_MILLION_PROMPT
    completion_cost = (completion_tokens / 1_000_000) * COST_PER_MILLION_COMPLETION
    data["cost"] = round(data.get("cost", 0.0) + prompt_cost + completion_cost, 6)

    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_total_metrics():
    """Reads accumulated metrics."""
    if not os.path.exists(METRICS_FILE):
        return {
            "total_calls": 0, 
            "prompt_tokens": 0, 
            "completion_tokens": 0, 
            "total_tokens": 0,
            "cost": 0.000000,
            "model": "meta-models/muse-spark-open-1026"
        }
    
    try:
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "total_calls": 0, 
            "prompt_tokens": 0, 
            "completion_tokens": 0, 
            "total_tokens": 0,
            "cost": 0.000000,
            "model": "meta-models/muse-spark-open-1026"
        }