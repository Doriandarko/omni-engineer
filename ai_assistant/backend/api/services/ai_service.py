# backend/api/services/ai_service.py

from ...core.ai_integration import AIIntegration

class AIService:
    def __init__(self):
        self.ai_integration = AIIntegration()

    async def generate_response(self, prompt: str, user_id: str) -> str:
        return await self.ai_integration.generate_response(prompt, user_id)

    def stream_response(self, prompt: str, user_id: str):
        return self.ai_integration.stream_response(prompt, user_id)

    def switch_model(self, model: str) -> str:
        return self.ai_integration.switch_model(model)