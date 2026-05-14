from dependency_injector import containers, providers
from typing import Callable
import logging
from agentic.application.repository_interfaces import IChatRepository
from agentic.application.service_interface import IChatService
from agentic.infrastructure.repository.chat_repository import ChatRepository
from agentic.infrastructure.service.chat_service import ChatService
from agentic.infrastructure.ai_client import OllamaClient

logger = logging.getLogger(__name__)

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    ai_client = providers.Singleton(OllamaClient)
    
    chat_repository: Callable[[], IChatRepository] = providers.Factory(ChatRepository, logger=logger)
    
    chat_service: Callable[[], IChatService] = providers.Factory(
        ChatService, 
        repository=chat_repository, 
        ai_client=ai_client
    )
    
container = Container()
