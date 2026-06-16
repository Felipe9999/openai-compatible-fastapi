from fastapi import FastAPI, HTTPException, Request, Header
import nest_asyncio
from pyngrok import ngrok, conf
import uvicorn
import hashlib
import time
from functools import wraps
from typing import Any, Callable, List, Optional
from pydantic import BaseModel
import sqlite3
import configs as cfg

from providers import OllamaProvider, GeminiProvider

# Initialize Providers
providers = {}
if "ollama" in cfg.PROVIDERS:
    providers["ollama"] = OllamaProvider(
        name="ollama",
        base_url=cfg.PROVIDERS["ollama"]["base_url"],
        blacklist=cfg.PROVIDERS["ollama"].get("blacklist", [])
    )
if "gemini" in cfg.PROVIDERS:
    providers["gemini"] = GeminiProvider(
        name="gemini",
        base_url=cfg.PROVIDERS["gemini"]["base_url"],
        api_key=cfg.PROVIDERS["gemini"].get("api_key", ""),
        blacklist=cfg.PROVIDERS["gemini"].get("blacklist", [])
    )

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "ollama/llama3"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.1
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False

def rate_limit():
    def decorator(func: Callable) -> Callable:
        usage: dict[str, list[float]] = {}

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            authorization = kwargs.get("authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=400, detail="API key missing or invalid format")
                
            api_key = authorization[len("Bearer "):]
                
            conn = sqlite3.connect(cfg.DB_NAME, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT email FROM api_keys WHERE api_key = ?", (api_key,))
            result = c.fetchall()
            if result:
                user_email = result[0][0]
            else:
                raise HTTPException(status_code=400, detail="Invalid API Key")
            conn.close()

            unique_id: str = hashlib.sha256(user_email.encode()).hexdigest()

            now = time.time()
            if unique_id not in usage:
                usage[unique_id] = []
            timestamps = usage[unique_id]
            timestamps[:] = [t for t in timestamps if now - t < cfg.time_period]

            if len(timestamps) < cfg.num_request:
                timestamps.append(now)
                return await func(*args, **kwargs)

            wait = cfg.time_period - (now - timestamps[0])
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {wait:.2f} seconds",
            )

        return wrapper
    return decorator


app = FastAPI(title="OpenAI-compatible API")

@app.get("/v1/models")
@app.get("/models")
#@rate_limit()
async def list_models(authorization: str = Header(...)):
    """Return an aggregated list of models from all configured providers."""
    all_models = []
    
    for provider_name, provider in providers.items():
        models = await provider.get_models()
        filtered_models = [m for m in models if not provider.is_blacklisted(m["id"])]
        all_models.extend(filtered_models)
        
    return {
        "object": "list",
        "data": all_models
    }

from fastapi.responses import StreamingResponse

@app.post("/v1/chat/completions")
@app.post("/chat/completions")
#@rate_limit()
async def chat_completions(request: Request, body: ChatCompletionRequest, authorization: str = Header(...)):
    """Proxy the chat completion request to the correct provider based on the model prefix."""
    request_payload = body.dict(exclude_unset=True)
    model_name = request_payload.get("model", "")
    
    provider_name = model_name.split("/")[0] if "/" in model_name else "ollama"
    
    if provider_name not in providers:
        raise HTTPException(status_code=400, detail=f"Unsupported or unconfigured provider: {provider_name}")
        
    provider = providers[provider_name]

    if provider.is_blacklisted(model_name):
        raise HTTPException(status_code=403, detail=f"Model {model_name} is blacklisted and cannot be used.")

    # Check if stream is requested
    is_stream = request_payload.get("stream", False)

    if is_stream:
        return StreamingResponse(
            provider.stream_chat_completions(request_payload),
            media_type="text/event-stream"
        )
    else:
        response = await provider.chat_completions(request_payload)
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        return response

if __name__ == "__main__":
    uvicorn.run("serving:app", host="0.0.0.0", port=8000, reload=True)