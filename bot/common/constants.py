from dotenv import load_dotenv
from pathlib import Path
import os
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', None)
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN', None)
MODEL = os.getenv('MODEL', None)
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

with open('configs/scenarios.yaml') as f:
    scenarios = yaml.safe_load(f)

with open('configs/bot_parameters.yaml') as f:
    bot_parameters = yaml.safe_load(f)

CHAT_HISTORY_MESSAGE_COUNT = bot_parameters['chat_history_message_count']
