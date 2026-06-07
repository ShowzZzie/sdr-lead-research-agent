from dotenv import load_dotenv
import os
import logging
from pythonjsonlogger.json import JsonFormatter

load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("Missing Anthropic API key")

max_tokens=8192
claude_model="claude-sonnet-4-6"

database_name = "database.db"
db_path = f"sqlite:///{database_name}"

logger = logging.getLogger()
logging.getLogger("httpx").setLevel(logging.WARNING)

log_handler = logging.StreamHandler()
formatter = JsonFormatter()
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)