from dotenv import load_dotenv
import os

load_dotenv()

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("Missing Anthropic API key")

max_tokens=4096
claude_model="claude-sonnet-4-6"

database_name = "database.db"
db_path = f"sqlite:///{database_name}"