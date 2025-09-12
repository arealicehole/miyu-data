from openai import AsyncOpenAI
from src.providers.base import AIProvider
from src.models.ai_models import AIRequest, AIResponse
import os
import logging

logger = logging.getLogger(__name__)

class OpenRouterProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")
            
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.default_model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
        self.app_url = os.getenv('APP_URL', 'https://miyu-data.discord')
        self.app_name = os.getenv('APP_NAME', 'Miyu-Data Discord Bot')
        
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """
        Execute a chat completion request using OpenRouter
        
        Args:
            request: The AI request containing model, messages, and parameters
            
        Returns:
            AIResponse containing the generated content
        """
        try:
            response = await self.client.chat.completions.create(
                model=request.model or self.default_model,
                messages=request.messages,
                max_tokens=request.max_tokens,
                stream=request.stream,
                temperature=request.temperature,
                extra_headers={
                    "HTTP-Referer": self.app_url,
                    "X-Title": self.app_name,
                }
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None
            )
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise RuntimeError(f"OpenRouter API error: {str(e)}")