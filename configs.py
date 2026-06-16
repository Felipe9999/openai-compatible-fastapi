DB_NAME = "users.db"
SUPPORTED_DOMAINS = ["gmail.com", "protonmail.com"]
MASKED_API_KEY_LEN = 5

time_period = 60 # In Seconds
num_request = 2 # Number of request that a user can make in 60 seconds

import os
from dotenv import load_dotenv

load_dotenv()

PROVIDERS = {
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "blacklist": [],
    },
    "gemini": {
        "base_url": os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        "api_key": os.getenv("GEMINI_API_KEY", ""),
        "blacklist": os.getenv("GEMINI_BLACKLISTED_MODELS", "").split(',')
    }
}
