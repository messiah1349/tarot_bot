import logging
from datetime import datetime

from google import genai
from google.genai.types import Content, Part

from bot.agent.base_agent import BaseAgent, AgentResponse
from bot.agent.agent_chat import AgentChat
from bot.client.client_messages import Message, MessageType
from bot.common.constants import GEMINI_TOKEN, GEMINI_MODEL, agent_scenarios, bot_parameters

logger = logging.getLogger(__name__)


class GeminiAgent(BaseAgent):

    def __init__(self) -> None:
        super().__init__()
        self._client = genai.Client(
            api_key = GEMINI_TOKEN,
        )
        logger.info("Gemini client successfully created")

    def _create_agent_chat(self) -> AgentChat:
        chat = [] 
        agent_chat = AgentChat(chat, None, True)
        return agent_chat

    def _chat_message_counts(self, agent_chat: AgentChat) -> int:
        return len(agent_chat.chat)

    async def _call_gemini(self, messages: list[Content]) -> str|None:
        config = {'system_instruction': agent_scenarios['instructions']}
        response = await self._client.aio.models.generate_content(model=GEMINI_MODEL, contents=messages, config=config)
        return response.text

    async def ask(self, message: Message) -> AgentResponse:
        user_id = str(message.user_id)
        agent_chat = self._get_agent_chat(user_id)
        chat = agent_chat.chat
        logger.info(f"user id = {user_id}, message counts: {self._chat_message_counts(agent_chat)}")

        parts = []
        for message_content in message.content:
            if message_content.message_type == MessageType.IMAGE:
                image = message_content.content
                file = self._client.files.upload(file=image, config={'mime_type': 'image/jpeg'})
                part = Part.from_uri(file_uri=file.uri, mime_type=file.mime_type)
                parts.append(part)
            else:
                parts.append(Part(text=message_content.content))

        logger.info(f'{parts=}')
        chat.append(Content(role='user', parts=parts))

        try:
            response_text = await self._call_gemini(chat)
            chat.append(Content(role='model', parts=[Part(text=response_text)]))
            updated_agent_chat = AgentChat(chat, datetime.now(), True)
            self._set_agent_chat(user_id, updated_agent_chat)
            logger.info(f'before send agent response: {self._chats=}')
            return AgentResponse(response_text, 200, None)
        except Exception as e:
            return AgentResponse(None, 400, str(e))
            
