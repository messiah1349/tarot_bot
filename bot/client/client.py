from datetime import datetime
import logging

from PIL import Image
import io
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from bot.agent.base_agent import BaseAgent
from bot.client.client_messages import Message, MessageType, MessageContent
from bot.common.constants import TELEGRAM_TOKEN, bot_parameters, bot_scenarios, AGENT
from bot.common.utils import escape_markdown_v2


logger = logging.getLogger(__name__)


class Client:
    def __init__(self):
        if not TELEGRAM_TOKEN:
            logger.error('telegram token is not provided')
            raise AttributeError
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        if AGENT == 'open_ai_agent':
            from bot.agent.open_ai_agent import OpenAIAgent
            self.agent: BaseAgent = OpenAIAgent()
        elif bot_parameters['agent'] == 'gemini_agent':
            from bot.agent.gemini_agent import GeminiAgent
            self.agent: BaseAgent = GeminiAgent()
        else:
            from bot.agent.test_agent import TestAgent
            self.agent: BaseAgent = TestAgent()

    async def _reply_with_markdown(self, update: Update, markdown_text: str|None) -> None:
        if not update.message:
            return
        if markdown_text is None:
            await update.message.reply_text(bot_scenarios['bad_request_llm_reply'])
            return

        logger.info(f'{markdown_text=}')

        markdown_text = escape_markdown_v2(markdown_text)
        try:
            # First, try to send with Markdown formatting
            await update.message.reply_text(markdown_text, parse_mode=ParseMode.MARKDOWN_V2)
            logger.info("sanitized_text was sent")

        except BadRequest as e:
            # Check if the error is the one we're looking for
            if "Can't parse entities" in str(e):
                logger.warning(f"couldn't parse markdown from llm, {markdown_text=}")
                # If it is, send the message again as plain text
                cleaned_text = markdown_text.replace('*', '').replace('_', '').replace('`', '')#.replace('\n', '')
                await update.message.reply_text(cleaned_text)
            else:
                await update.message.reply_text(bot_scenarios['bad_request_llm_reply'])

    async def start(self, update: Update, context: CallbackContext):
        logger.info('start message request')
        await self._reply_with_markdown(update, bot_scenarios['welcome_message'])
        # await update.message.reply_text(
        #     bot_scenarios['welcome_message'], parse_mode='markdown',
        # )

    async def handle_image(self, update: Update, context: CallbackContext):
        if not update.message:
            return

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
        await self._reply_with_markdown(update, bot_scenarios['agent_wait_message_with_photo'])
        response = await self.agent.ask(message)
        if response.status == 400:
            await self._reply_with_markdown(update, bot_scenarios['bad_request_llm_reply'])
        else:
            await self._reply_with_markdown(update, response.text)

    async def handle_text(self, update: Update, context: CallbackContext):
        if not update.message:
            return

        if not update.message.from_user:
            return

        user_id = update.message.from_user.id
        user_text = update.message.text

        # ask agent and reply
        message = Message(str(user_id), [MessageContent(MessageType.TEXT, user_text)], datetime.now())
        await update.message.reply_text(bot_scenarios['agent_wait_message_with_text'], parse_mode='markdown')
        response = await self.agent.ask(message)
        await self._reply_with_markdown(update, response.text)

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

