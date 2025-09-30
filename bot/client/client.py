from datetime import datetime
import logging

from PIL import Image
import io
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from bot.agent.base_agent import BaseAgentClass
from bot.client.client_messages import Message, MessageType, MessageContent
from bot.common.constants import TELEGRAM_TOKEN, bot_parameters, bot_scenarios
from bot.common.utils import escape_markdown_v2


logger = logging.getLogger(__name__)


class Client:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        if bot_parameters['agent'] == 'open_ai_chat_agent':
            from bot.agent.open_ai_chat_agent import OpenAIAgent
            self.agent: BaseAgentClass = OpenAIAgent()
        elif bot_parameters['agent'] == 'gemini_agent':
            from bot.agent.gemini_agent import GeminiAgent
            self.agent: BaseAgentClass = GeminiAgent()
        else:
            from bot.agent.test_agent import TestAgent
            self.agent: BaseAgentClass = TestAgent()

    async def _reply_with_markdown(self, update: Update, markdown_text: str|None) -> None:
        if markdown_text is None:
            await update.message.reply_text(bot_scenarios['bad_request_llm_reply'])
            return

        sanitized_text = escape_markdown_v2(markdown_text)
        try:
            # First, try to send with Markdown formatting
            await update.message.reply_text(sanitized_text, parse_mode=ParseMode.MARKDOWN_V2)
            logger.info("sanitized_text was sent")

        except BadRequest as e:
            # Check if the error is the one we're looking for
            if "Can't parse entities" in str(e):
                logger.warning(f"couldn't parse markdown from llm, {sanitized_text=}")
                # If it is, send the message again as plain text
                await update.message.reply_text(sanitized_text)
            else:
                await update.message.reply_text(bot_scenarios['bad_request_llm_reply'])

    async def start(self, update: Update, context: CallbackContext):
        logger.info('start message request')
        await update.message.reply_text(
            bot_scenarios['welcome_message'], parse_mode='markdown',
        )

    async def handle_image(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id

        caption = update.message.caption

        photo = update.message.photo[-1]
        tg_file = await photo.get_file()

        image_bytearray = await tg_file.download_as_bytearray()
        telegram_image = Image.open(io.BytesIO(image_bytearray))

        img_byte_stream = io.BytesIO()
        telegram_image.save(img_byte_stream, format='JPEG')
        img_byte_stream.seek(0)

        message_content = []
        image_message_content = MessageContent(MessageType.IMAGE, img_byte_stream)
        message_content.append(image_message_content)

        if caption:
            text_message_content = MessageContent(MessageType.TEXT, caption)
            message_content.append(text_message_content)
        
        message = Message(str(user_id), message_content, datetime.now())

        #ask agent and reply
        await update.message.reply_text(bot_scenarios['agent_wait_message_with_photo'], parse_mode='markdown')
        response = self.agent.ask(message)
        await self._reply_with_markdown(update, response.text)


    async def handle_text(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        user_text = update.message.text

        # ask agent and reply
        message = Message(user_id, [MessageContent(MessageType.TEXT, user_text)], datetime.now())
        await update.message.reply_text(bot_scenarios['agent_wait_message_with_text'], parse_mode='markdown')
        response = self.agent.ask(message)
        await self._reply_with_markdown(update, response.text)

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

