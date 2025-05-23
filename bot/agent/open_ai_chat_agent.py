from openai import OpenAI

from bot.agent.base_agent import AbstractAgentClass
from bot.common.constants import OPENAI_TOKEN, MODEL, scenarios


class OpenAIAgent(AbstractAgentClass):
    def __init__(self, ):
        self.client = OpenAI(api_key=OPENAI_TOKEN)
        self.model = MODEL
        self.instructions = scenarios['instructions']

    def ask(self, text: str|None=None, image: bytes|None=None) -> str:
        """
        Send either text or image (or both) to OpenAI and return the assistant response.
        """
        # build your messages list
        messages = []
        if text:
            messages.append({"role": "user", "content": text})

        if image:
            # if using vision-capable model
            return self._ask_with_image(image, text)

        return self._ask_text_only(messages)

    def _ask_text_only(self, messages: list) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=messages,
            temperature=.7,
        )
        return response.output_text

    def _ask_with_image(self, image_bytes: bytes, text: str|None):
        messages = [
            {
                'role': 'user',
                'content': [
                    {'type': 'input_text', 'text': text},
                    {'type': 'input_image', 'image_url': f"data:image/jpeg;base64,{image_bytes}"},
                ]
            }
        ]
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=messages,
        )

        return response.output_text

