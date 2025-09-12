# Developer Onboarding Guide - Miyu-Data Discord Bot

Welcome to the Miyu-Data Discord Bot project! This comprehensive guide will help you understand the codebase and get productive quickly.

## 1. Project Overview

### Purpose
Miyu-Data is an advanced Discord bot designed for meeting transcript analysis and knowledge management. It uses Retrieval-Augmented Generation (RAG) to provide intelligent search and conversational AI capabilities within Discord channels.

### Main Functionality
- **Transcript Ingestion**: Captures and stores Discord channel messages or uploaded text files
- **Semantic Search**: AI-powered search using vector embeddings
- **Conversational AI**: Natural language interactions with @ mentions
- **Meeting Analysis**: Extracts action items, decisions, and key topics
- **RAG System**: Combines vector search with LLM responses for accurate, context-aware answers

### Tech Stack
- **Language**: Python 3.11+
- **Framework**: discord.py (2.3.0+)
- **AI Providers**: 
  - OpenRouter (primary LLM provider)
  - OpenAI (embeddings)
- **Vector Database**: Pinecone
- **Containerization**: Docker & Docker Compose
- **Key Libraries**:
  - langchain (RAG orchestration)
  - pydantic (data validation)
  - tiktoken (token counting)
  - sentence-transformers (embeddings)

### Architecture Pattern
- **Modular Provider Pattern**: Swappable AI/embedding providers
- **Service Layer Architecture**: Separated concerns (AI, DB, Commands)
- **Event-Driven**: Discord event handlers for real-time interactions
- **RAG Pipeline**: Query → Optimization → Vector Search → LLM Enhancement

## 2. Repository Structure

```
miyu-data/
├── src/                      # Main source code
│   ├── __init__.py          # Bot initialization and setup
│   ├── commands.py          # Discord slash commands (/search, /ingest, etc.)
│   ├── events.py            # Discord event handlers (@ mentions)
│   ├── config.py            # Central configuration management
│   ├── ai_service.py        # AI/LLM service layer
│   ├── db_service.py        # Database and vector operations
│   ├── query_optimizer.py   # RAG query optimization
│   ├── conversation_manager.py # Chat history and context
│   ├── message_handler.py   # Discord message utilities
│   ├── models/              # Data models (unused currently)
│   └── providers/           # Provider implementations
│       ├── base.py          # Abstract base classes
│       ├── openrouter.py    # OpenRouter LLM provider
│       ├── deepseek.py      # Legacy DeepSeek provider
│       └── embeddings.py    # OpenAI embeddings provider
├── PRPs/                    # Project Reference Points (documentation)
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── Dockerfile              # Container definition
├── docker-compose.yml      # Orchestration config
├── VERSION                 # Semantic version (2.0.0)
└── CHANGELOG.md           # Version history
```

### Non-Standard Patterns
- **PRPs Directory**: Contains AI-generated documentation and planning
- **Dual Provider System**: Separate providers for LLM and embeddings
- **Dimension Padding**: Embeddings padded from 1536 to 3072 dimensions for compatibility

## 3. Getting Started

### Prerequisites
- Python 3.11 or higher
- Docker & Docker Compose (optional but recommended)
- Discord Developer Account
- API Keys:
  - Discord Bot Token
  - OpenRouter API Key
  - OpenAI API Key (for embeddings)
  - Pinecone API Key

### Environment Setup

1. **Clone the repository**:
```bash
git clone https://github.com/arealicehole/miyu-data.git
cd miyu-data
```

2. **Create virtual environment** (for local development):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Set up Pinecone index**:
- Create index with 3072 dimensions
- Use cosine similarity metric
- Name it according to your .env configuration

### Running Locally
```bash
# Direct Python execution
python main.py

# Using Docker
docker-compose up -d
```

### Running Tests
```bash
# Currently no formal test suite
# Test scripts can be created in root directory
python test_semantic_search.py  # Example test
```

### Building for Production
```bash
# Using build script
./build.sh 2.0.0

# Manual Docker build
docker build -t miyu-data-bot:2.0.0 .
```

## 4. Key Components

### Entry Points
- **main.py**: Simple launcher that calls `src.run()`
- **src/__init__.py**: Real entry point, initializes bot and registers commands

