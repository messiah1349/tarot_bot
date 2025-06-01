from bot.agent.base_agent import AbstractAgentClass

class TestAgent(AbstractAgentClass):
    def ask(self, messages) -> str:
        return 'that is test agent response'

