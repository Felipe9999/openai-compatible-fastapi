from typing import Any, Dict, List
import httpx
from .base import BaseProvider

class GeminiProvider(BaseProvider):
    async def get_models(self) -> List[Dict[str, Any]]:
        """Fetch models from Gemini's OpenAI-compatible /models endpoint."""
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.get(f"{self.base_url}/models", headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if "data" in data:
                    models = []
                    for model in data["data"]:
                        model["id"] = f"gemini/{model['id']}" # Prefix with provider
                        models.append(model)
                    return models
                return []
        except Exception as e:
            print(f"Error fetching Gemini models: {e}")
            return []

    async def chat_completions(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Proxy chat completions to Gemini's OpenAI-compatible endpoint."""
        if not self.api_key:
             return {"error": {"message": "Gemini API key not configured", "type": "config_error"}}
             
        # Remove 'gemini/' prefix from model name
        if request_payload.get("model", "").startswith("gemini/"):
            request_payload["model"] = request_payload["model"].replace("gemini/", "", 1)
            
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    return {"error": {"message": f"Gemini API error: {response.text}", "type": "provider_error", "code": response.status_code}}
                
                return response.json()
        except Exception as e:
            return {"error": {"message": f"Error connecting to Gemini: {str(e)}", "type": "connection_error"}}

    async def stream_chat_completions(self, request_payload: Dict[str, Any]):
        """Proxy streaming chat completions to Gemini's OpenAI-compatible endpoint."""
        if not self.api_key:
             yield f"data: {{\"error\": \"Gemini API key not configured\"}}\n\n".encode("utf-8")
             return
             
        if request_payload.get("model", "").startswith("gemini/"):
            request_payload["model"] = request_payload["model"].replace("gemini/", "", 1)
            
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", 
                f"{self.base_url}/chat/completions", 
                json=request_payload,
                headers=headers
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"data: {{\"error\": \"Gemini API error: {error_text.decode('utf-8')}\"}}\n\n".encode("utf-8")
                    return
                async for chunk in response.aiter_bytes():
                    yield chunk