### Core Business Logic

#### Commands (`src/commands.py`)
- `/ingest` - Capture channel messages
- `/search` - Semantic search with RAG
- `/closerlook` - Deep analysis of topics
- `/explore` - Interactive content discovery
- `/autoreport` - Generate comprehensive reports

#### AI Service (`src/ai_service.py`)
- Manages LLM interactions
- Handles prompt engineering
- Implements retry logic
- Supports multiple providers

#### Database Service (`src/db_service.py`)
- Manages Pinecone vector database
- Handles chunking (1500 chars)
- Generates embeddings
- Performs semantic search

#### Query Optimizer (`src/query_optimizer.py`)
- Detects query types (factual, conceptual, temporal)
- Expands queries for better retrieval
- Multi-query processing
- Result ranking and boosting

### Configuration Management
- **src/config.py**: Centralized bot configuration
- **.env**: Environment variables (never commit!)
- **docker-compose.yml**: Container orchestration

### Authentication/Authorization
- Discord bot token authentication
- No user-level auth (relies on Discord permissions)
- API keys stored in environment variables

## 5. Development Workflow

### Git Conventions
- **Branch naming**: `feature/description`, `fix/issue-description`
- **Commit format**: Conventional commits (feat:, fix:, docs:, etc.)
- **Main branch**: `main` (protected)

### Creating a New Feature

1. **Create feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Implement feature**:
- Add new command in `src/commands.py`
- Register in `src/__init__.py`
- Update help text if needed

3. **Test locally**:
```bash
python main.py
# Test in Discord
```

4. **Commit and push**:
```bash
git add .
git commit -m "feat: add new amazing feature"
git push origin feature/your-feature-name
```

### Testing Requirements
- Manual testing in Discord required
- Create test scripts for complex features
- Verify RAG search returns relevant results
- Check conversation context preservation

### Code Style
- PEP 8 compliance
- Type hints encouraged
- Docstrings for public functions
- Clear variable names

### PR Process
1. Create PR against `main`
2. Include description of changes
3. List tested scenarios
4. Update VERSION if needed
5. Update CHANGELOG.md

### CI/CD Pipeline
- Currently no automated CI/CD
- Manual Docker builds
- Deploy via docker-compose

## 6. Architecture Decisions

### Design Patterns

#### Provider Pattern
```python
# Abstract base for swappable implementations
class AIProvider(ABC):
    async def chat_completion(self, request: AIRequest) -> AIResponse
```

#### Service Layer
- Separation of concerns
- Business logic in services
- Discord interaction in commands/events

#### RAG Pipeline
1. Query → Optimization
2. Multi-query expansion
3. Vector search
4. Result ranking
5. LLM enhancement

### State Management
- Stateless for commands
- Conversation history per channel (30-min timeout)
- No persistent user state

### Error Handling
- Retry decorator for AI calls
- Graceful fallbacks
- User-friendly error messages
- Comprehensive logging

### Security Measures
- API keys in environment variables
- No credential logging
- Input sanitization for Discord
- Rate limiting via Discord.py

### Performance Optimizations
- Chunking for large transcripts
- Embedding caching in Pinecone
- Async/await throughout
- Query result limiting

## 7. Common Tasks

### Adding a New Discord Command

1. **Create command in `src/commands.py`**:
```python
@bot.tree.command(name="mycommand", description="Description")
@app_commands.describe(param="Parameter description")
@handle_interaction_errors
async def mycommand(interaction: discord.Interaction, param: str):
    _ensure_services()
    # Implementation
    await interaction.followup.send("Response")
```

2. **Register in `src/__init__.py`**:
```python
from .commands import mycommand
bot.tree.add_command(mycommand)
```

### Adding a New AI Provider

1. **Create provider in `src/providers/`**:
```python
class NewProvider(AIProvider):
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        # Implementation
```

2. **Update `src/providers/__init__.py`**:
```python
if provider_name == "newprovider":
    return NewProvider(api_key)
```

### Modifying RAG Behavior

1. **Edit `src/query_optimizer.py`**:
- Adjust query types
- Modify expansion strategies
- Change scoring thresholds

2. **Update `src/db_service.py`**:
- Change chunk size (RAG_CHUNK_SIZE)
- Modify overlap (RAG_CHUNK_OVERLAP)
- Adjust similarity thresholds

