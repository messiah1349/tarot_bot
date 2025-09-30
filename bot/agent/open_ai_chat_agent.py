from openai import OpenAI

from bot.agent.base_agent import BaseAgentClass, messages_typing
from bot.common.constants import OPENAI_TOKEN, agent_scenarios, bot_parameters


class OpenAIAgent(BaseAgentClass):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_TOKEN)
        self.model = bot_parameters['model']
        self.instructions = agent_scenarios['instructions']

    def ask(self, messages: messages_typing) -> str:
        """
        Send either text or image (or both) to OpenAI and return the assistant response.
        """
        # build your messages list

        transform_messages = self.transform_messages(messages)

        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=transform_messages,
            temperature=.7,
        )
        return response.output_text

    @staticmethod
    def transform_messages(messages: messages_typing) -> messages_typing:
        '''
            adapt message from telegram client history to open ai format
            mostly for image url transformation
        '''
        messages_transform = []

        for message in messages:
            if not isinstance(message['content'], list):
                messages_transform.append(message)
            else:
                trim_message = {}
                trim_message['role'] = 'user'
                trim_message['content'] = []
                for content_dict in message['content']:
                    content_trim_dict = {}
                    for key, value in content_dict.items():
                        if key == 'image_url':
                            content_trim_dict[key] = f'data:image/jpeg;base64,{value}'
                        else:
                            content_trim_dict[key] = value
                    trim_message['content'].append(content_trim_dict)
                messages_transform.append(trim_message)
        return messages_transform

    # def _ask_with_image(self, image_bytes: bytes, text: str|None):
    #     messages = [
    #         {
    #             'role': 'user',
    #             'content': [
    #                 {'type': 'input_text', 'text': text},
    #                 {'type': 'input_image', 'image_url': f"data:image/jpeg;base64,{image_bytes}"},
    #             ]
    #         }
    #     ]
    #     response = self.client.responses.create(
    #         model=self.model,
    #         instructions=self.instructions,
    #         input=messages,
    #     )
    #
    #     return response.output_text
    #
