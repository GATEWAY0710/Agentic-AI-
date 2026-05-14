from abc import ABC, abstractmethod
from typing import List, Optional
from agentic.domain.request_models import MessageCreate, Message, ChatSession

class IChatRepository(ABC):
    @abstractmethod
    async def create_session(self, title: str) -> ChatSession:
        raise NotImplementedError

    @abstractmethod
    async def get_session(self, session_id: int) -> Optional[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_sessions(self) -> List[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    async def save_message(self, message: MessageCreate) -> Message:
        raise NotImplementedError

    @abstractmethod
    async def get_history(self, session_id: int, limit: int = 20) -> List[Message]:
        raise NotImplementedError

