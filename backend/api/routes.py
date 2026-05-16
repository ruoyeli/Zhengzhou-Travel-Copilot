from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.schemas.chat_schemas import ChatRequest
from backend.services.agent_service import stream_agent

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for chunk in stream_agent(request.message, request.thread_id):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")