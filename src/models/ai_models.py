from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AIMessage(BaseModel):
    role: str
    content: str

class AIRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    max_tokens: int = 4096
    stream: bool = False
    temperature: Optional[float] = None

class AIResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None