# backend/api/services/code_service.py

from ...core.code_analyzer import CodeAnalyzer
from ...core.ai_integration import AIIntegration

class CodeService:
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.ai_integration = AIIntegration()

    def get_refactoring_suggestions(self, code: str):
        return self.code_analyzer.analyze_code(code)

    async def get_debug_assistance(self, code: str, error: str):
        prompt = f"Debug the following code:\n\n{code}\n\nError:\n{error}\n\nExplanation and possible fix:"
        return await self.ai_integration.generate_response(prompt)

    async def get_code_completion(self, code: str):
        prompt = f"Complete the following code:\n\n{code}\n"
        return await self.ai_integration.generate_response(prompt)