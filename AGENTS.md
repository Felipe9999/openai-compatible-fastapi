# Agent Instructions

## Architecture & Entrypoints
This repository consists of two separate processes that must run concurrently:
- **Frontend (Auth & API Key Management):** Streamlit app.
  - Entrypoint: `app.py`
  - Command: `streamlit run app.py`
- **Backend (LLM Proxy API):** FastAPI server acting as a unified proxy to local (Ollama) and cloud (Gemini) LLMs.
  - Entrypoint: `serving.py`
  - Command: `uvicorn serving:app --reload --port 8000`

## Dependencies & Environment
- **Authentication:** The Streamlit app uses a local database for email and password authentication. No external credentials are required for login.
- **Database:** State (users, API keys) is stored locally in `users.db` (SQLite).
- **Backend Providers:** The backend no longer uses vLLM. Instead, it relies on a local Ollama instance (default port 11434) and cloud providers like Gemini.
- **Environment Variables:** API keys and provider URLs are loaded from a `.env` file (e.g., `GEMINI_API_KEY`, `OLLAMA_BASE_URL`). Ensure this file is present.

## Development Quirks
- **Rate Limiting:** The `@rate_limit()` decorator on the `/v1/models` and `/v1/chat/completions` endpoints in `serving.py` is currently commented out for development/testing purposes.
- **Testing:** `testing_api.py` contains a hardcoded script to verify the OpenAI-compatible endpoint using the official `openai` Python client.
- **Model Routing:** Models are requested with a prefix corresponding to their provider (e.g., `ollama/llama3` or `gemini/gemini-1.5-pro`). The backend parses this prefix to proxy the request via `httpx` to the correct service.

## Key Files & Directories
- `configs.py`: Contains global settings like rate limiting thresholds, DB naming, and `PROVIDERS` configurations (loading secrets via `python-dotenv`).
- `providers/`: Directory containing modular implementations for different AI backend services (`base.py`, `ollama.py`, `gemini.py`).
- `auths.py` / `api_key_backend.py`: Core logic for Streamlit's login/register flow and DB interactions.
