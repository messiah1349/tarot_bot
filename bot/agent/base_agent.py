from abc import abstractmethod, ABC

messages_typing = list[dict[str, str|list[dict[str, str]]]]


class AbstractAgentClass(ABC):

    @abstractmethod
    def ask(self, messages: messages_typing) -> str:
        pass

