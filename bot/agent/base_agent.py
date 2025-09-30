from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime 
from typing import Any
import logging

from bot.client.client_messages import Message
from bot.agent.agent_chat import AgentChat
from bot.common.constants import CHAT_LAST_MESSAGE_SECONDS_DELTA


logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    text: str|None
    status: int
    error_message: str|None


class BaseAgentClass(ABC):

    def __init__(self) -> None:
        self._chats: dict[str, AgentChat] = {}

    @abstractmethod
    def _create_agent_chat(self) -> AgentChat:
        pass

    @abstractmethod
    def _chat_message_counts(self, agent_chat: AgentChat) -> int:
        pass

    def _get_agent_chat(self, user_id: str) -> Any:
        logger.info(f'{user_id=}, {self._chats=}')
        logger.info(f"check user id in chat: {user_id in self._chats}")
        if not user_id in self._chats:
            agent_chat = self._create_agent_chat()
            self._chats[user_id] = agent_chat
            logger.info(f'new chat created for user id = {user_id}')
            return agent_chat
        
        agent_chat = self._chats[user_id]

        if agent_chat.last_call_date:
            time_delta = (datetime.now() - agent_chat.last_call_date).total_seconds()
            if time_delta > CHAT_LAST_MESSAGE_SECONDS_DELTA:
                agent_chat = self._create_agent_chat()
                self._chats[user_id] = agent_chat

        logger.info(f"user is = {user_id}, message counts: {self._chat_message_counts(agent_chat)}")

        return agent_chat

    def _set_agent_chat(self, user_id: str, agent_chat: AgentChat) -> None:
        self._chats[user_id] = agent_chat

    @abstractmethod
    def ask(self, message: Message) -> AgentResponse:
        pass

