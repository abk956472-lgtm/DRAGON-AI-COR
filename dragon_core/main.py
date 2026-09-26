from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dragon_core.config import settings
from dragon_core.ai_provider import AIProviderService

app = FastAPI(
    title="Dragon Core API",
    version="1.0.0",
    description="Dragon Core AI Integration Engine"
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    provider: Optional[str] = None

@app.get("/")
async def root():
    return {
        "service": "Dragon Core API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "default_provider": settings.DEFAULT_AI_PROVIDER,
        "debug": settings.DEBUG
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")

    provider_service = AIProviderService(provider=request.provider)
    formatted_messages = [msg.model_dump() for msg in request.messages]

    result = await provider_service.generate_completion(
        messages=formatted_messages,
        model=request.model
    )

    return {
        "id": "dragon-chat-completion",
        "object": "chat.completion",
        "provider": result.get("provider"),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result.get("content", "")
                },
                "finish_reason": "stop"
            }
        ],
        "metadata": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dragon_core.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
