# Refactoring Plan for Miyu-Data Discord Bot

## Executive Summary
This refactoring plan addresses architectural improvements, code quality issues, and integration of OpenRouter as the AI provider. The plan focuses on vertical slice architecture, single responsibility principle, and type safety with Pydantic v2.

## Priority Issues & Fixes

### 1. 🔴 HIGH PRIORITY: Missing Pydantic Models for Type Safety

**Location:** All modules lack structured data models  
**Problem:** No type-safe data contracts between layers, making the code error-prone and hard to maintain  
**Priority:** HIGH

**Fix:** Create Pydantic v2 models for all data structures

```python
# src/models/transcript.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class TranscriptChunk(BaseModel):
    channel_id: str
    timestamp: datetime
    source: Literal["channel", "file"]
    transcript_name: str
    chunk_index: int
    total_chunks: int
    text: str

class TranscriptSections(BaseModel):
    conversation_topics: List[str] = Field(default_factory=list)
    content_ideas: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    notes_for_ai: List[str] = Field(default_factory=list)
    decisions_made: List[str] = Field(default_factory=list)
    critical_updates: List[str] = Field(default_factory=list)

class TranscriptMetadata(BaseModel):
    channel_id: str
    timestamp: datetime
    source: Literal["channel", "file"]
    type: Literal["transcript"] = "transcript"
    transcript_name: str
    chunk_index: int
    total_chunks: int
    text: str
    sections: TranscriptSections

# src/models/ai_models.py
class AIRequest(BaseModel):
    model: str
    messages: List[dict]
    max_tokens: int = 4096
    stream: bool = False
    temperature: Optional[float] = None

class AIResponse(BaseModel):
    content: str
    model: str
    usage: Optional[dict] = None
```

### 2. 🔴 HIGH PRIORITY: OpenRouter Integration for AI Provider Flexibility

**Location:** `src/ai_service.py`  
**Problem:** Hardcoded to DeepSeek API, no provider flexibility  
**Priority:** HIGH

**Fix:** Implement OpenRouter integration with provider abstraction

```python
# src/providers/base.py
from abc import ABC, abstractmethod
from typing import Optional
from src.models.ai_models import AIRequest, AIResponse

class AIProvider(ABC):
    @abstractmethod
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        pass

# src/providers/openrouter.py
from openai import AsyncOpenAI
from src.providers.base import AIProvider
from src.models.ai_models import AIRequest, AIResponse
import os

class OpenRouterProvider(AIProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv('OPENROUTER_API_KEY'),
        )
        self.default_model = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
        
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        try:
            response = await self.client.chat.completions.create(
                model=request.model or self.default_model,
                messages=request.messages,
                max_tokens=request.max_tokens,
                stream=request.stream,
                extra_headers={
                    "HTTP-Referer": os.getenv('APP_URL', 'https://miyu-data.discord'),
                    "X-Title": "Miyu-Data Discord Bot",
                }
            )
            return AIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None
            )
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {str(e)}")

# src/providers/deepseek.py (for backward compatibility)
class DeepSeekProvider(AIProvider):
    # Existing DeepSeek implementation refactored to use AIProvider interface
    pass
```

### 3. 🔴 HIGH PRIORITY: Functions >20 Lines Need Decomposition

**Location:** Multiple functions exceed 20 lines  
**Problem:** Complex functions violate single responsibility and are hard to test  
**Priority:** HIGH

**Specific Functions to Refactor:**

#### `ai_service.py` - Methods with 30-45 lines each
```python
# Refactor get_closer_look, generate_comprehensive_report, get_response
# Split into smaller methods:

class AIService:
    async def get_closer_look(self, transcript: str, topic: str) -> str:
        request = self._build_closer_look_request(transcript, topic)
        return await self._execute_request(request)
    
    def _build_closer_look_request(self, transcript: str, topic: str) -> AIRequest:
        transcript = self._truncate_transcript(transcript)
        return AIRequest(
            model=self.model,
            messages=[
                {"role": "system", "content": self.CLOSER_LOOK_PROMPT},
                {"role": "user", "content": self._format_closer_look_query(transcript, topic)}
            ],
            max_tokens=self.max_tokens
        )
    
    def _truncate_transcript(self, transcript: str) -> str:
        max_length = self.max_tokens * 4
        return transcript[:max_length] if len(transcript) > max_length else transcript
    
    async def _execute_request(self, request: AIRequest) -> str:
        response = await self.provider.chat_completion(request)
        return response.content
```

#### `db_service.py` - `save_transcript` method (50+ lines)
```python
# Split into smaller methods:
class DBService:
    async def save_transcript(self, channel_id: int, transcript: str, 
                             source: str = "channel", transcript_name: str = None):
        metadata = await self._prepare_metadata(channel_id, transcript, source, transcript_name)
        vectors = self._create_vectors(transcript, metadata)
        await self._upsert_vectors(vectors)
        return f"{channel_id}_{metadata.timestamp}"
    
    async def _prepare_metadata(self, channel_id: int, transcript: str, 
                               source: str, transcript_name: str) -> TranscriptMetadata:
        # Generate report and parse sections
        pass
    
    def _create_vectors(self, transcript: str, metadata: TranscriptMetadata) -> List:
        # Create vector chunks
        pass
    
    async def _upsert_vectors(self, vectors: List):
        # Batch upsert with retry logic
        pass
```

