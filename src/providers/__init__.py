from .base import AIProvider
from .openrouter import OpenRouterProvider
from .deepseek import DeepSeekProvider
import os
from typing import Optional

def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Factory function to get the appropriate AI provider based on configuration
    
    Args:
        provider_name: Name of the provider to use. If None, uses AI_PROVIDER env var
        
    Returns:
        An instance of the appropriate AI provider
    """
    if provider_name is None:
        provider_name = os.getenv('AI_PROVIDER', 'openrouter')
    
    providers = {
        'openrouter': OpenRouterProvider,
        'deepseek': DeepSeekProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown AI provider: {provider_name}. Available: {list(providers.keys())}")
    
    return provider_class()

__all__ = [
    'AIProvider',
    'OpenRouterProvider',
    'DeepSeekProvider',
    'get_ai_provider'
]