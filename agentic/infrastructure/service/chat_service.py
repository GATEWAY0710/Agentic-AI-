from typing import List, AsyncGenerator
from agentic.application.repository_interfaces import IChatRepository
from agentic.application.service_interface import IChatService
from agentic.domain.request_models import MessageCreate, ChatSession
from agentic.infrastructure.ai_client import OllamaClient

class ChatService(IChatService):
    def __init__(self, repository: IChatRepository, ai_client: OllamaClient):
        self.repository = repository
        self.ai_client = ai_client

    async def handle_user_message(self, session_id: int, user_message: str) -> str:
        full_response = ""
        async for chunk in self.handle_user_message_stream(session_id, user_message):
            full_response += chunk
        return full_response

    async def handle_user_message_stream(self, session_id: int, user_message: str) -> AsyncGenerator[str, None]:
        # 1. Get history from Repository
        history_entities = await self.repository.get_history(session_id)
        history = [{"role": m.role, "content": m.content} for m in history_entities]

        # 2. Save User Message to DB
        await self.repository.save_message(
            MessageCreate(session_id=session_id, role="user", content=user_message)
        )

        # 3. Stream AI Response and accumulate full string
        full_ai_response = ""
        async for chunk in self.ai_client.generate_response_stream(history, user_message):
            full_ai_response += chunk
            yield chunk

        # 4. Save the FULL AI Response to DB after streaming is done
        if full_ai_response:
            await self.repository.save_message(
                MessageCreate(session_id=session_id, role="assistant", content=full_ai_response)
            )

    async def create_new_chat(self, title: str = "New Chat") -> ChatSession:
        return await self.repository.create_session(title)

    async def list_chats(self) -> List[ChatSession]:
        return await self.repository.get_all_sessions()
