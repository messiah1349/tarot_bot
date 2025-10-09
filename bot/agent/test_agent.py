from bot.agent.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def ask(self, messages) -> str:
        return 'that is test agent response'

