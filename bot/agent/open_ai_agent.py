from typing import Any
from datetime import datetime
import logging

from openai import AsyncOpenAI

from bot.agent.base_agent import BaseAgent
from bot.common.constants import OPENAI_TOKEN, OPENAI_MODEL, agent_scenarios, bot_parameters
from bot.agent.base_agent import BaseAgent, AgentResponse
from bot.agent.agent_chat import AgentChat
from bot.client.client_messages import Message, MessageType

logger = logging.getLogger(__name__)


class OpenAIAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.client = AsyncOpenAI(api_key=OPENAI_TOKEN)
        self.model = OPENAI_MODEL
        self.instructions = agent_scenarios['instructions']
        logger.info(f'openai agent initialized with model = {self.model}')

    def _create_agent_chat(self) -> AgentChat:
        history = [{'role': 'system', 'content': self.instructions}]
        agent_chat = AgentChat(chat=history, last_call_date=None, last_call_status=True)
        return agent_chat

    def _chat_message_counts(self, agent_chat: AgentChat) -> int:
        return len(agent_chat.chat) - 1

    async def _call_openai(self, history: list[dict[str, Any]]) -> str:
        response = await self.client.responses.create(
            model=self.model,
            input=history,
        )
        return response.output_text

    async def ask(self, message: Message) -> AgentResponse:
        user_id = str(message.user_id)
        agent_chat = self._get_agent_chat(user_id)
        chat = agent_chat.chat
        logger.info(f"user id = {user_id}, message counts: {self._chat_message_counts(agent_chat)}")

        content = []
        for message_content in message.content:
            if message_content.message_type == MessageType.IMAGE:
                image = message_content.content
                uploaded_file = await self.client.files.create(
                    file=('telegram_image.jpg', image),
                    purpose="vision",
                )
                file_id = uploaded_file.id
                logger.info(f"{uploaded_file.expires_at=}")

                content.append({"type": "input_image", "file_id": file_id})
            else: # text
                content.append({"type": "input_text", "text": message_content.content})

        chat.append({"role": "user", "content": content})

        try:
            # logger.info(f'{chat=}')
            response_text = await self._call_openai(chat)
            chat.append({"role": "assistant", "content": response_text})
            updated_agent_chat = AgentChat(chat, datetime.now(), True)
            self._set_agent_chat(user_id, updated_agent_chat)
            # logger.info(f'before send agent response: {self._chats=}')
            return AgentResponse(response_text, 200, None)
        except Exception as e:
            logger.error(f'error happened during openai call. {e}')
            return AgentResponse(None, 400, str(e))
