import os
from typing import List, Optional
from openai import AsyncOpenAI
from abc import ABC, abstractmethod
import asyncio
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=3, base_delay=1):
    """Decorator for retrying failed API calls with exponential backoff"""
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    delay = base_delay * (2 ** retries)
                    logger.warning(f"Retry {retries}/{max_retries} after {delay}s delay: {str(e)}")
                    await asyncio.sleep(delay)
            return None
        return wrapper
    return decorator

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        pass
    
    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings provider using direct API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required for embeddings")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.raw_dimensions = 1536 if model == "text-embedding-3-small" else 3072
        # Pad to 3072 to match existing Pinecone index
        self.target_dimensions = 3072
        logger.info(f"Initialized OpenAI embedding provider with model: {model} (raw: {self.raw_dimensions}, padded: {self.target_dimensions} dimensions)")
    
    def _pad_embedding(self, embedding: List[float]) -> List[float]:
        """Pad embedding to target dimensions with zeros"""
        if len(embedding) >= self.target_dimensions:
            return embedding[:self.target_dimensions]
        return embedding + [0.0] * (self.target_dimensions - len(embedding))
    
    @retry_with_backoff(max_retries=3)
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Batch create embeddings with automatic batching for large inputs"""
        if not texts:
            return []
        
        # OpenAI allows up to 2048 inputs per request
        batch_size = 100  # Conservative batch size to avoid rate limits
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.debug(f"Creating embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")
            
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            # Sort by index to maintain order and pad embeddings
            sorted_embeddings = sorted(response.data, key=lambda x: x.index)
            all_embeddings.extend([self._pad_embedding(e.embedding) for e in sorted_embeddings])
        
        logger.info(f"Created {len(all_embeddings)} embeddings")
        return all_embeddings
    
    @retry_with_backoff(max_retries=3)
    async def create_embedding(self, text: str) -> List[float]:
        """Create a single embedding"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=[text]
        )
        return self._pad_embedding(response.data[0].embedding)

def get_embedding_provider() -> EmbeddingProvider:
    """Factory function to get the configured embedding provider"""
    provider_name = os.getenv('EMBEDDING_PROVIDER', 'openai').lower()
    
    if provider_name == 'openai':
        return OpenAIEmbeddingProvider()
    else:
        raise ValueError(f"Unknown embedding provider: {provider_name}")