from abc import ABC, abstractmethod
from typing import Optional
from src.models.ai_models import AIRequest, AIResponse

class AIProvider(ABC):
    @abstractmethod
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        """
        Execute a chat completion request
        
        Args:
            request: The AI request containing model, messages, and parameters
            
        Returns:
            AIResponse containing the generated content
        """
        pass