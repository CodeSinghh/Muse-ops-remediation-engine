import re
import json
import logging

# Setup basic logging for the agent
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AIOps Parser - %(message)s')
logger = logging.getLogger(__name__)

def parse_log_stream(log_file_path):
    """
    Optimized parser: Reads raw log files, filters for critical events, 
    and returns structured JSON context. Keeps token usage low.
    """
    critical_patterns = [
        r"\bERROR\b", r"\bFATAL\b", r"\bCRITICAL\b",  # Severity Keywords
        r"OOMKilled", r"CrashLoopBackOff",             # Kubernetes specifics
        r"java\.lang\.\w*Error", r"AttributeError",    # Stack Trace Indicators
        r"AccessDenied", r"Timeout"                    # Permission/Network
    ]
    
    combined_regex = re.compile("|".join(critical_patterns), re.IGNORECASE)
    extracted_events = []
    
    logger.info(f"Parsing logs from: {log_file_path}")
    
    try:
        with open(log_file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                clean_line = line.strip()
                if not clean_line: continue # Skip empty lines

                # Apply regex filter
                if combined_regex.search(clean_line):
                    extracted_events.append({
                        "id": f"evt_{line_num}",
                        "raw_timestamp": clean_line[:20],
                        "raw_log": clean_line
                    })
                    
        logger.info(f"Extraction complete. {len(extracted_events)} high-signal events found.")
        return extracted_events

    except FileNotFoundError:
        logger.error(f"File not found: {log_file_path}")
        return []
    except Exception as e:
        logger.error(f"Unexpected parsing error: {e}")
        return []

if __name__ == "__main__":
    # Test the parser against our sample log file
    events = parse_log_stream("payment-api-oom-crashloop.log")
    print("\n--- Structured JSON Output from Parser ---")
    print(json.dumps(events, indent=2))