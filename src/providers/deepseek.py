import aiohttp
import os
import logging
from src.providers.base import AIProvider
from src.models.ai_models import AIRequest, AIResponse

logger = logging.getLogger(__name__)

class DeepSeekProvider(AIProvider):
    # Model constants for DeepSeek V3.2
    MODEL_CHAT = "deepseek-chat"          # Non-thinking mode
    MODEL_REASONER = "deepseek-reasoner"  # Thinking mode

    # Token limits per mode
    MAX_TOKENS_CHAT = 8192      # 8K max for non-thinking
    MAX_TOKENS_REASONER = 32768 # 32K default for thinking (max 64K)

    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")

        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.default_model = self.MODEL_CHAT

    def _get_config(self, thinking: bool):
        """Get model, max_tokens, and timeout based on thinking mode."""
        if thinking:
            return self.MODEL_REASONER, self.MAX_TOKENS_REASONER, aiohttp.ClientTimeout(total=180)
        return self.MODEL_CHAT, self.MAX_TOKENS_CHAT, aiohttp.ClientTimeout(total=90)

    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """
        Execute a chat completion request using DeepSeek API

        Args:
            request: The AI request containing model, messages, and parameters

        Returns:
            AIResponse containing the generated content
        """
        # Get config based on thinking mode
        model, max_tokens, timeout = self._get_config(request.thinking)

        # Allow model override from request, otherwise use thinking-based default
        if request.model:
            model = request.model

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": model,
            "messages": request.messages,
            "max_tokens": max_tokens if request.thinking else request.max_tokens,
            "stream": request.stream
        }

        if request.temperature is not None:
            payload["temperature"] = request.temperature

        logger.info(f"DeepSeek request: model={model}, thinking={request.thinking}, max_tokens={payload['max_tokens']}")

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                ) as response:
                    response_text = await response.text()

                    if response.status != 200:
                        logger.error(f"DeepSeek API error {response.status}: {response_text}")
                        raise RuntimeError(f"DeepSeek API error {response.status}: {response_text[:500]}")

                    data = await response.json(content_type=None)

                    return AIResponse(
                        content=data['choices'][0]['message']['content'],
                        model=data.get('model', model),
                        usage=data.get('usage')
                    )
        except aiohttp.ClientError as e:
            logger.error(f"DeepSeek connection error: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"DeepSeek connection error: {str(e)}")
        except Exception as e:
            logger.error(f"DeepSeek error: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"DeepSeek error: {str(e)}")
