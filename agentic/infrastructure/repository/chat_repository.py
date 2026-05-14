from typing import List, Optional
from logging import Logger
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from agentic.infrastructure.database import AsyncSessionLocal
from agentic.application.repository_interfaces import IChatRepository
from agentic.domain.models import SessionEntity, MessageEntity
from agentic.domain.request_models import MessageCreate, Message, ChatSession

class ChatRepository(IChatRepository):
    def __init__(self, logger: Logger):
        self.logger = logger

    async def create_session(self, title: str) -> Optional[ChatSession]:
        async with AsyncSessionLocal() as session:
            try:
                entity = SessionEntity(title=title)
                session.add(entity)
                await session.commit()
                stmt = select(SessionEntity).where(SessionEntity.id == entity.id).options(selectinload(SessionEntity.messages))
                result = await session.execute(stmt)
                full_entity = result.scalars().first()
                self.logger.info("Chat session created successfully.")
                return ChatSession.model_validate(full_entity)
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error creating chat session: {e}")
                return None

    async def get_session(self, session_id: int) -> Optional[ChatSession]:
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(SessionEntity).where(SessionEntity.id == session_id).options(selectinload(SessionEntity.messages))
                result = await session.execute(stmt)
                entity = result.scalars().one_or_none()
                if entity:
                    return ChatSession.model_validate(entity)
                return None
            except Exception as e:
                self.logger.error(f"Error retrieving session {session_id}: {e}")
                return None

    async def get_all_sessions(self) -> List[ChatSession]:
        async with AsyncSessionLocal() as session:
            try:
                stmt = select(SessionEntity).options(selectinload(SessionEntity.messages)).order_by(SessionEntity.created_at.desc())
                result = await session.execute(stmt)
                entities = result.scalars().all()
                return [ChatSession.model_validate(e) for e in entities]
            except Exception as e:
                self.logger.error(f"Error retrieving all sessions: {e}")
                return []

    async def save_message(self, message: MessageCreate) -> Optional[Message]:
        async with AsyncSessionLocal() as session:
            try:
                entity = MessageEntity(
                    session_id=message.session_id,
                    role=message.role,
                    content=message.content
                )
                session.add(entity)
                await session.commit()
                await session.refresh(entity)
                self.logger.info(f"Message saved for session {message.session_id}")
                return Message.model_validate(entity)
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error saving message: {e}")
                return None

    async def get_history(self, session_id: int, limit: int = 20) -> List[Message]:
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    select(MessageEntity)
                    .where(MessageEntity.session_id == session_id)
                    .order_by(MessageEntity.created_at.asc())
                    .limit(limit)
                )
                entities = result.scalars().all()
                return [Message.model_validate(e) for e in entities]
            except Exception as e:
                self.logger.error(f"Error retrieving history for session {session_id}: {e}")
                return []
