from bot.agent.base_agent import BaseAgentClass

class TestAgent(BaseAgentClass):
    def ask(self, messages) -> str:
        return 'that is test agent response'

