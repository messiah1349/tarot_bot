from bot.agent.base_agent import messages_typing


def transform_long_history_messages(messages: messages_typing) -> messages_typing:
    messages_trim = []

    for message in messages:
        if not isinstance(message['content'], list):
            messages_trim.append(message)
        else:
            trim_message = {}
            trim_message['role'] = 'user'
            trim_message['content'] = []
            for content_dict in message['content']:
                content_trim_dict = {}
                for key, value in content_dict.items():
                    content_trim_dict[key] = value[:100]
                trim_message['content'].append(content_trim_dict)
            messages_trim.append(trim_message)
    return messages_trim
