import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
from metrics_tracker import record_api_call

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AIOps Agent - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(
    base_url="https://inference.baseten.co/v1",
    api_key=os.environ.get("BASETEN_API_KEY")
)

SYSTEM_PROMPT = """
You are an expert Autonomous AIOps & Cloud Infrastructure Remediation Agent.
Given a list of parsed crash logs and failure events:
1. Provide a concise Root Cause Analysis (RCA).
2. Generate valid, production-ready Terraform (HCL) resource configuration or patch to fix the infrastructure deficit.
3. Output your response STRICTLY as a valid JSON object using double quotes for all keys and string values. 
Do NOT use single quotes. Do NOT use Python assignments (=). 
The JSON must have exactly two keys: "rca" and "terraform_patch".
Example format:
{
  "rca": "Your RCA explanation here",
  "terraform_patch": "resource \\"kubernetes_deployment\\" \\"example\\" { ... }"
}
"""

def generate_remediation(log_file_path):
    from parser import parse_log_stream
    events = parse_log_stream(log_file_path)
    if not events:
        logger.warning("No events to process.")
        return None

    prompt_input = f"Log Events to Analyze:\n{json.dumps(events, indent=2)}"
    
    logger.info("Sending payload to Baseten model endpoint...")
    
    try:
        response = client.chat.completions.create(
            model="meta-models/muse-spark-open-1026",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_input}
            ],
            temperature=0.0
        )
        
        if hasattr(response, 'usage') and response.usage:
            p_tok = response.usage.prompt_tokens
            c_tok = response.usage.completion_tokens
            t_tok = response.usage.total_tokens
            record_api_call(p_tok, c_tok)
            logger.info(f"📊 LIVE API METRICS | Prompt: {p_tok} | Completion: {c_tok} | Total: {t_tok}")

        result_content = response.choices[0].message.content
        return result_content

    except Exception as e:
        logger.error(f"Error during Baseten API call: {e}")
        return None