from dotenv import load_dotenv
from pathlib import Path
import os
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', None)
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN', None)
MODEL = os.getenv('MODEL', None)

with open('configs/scenarios.yaml') as f:
    scenarios = yaml.safe_load(f)

