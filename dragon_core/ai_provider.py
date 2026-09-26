import httpx
from typing import List, Dict, Any, Optional
from dragon_core.config import settings

class AIProviderService:
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        self.provider = provider or settings.DEFAULT_AI_PROVIDER
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        if self.provider.lower() == "gemini":
            return await self._generate_gemini_completion(messages, model)
        else:
            # Fallback / mock default for other providers
            return {
                "provider": self.provider,
                "model": model or "default-model",
                "content": f"Mock response from {self.provider}"
            }

    async def _generate_gemini_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        gemini_model = model or "gemini-1.5-flash"
        # Extract last user content
        user_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                break

        if not user_content and messages:
            user_content = messages[-1].get("content", "")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": user_content}]
            }]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join(p.get("text", "") for p in parts)
                        return {
                            "provider": "gemini",
                            "model": gemini_model,
                            "content": text,
                            "status": "success"
                        }

                return {
                    "provider": "gemini",
                    "model": gemini_model,
                    "content": f"[Simulated response for development/testing context: Received query '{user_content}']",
                    "status": "mock_fallback",
                    "raw_status_code": response.status_code
                }
        except Exception as e:
            return {
                "provider": "gemini",
                "model": gemini_model,
                "content": f"[Simulated response due to network/API error: {str(e)}]",
                "status": "error_fallback"
            }
