from typing import Any, Dict, List
from openai import AsyncOpenAI
from .base import BaseProvider

class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, name: str, base_url: str, api_key: str = "", blacklist: List[str] = None):
        super().__init__(name, base_url, api_key, blacklist)
        # OpenAI package requires a non-empty api_key
        # If none provided, use a dummy one (Ollama typically doesn't check it)
        actual_api_key = self.api_key if self.api_key else "dummy_key"
        self.client = AsyncOpenAI(api_key=actual_api_key, base_url=self.base_url)

    async def get_models(self) -> List[Dict[str, Any]]:
        """Fetch models from the OpenAI-compatible /models endpoint."""
        try:
            response = await self.client.models.list()
            models = []
            for m in response.data:
                model_dict = m.model_dump()
                model_dict["id"] = f"{self.name}/{model_dict['id']}" # Prefix with provider
                models.append(model_dict)
            return models
        except Exception as e:
            print(f"Error fetching {self.name} models: {e}")
            return []

    async def chat_completions(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Proxy chat completions to the OpenAI-compatible endpoint."""
        if request_payload.get("model", "").startswith(f"{self.name}/"):
            request_payload["model"] = request_payload["model"].replace(f"{self.name}/", "", 1)
            
        try:
            response = await self.client.chat.completions.create(**request_payload)
            return response.model_dump()
        except Exception as e:
            return {"error": {"message": f"Error from {self.name}: {str(e)}", "type": "provider_error"}}

    async def stream_chat_completions(self, request_payload: Dict[str, Any]):
        """Proxy streaming chat completions to the OpenAI-compatible endpoint."""
        if request_payload.get("model", "").startswith(f"{self.name}/"):
            request_payload["model"] = request_payload["model"].replace(f"{self.name}/", "", 1)
            
        try:
            stream = await self.client.chat.completions.create(**request_payload)
            async for chunk in stream:
                yield f"data: {chunk.model_dump_json()}\n\n".encode("utf-8")
        except Exception as e:
            yield f"data: {{\"error\": \"Error from {self.name}: {str(e)}\"}}\n\n".encode("utf-8")