### Debugging Common Issues

#### Bot Not Responding
```python
# Check logs
docker-compose logs -f

# Verify token
echo $DISCORD_TOKEN

# Check permissions in Discord
```

#### RAG Search Returns Nothing
```python
# Lower similarity threshold
min_score=0.2  # Instead of 0.3

# Check embeddings generation
logger.info(f"Embedding dimensions: {len(embedding)}")
```

#### Memory Issues
```bash
# Increase Docker memory
docker-compose down
# Edit docker-compose.yml - add memory limits
docker-compose up -d
```

## 8. Potential Gotchas

### Configuration Issues
- **Embedding Dimensions**: Must be 3072 (padded from 1536)
- **Pinecone Index**: Must exist before running
- **Model Names**: Some require specific format (e.g., "openai/gpt-4")

### Environment Variables
- **Required**: DISCORD_TOKEN, OPENROUTER_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY
- **Optional but Important**: YOLO_MODE, RAG_CHUNK_SIZE
- **Never commit .env file**

### External Dependencies
- Pinecone service must be accessible
- OpenAI API for embeddings (separate from LLM)
- Discord API rate limits apply

### Known Issues
- Embedding padding reduces similarity scores
- Large transcripts may timeout
- @ mentions fail without transcript

### Performance Bottlenecks
- Embedding generation (API calls)
- Large channel history ingestion
- Multiple query expansions

### Technical Debt
- No formal test suite
- Manual deployment process
- Hardcoded dimension padding
- Missing database migrations

## 9. Documentation and Resources

### Existing Documentation
- **README.md**: Basic setup and usage
- **DEPLOYMENT.md**: Docker deployment guide
- **CHANGELOG.md**: Version history
- **rag.md**: RAG implementation research
- **.env.example**: Configuration template

### API Documentation
- Discord.py: https://discordpy.readthedocs.io/
- OpenRouter: https://openrouter.ai/docs
- Pinecone: https://docs.pinecone.io/
- LangChain: https://python.langchain.com/

### Key Concepts
- **RAG**: Retrieval-Augmented Generation
- **Embeddings**: Vector representations of text
- **Semantic Search**: Meaning-based retrieval
- **Chunking**: Splitting text for processing

### Team Conventions
- Use conventional commits
- Document breaking changes
- Update VERSION file
- Keep CHANGELOG current

## 10. Next Steps - New Developer Checklist

### Week 1: Environment Setup
- [ ] Clone repository
- [ ] Set up Python environment
- [ ] Configure .env file
- [ ] Get API keys from team
- [ ] Run bot locally
- [ ] Join test Discord server

### Week 2: Understand Core Flow
- [ ] Ingest a test transcript
- [ ] Try all slash commands
- [ ] Test @ mention interactions
- [ ] Review conversation flow
- [ ] Understand RAG pipeline

### Week 3: Make First Contribution
- [ ] Fix a small bug or typo
- [ ] Add logging to a function
- [ ] Improve error message
- [ ] Create test script
- [ ] Submit first PR

### Week 4: Deep Dive
- [ ] Study query optimization
- [ ] Understand embedding process
- [ ] Review provider pattern
- [ ] Explore enhancement opportunities
- [ ] Propose new feature

### Resources for Learning
1. Read through `src/commands.py` for command patterns
2. Study `src/query_optimizer.py` for RAG logic
3. Review `src/conversation_manager.py` for chat handling
4. Examine `src/providers/` for abstraction patterns

### Getting Help
- Review existing code for patterns
- Check logs for debugging (`docker-compose logs`)
- Test in isolation with scripts
- Ask team about architecture decisions

## Tips for Success

1. **Start Small**: Make tiny changes first to understand the flow
2. **Use Logging**: Add logger.info() statements to trace execution
3. **Test Locally**: Always test in your own Discord server first
4. **Read the Prompts**: Understanding prompts in `ai_service.py` is key
5. **Monitor Costs**: Be aware of API usage, especially during development

## Conclusion

The Miyu-Data bot is a sophisticated RAG-powered Discord bot with room for growth. Focus on understanding the data flow from Discord → Commands → Services → Providers, and you'll quickly become productive.

Welcome to the team! 🚀