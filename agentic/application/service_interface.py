from abc import ABC, abstractmethod
from typing import List, AsyncGenerator

from agentic.domain.request_models import ChatSession


class IChatService(ABC):
    @abstractmethod
    async def handle_user_message(self, session_id: int, user_message: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def handle_user_message_stream(self, session_id: int, user_message: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    @abstractmethod
    async def create_new_chat(self, title: str = "New Chat") -> ChatSession:
        raise NotImplementedError

    @abstractmethod
    async def list_chats(self) -> List[ChatSession]:
        raise NotImplementedError
