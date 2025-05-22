from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from bot.agent.open_ai_chat_agent import OpenAIAgent  # your agent class


class Client:
    def __init__(self, token: str, openai_api_key: str):
        self.application = Application.builder().token(token).build()

        # initialize your agent
        self.agent = OpenAIAgent(api_key=openai_api_key, instructions='you are tarot expert', model='gpt-4.1')

        # register handlers
        self.application.add_handler(CommandHandler("start", self.start))
        # handle images
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_image))
        # handle text
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text(
            "👋 Hi there! Send me text or an image, and I'll forward it to my AI agent."
        )

    async def handle_image(self, update: Update, context: CallbackContext):
        photo = update.message.photo[-1]
        file = photo.get_file()
        img_bytes = file.download_as_bytearray()
        # call your agent, passing image bytes
        response = self.agent.ask(image=img_bytes)
        await update.message.reply_text(response)

    async def handle_text(self, update: Update, context: CallbackContext):
        user_text = update.message.text
        response = self.agent.ask(text=user_text)
        await update.message.reply_text(response)

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

