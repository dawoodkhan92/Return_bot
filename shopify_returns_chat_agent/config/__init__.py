"""Load environment variables for the chat agent.

Usage:
    from config import SHOPIFY_ADMIN_TOKEN, SHOPIFY_STORE_DOMAIN, OPENAI_API_KEY
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Locate .env (or env.example renamed) two levels up from this file
_base_dir = Path(__file__).resolve().parent.parent
_load_path = _base_dir / ".env"
if _load_path.exists():
    load_dotenv(_load_path)
else:
    # Fallback to env.example so developers see which vars are missing
    example_path = _base_dir / "env.example"
    if example_path.exists():
        load_dotenv(example_path)

SHOPIFY_ADMIN_TOKEN: str | None = os.getenv("SHOPIFY_ADMIN_TOKEN")
SHOPIFY_STORE_DOMAIN: str | None = os.getenv("SHOPIFY_STORE_DOMAIN")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

required_missing = []
for var in ("SHOPIFY_ADMIN_TOKEN", "SHOPIFY_STORE_DOMAIN"):
    if os.getenv(var) in (None, "", "put_your_token_here"):
        required_missing.append(var)

if required_missing:
    missing_str = ", ".join(required_missing)
    raise RuntimeError(
        f"Missing required environment variables: {missing_str}.\n"
        "Create a .env file (copy env.example) and fill in the values."
    ) 