from dotenv import load_dotenv
from pathlib import Path
import os
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', None)
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN', None)
GEMINI_TOKEN = os.getenv('GEMINI_API_KEY', None)
GEMINI_MODEL = os.getenv('GEMINI_MODEL', None)
OPENAI_MODEL = os.getenv('OPENAI_MODEL', None)
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

with open('configs/agent_scenarios.yaml') as f:
    agent_scenarios = yaml.safe_load(f)

with open('configs/bot_scenarios.yaml') as f:
    bot_scenarios = yaml.safe_load(f)

with open('configs/bot_parameters.yaml') as f:
    bot_parameters = yaml.safe_load(f)

AGENT = bot_parameters['agent']

# CHAT_HISTORY_MESSAGE_COUNT = bot_parameters['chat_history_message_count']
CHAT_LAST_MESSAGE_SECONDS_DELTA = bot_parameters['time_between_chat_messages_in_seconds']