### 4. 🟡 MEDIUM PRIORITY: Long Files Need Decomposition

**Location:** `db_service.py` (260 lines), `commands.py` (167 lines)  
**Problem:** Files too long, mixing multiple concerns  
**Priority:** MEDIUM

**Fix:** Split into vertical slices by feature

```
src/
├── features/
│   ├── transcript_ingestion/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── commands.py
│   ├── ai_analysis/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── commands.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── service.py
│   │   └── commands.py
│   └── storage/
│       ├── __init__.py
│       ├── models.py
│       └── pinecone_service.py
```

### 5. 🟡 MEDIUM PRIORITY: Cross-Feature Imports Violating Vertical Slices

**Location:** Circular dependencies between modules  
**Problem:** `db_service.py` imports from `ai_service.py`, creating tight coupling  
**Priority:** MEDIUM

**Fix:** Use dependency injection and interfaces

```python
# src/features/storage/interfaces.py
from abc import ABC, abstractmethod

class IReportGenerator(ABC):
    @abstractmethod
    async def generate_report(self, transcript: str) -> str:
        pass

# src/features/storage/pinecone_service.py
class PineconeService:
    def __init__(self, report_generator: IReportGenerator):
        self.report_generator = report_generator
        # ... rest of init
    
    async def save_transcript(self, ...):
        # Use injected report_generator instead of direct import
        report = await self.report_generator.generate_report(transcript)
```

### 6. 🟡 MEDIUM PRIORITY: Classes with Multiple Responsibilities

**Location:** `DBService` class  
**Problem:** Handles storage, parsing, querying, and report generation  
**Priority:** MEDIUM

**Fix:** Split into single-responsibility services

```python
# src/features/storage/transcript_storage.py
class TranscriptStorage:
    """Only handles storage operations"""
    async def save(self, transcript: TranscriptChunk) -> str:
        pass
    
    async def get(self, channel_id: int) -> str:
        pass

# src/features/reporting/report_parser.py
class ReportParser:
    """Only handles report parsing"""
    def parse_sections(self, report: str) -> TranscriptSections:
        pass

# src/features/storage/vector_service.py
class VectorService:
    """Only handles vector operations"""
    def create_vectors(self, text: str) -> List:
        pass
```

### 7. 🟢 LOW PRIORITY: Missing Type Hints

**Location:** Throughout codebase  
**Problem:** Many functions missing return type hints and parameter types  
**Priority:** LOW

**Fix:** Add comprehensive type hints

```python
# Examples of missing type hints to add:
from typing import List, Dict, Optional, Tuple

async def process_channel_messages(
    interaction: discord.Interaction, 
    max_messages: int
) -> Tuple[str, int]:  # Added return type
    pass

def parse_report_sections(self, report: str) -> Dict[str, List[str]]:  # Added return type
    pass
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. Create Pydantic models for all data structures
2. Add comprehensive type hints throughout
3. Install required dependencies (openai, pydantic)

### Phase 2: AI Provider Integration (Week 1-2)
1. Implement AIProvider abstract base class
2. Create OpenRouterProvider implementation
3. Refactor existing DeepSeek code to use provider pattern
4. Add provider selection configuration

### Phase 3: Function Decomposition (Week 2)
1. Break down all functions >20 lines
2. Extract methods following single responsibility
3. Ensure each function does one thing well

### Phase 4: Vertical Slice Architecture (Week 3)
1. Reorganize code into feature-based folders
2. Implement dependency injection
3. Remove cross-feature imports
4. Create clear boundaries between features

### Phase 5: Testing & Documentation (Week 3-4)
1. Add unit tests for refactored components
2. Update documentation
3. Create integration tests for OpenRouter

## Environment Variable Updates

Add to `.env`:
```
# AI Provider Configuration
AI_PROVIDER=openrouter  # Options: openrouter, deepseek
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini  # Or any model from OpenRouter
APP_URL=https://your-discord-bot-url
APP_NAME=Miyu-Data Discord Bot

# Keep for backward compatibility
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## Dependencies to Add

Update `requirements.txt`:
```
discord.py>=2.3.0
python-dotenv>=1.0.0
requests>=2.31.0
pinecone-client>=2.2.4
datetime>=5.4
pydantic>=2.0.0
openai>=1.0.0  # For OpenRouter integration
```

## Benefits After Refactoring

1. **Type Safety**: Pydantic models prevent runtime errors
2. **Provider Flexibility**: Easy switching between AI providers
3. **Maintainability**: Smaller, focused functions easier to understand
4. **Testability**: Isolated components can be unit tested
5. **Scalability**: Vertical slices allow independent feature development
6. **Cost Optimization**: OpenRouter automatically selects cost-effective models

## Risk Mitigation

- Keep backward compatibility with existing DeepSeek integration
- Implement feature flags for gradual rollout
- Maintain comprehensive logging during migration
- Create rollback plan for each phase

## Success Metrics

- Reduce average function length from 35 lines to <15 lines
- Achieve 100% type coverage with Pydantic models
- Reduce file sizes to <150 lines per file
- Zero circular dependencies
- 90%+ test coverage for new code

## Next Steps

1. Review and approve this plan
2. Set up development branch
3. Begin Phase 1 implementation
4. Create test environment with OpenRouter account
5. Schedule code review checkpoints