from typing import Any, Dict, List
import httpx
import time
from .base import BaseProvider

class OllamaProvider(BaseProvider):
    async def get_models(self) -> List[Dict[str, Any]]:
        """Fetch models from Ollama's /tags endpoint and format to OpenAI standard."""
        try:
            # Ollama's tags endpoint isn't under /v1 normally, but they also expose /v1/models in newer versions
            # We will use /v1/models if available, otherwise fallback. For simplicity, we assume /v1 is the base url.
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                data = response.json()
                
                # If Ollama returns OpenAI compatible /v1/models
                if "data" in data:
                    models = []
                    for model in data["data"]:
                        model["id"] = f"ollama/{model['id']}" # Prefix with provider
                        models.append(model)
                    return models
                return []
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
            return []

    async def chat_completions(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Proxy chat completions to Ollama's OpenAI-compatible endpoint."""
        if request_payload.get("model", "").startswith("ollama/"):
            request_payload["model"] = request_payload["model"].replace("ollama/", "", 1)
            
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": {"message": f"Ollama error: {e.response.text}", "type": "provider_error"}}
        except Exception as e:
            return {"error": {"message": f"Error connecting to Ollama: {str(e)}", "type": "connection_error"}}

    async def stream_chat_completions(self, request_payload: Dict[str, Any]):
        """Proxy streaming chat completions to Ollama's OpenAI-compatible endpoint."""
        if request_payload.get("model", "").startswith("ollama/"):
            request_payload["model"] = request_payload["model"].replace("ollama/", "", 1)
            
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST", 
                f"{self.base_url}/chat/completions", 
                json=request_payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"data: {{\"error\": \"Ollama error: {error_text.decode('utf-8')}\"}}\n\n".encode("utf-8")
                    return
                async for chunk in response.aiter_bytes():
                    yield chunk
