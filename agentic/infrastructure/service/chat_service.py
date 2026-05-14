from agentic.application.repository_interfaces import IChatRepository
from agentic.application.service_interface import IChatService
from agentic.domain.request_models import MessageCreate, Message, ChatSession
from agentic.infrastructure.ai_client import OllamaClient

class ChatService(IChatService):
    def __init__(self, repository: IChatRepository, ai_client: OllamaClient):
        self.repository = repository
        self.ai_client = ai_client

    async def handle_user_message(self, session_id: int, user_message: str) -> str:
        history_entities = await self.repository.get_history(session_id)
        history = [{"role": m.role, "content": m.content} for m in history_entities]

        await self.repository.save_message(
            MessageCreate(session_id=session_id, role="user", content=user_message)
        )

        ai_response = await self.ai_client.generate_response(history, user_message)

        await self.repository.save_message(
            MessageCreate(session_id=session_id, role="assistant", content=ai_response)
        )

        return ai_response

    async def create_new_chat(self, title: str = "New Chat") -> ChatSession:
        return await self.repository.create_session(title)

    async def list_chats(self):
        return await self.repository.get_all_sessions()
