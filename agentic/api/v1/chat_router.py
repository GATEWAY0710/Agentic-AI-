from fastapi import APIRouter, Depends, HTTPException
from agentic.infrastructure.dependency import container
from agentic.application.service_interface import IChatService

router = APIRouter()

@router.post("")
async def create_session(title: str = "New Chat"):
    chat_service: IChatService = container.chat_service()
    return await chat_service.create_new_chat(title)

@router.get("/sessions")
async def list_sessions():
    chat_service: IChatService = container.chat_service()
    return await chat_service.list_chats()

@router.post("/{session_id}/message")
async def send_message(session_id: int, message: str):
    chat_service: IChatService = container.chat_service()
    reply = await chat_service.handle_user_message(session_id, message)
    return {"reply": reply}
