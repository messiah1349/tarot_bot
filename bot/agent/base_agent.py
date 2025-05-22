from abc import abstractmethod, ABC


class AbstractAgentClass(ABC):

    @abstractmethod
    def ask(self, text: str|None=None, image: bytes|None=None) -> str:
        pass
