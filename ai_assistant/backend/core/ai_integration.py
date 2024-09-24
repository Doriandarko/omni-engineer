# backend/core/ai_integration.py

import openai
from ..utils.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class AIIntegration:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model

    async def generate_response(self, prompt: str, user_id: str = None) -> str:
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def stream_response(self, prompt: str, user_id: str = None):
        try:
            async for chunk in await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            ):
                content = chunk["choices"][0].get("delta", {}).get("content")
                if content is not None:
                    yield content
        except Exception as e:
            yield f"An error occurred: {str(e)}"

    def switch_model(self, model: str) -> str:
        available_models = ["gpt-3.5-turbo", "gpt-4"]  # Add more as needed
        if model in available_models:
            self.model = model
            return f"Switched to model: {model}"
        else:
            raise ValueError(f"Invalid model. Available models are: {', '.join(available_models)}")