import aiohttp
import os
import logging
from src.providers.base import AIProvider
from src.models.ai_models import AIRequest, AIResponse

logger = logging.getLogger(__name__)

class DeepSeekProvider(AIProvider):
    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
            
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.default_model = "deepseek-chat"
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """
        Execute a chat completion request using DeepSeek API
        
        Args:
            request: The AI request containing model, messages, and parameters
            
        Returns:
            AIResponse containing the generated content
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": request.model or self.default_model,
            "messages": request.messages,
            "max_tokens": request.max_tokens,
            "stream": request.stream
        }
        
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    return AIResponse(
                        content=data['choices'][0]['message']['content'],
                        model=data.get('model', self.default_model),
                        usage=data.get('usage')
                    )
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise RuntimeError(f"DeepSeek API error: {str(e)}")