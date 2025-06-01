import pytest
import base64
from bot.agent.open_ai_chat_agent import OpenAIAgent


def open_image():
    with open('/Users/evgenii/Pictures/adhocs/2023-01-22 22.09.16.jpg', 'rb') as file:
        img_bytes = base64.b64encode(file.read()).decode('utf-8')
    return img_bytes

text_with_image = 'what do you see on this picture'
text_no_image = 'what is a capital of bangladesh'
image = open_image()

open_ai_agent = OpenAIAgent()

resp_no_image = open_ai_agent.ask(text_no_image)
resp_with_image = open_ai_agent.ask(text_with_image, image)

print(f'{resp_no_image=}')
print(f'{resp_with_image=}')
