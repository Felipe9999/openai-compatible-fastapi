from typing import Any, Dict, List
import httpx

class BaseProvider:
    def __init__(self, name: str, base_url: str, api_key: str = "", blacklist: List[str] = None):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.blacklist = blacklist or []

    def is_blacklisted(self, model_name: str) -> bool:
        """Check if a model is blacklisted, ignoring any provider prefixes."""
        actual_name = model_name.split("/", 1)[1] if "/" in model_name else model_name
        return actual_name in self.blacklist

    async def get_models(self) -> List[Dict[str, Any]]:
        """Fetch models from the provider and format as OpenAI standard."""
        raise NotImplementedError

    async def chat_completions(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Proxy a chat completion request to the provider."""
        raise NotImplementedError

    from typing import AsyncGenerator
    async def stream_chat_completions(self, request_payload: Dict[str, Any]):
        """Proxy a streaming chat completion request and yield bytes."""
        raise NotImplementedError
