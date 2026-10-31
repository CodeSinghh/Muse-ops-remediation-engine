import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AIOps Normalizer - %(message)s')
logger = logging.getLogger(__name__)

def clean_and_normalize_output(raw_text: str) -> dict:
    """
    Parses the exact JSON structure returned by Baseten.
    """
    if not raw_text:
        logger.error("Raw text is empty.")
        return {"rca": "", "terraform_patch": ""}

    cleaned = raw_text.replace('\xa0', ' ').strip()

    # Strip markdown code blocks if the model wrapped it anyway
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        cleaned = cleaned.strip()

    try:
        # Standard parse with strict=False to handle any minor control formatting
        data = json.loads(cleaned, strict=False)
        return {
            "rca": data.get("rca", "No RCA provided"),
            "terraform_patch": data.get("terraform_patch", "")
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        return {"rca": "", "terraform_patch": ""}