import os
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(project_root, '.env'))

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
STAFF_ACCESS_CODE = os.getenv("STAFF_ACCESS_CODE")

if not all([LLM_BASE_URL, LLM_API_KEY, LLM_MODEL]):
    raise ValueError(
        "Missing LLM configuration. Please ensure LLM_BASE_URL, LLM_API_KEY, "
        "and LLM_MODEL are set in your .env file."
    )
