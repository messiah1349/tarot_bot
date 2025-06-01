import logging
from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from bot.agent.base_agent import AbstractAgentClass
from bot.common.constants import TELEGRAM_TOKEN, bot_parameters, CHAT_HISTORY_MESSAGE_COUNT
from bot.common.debug_tools import transform_long_history_messages


logger = logging.getLogger(__name__)


class Client:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        if bot_parameters['agent'] == 'open_ai_chat_agent':
            from bot.agent.open_ai_chat_agent import OpenAIAgent
            self.agent: AbstractAgentClass = OpenAIAgent()
        else:
            from bot.agent.test_agent import TestAgent
            self.agent: AbstractAgentClass = TestAgent()

    async def start(self, update: Update, context: CallbackContext):
        logger.info('start message request')
        await update.message.reply_text(
            "👋 Hi there! Send me text or an image, and I'll forward it to my AI agent."
        )

    async def handle_image(self, update: Update, context: CallbackContext):
        caption = update.message.caption
        caption = caption if caption else ""

        photo = update.message.photo[-1]
        file = await photo.get_file()
        img_bytes = await file.download_as_bytearray()

        #upddate conversation history
        history = context.user_data.setdefault("history", [])
        history_update = {
            'role': 'user', 
            'content': [
                {'type': 'text', 'text': caption},
                {'type': 'image_url', 'image_url': img_bytes},
            ]
        }
        history.append(history_update)
        context.user_data['history'] = history[-CHAT_HISTORY_MESSAGE_COUNT:]

        #ask agent and reply
        response = self.agent.ask(context.user_data['history'])
        await update.message.reply_text(response)

        # update history with agent reply
        history.append({'role': 'assistant', 'content': response})
        context.user_data['history'] = history[-CHAT_HISTORY_MESSAGE_COUNT:]
        logger.info(f'current story: "{transform_long_history_messages(context.user_data['history'])}"')

    async def handle_text(self, update: Update, context: CallbackContext):
        user_text = update.message.text
        # update history with user request
        history = context.user_data.setdefault("history", [])
        history.append({'role': 'user', 'content': user_text})
        context.user_data['history'] = history[-CHAT_HISTORY_MESSAGE_COUNT:]

        # ask agent and reply
        response = self.agent.ask(context.user_data['history'])
        await update.message.reply_text(response)

        history.append({'role': 'assistant', 'content': response})
        context.user_data['history'] = history[-CHAT_HISTORY_MESSAGE_COUNT:]
        logger.info(f'current story: "{transform_long_history_messages(context.user_data['history'])}"')

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

