from bot.client.client import Client
from bot.common.logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    client = Client()
    client.run()
