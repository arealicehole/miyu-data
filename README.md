# Miyu-Data: Discord Meeting Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
Miyu-Data is an advanced Discord bot that transforms meeting conversations into actionable insights. It leverages AI to analyze, categorize, and extract valuable information from meeting transcripts.

## 📚 Quick Links
- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Developer Guide](ONBOARDING.md)** - Complete onboarding documentation
- **[Deployment](DEPLOYMENT.md)** - Docker deployment instructions
- **[Changelog](CHANGELOG.md)** - What's new in v2.0.0

## ✨ New Features (v2.0.0)

### 🚀 RAG Implementation
- **Semantic Search** - AI-powered vector search using OpenAI embeddings
- **Query Optimization** - Intelligent query expansion and type detection
- **Multi-Query Processing** - Searches multiple query variations for comprehensive results
- **Conversational AI** - Natural @ mention interactions with chat history
- **Smart Context Detection** - Automatically determines when to search transcripts

### 🏗️ Technical Improvements
- **OpenRouter Integration** - Access 100+ AI models through unified API
- **Provider Pattern Architecture** - Swappable AI and embedding providers
- **Pydantic v2 Models** - Type-safe data handling throughout
- **Docker Support** - Containerized deployment with versioning
- **YOLO Mode** - Process unlimited transcript sizes without truncation

## Key Features
- **Intelligent Meeting Analysis**
  - Topic categorization
  - Action item extraction
  - Decision tracking
  - Critical update identification
- **AI-Powered Insights**
  - Multiple AI provider support (OpenRouter, DeepSeek)
  - Contextual understanding
  - Automated reporting
- **Efficient Data Management**
  - Pinecone vector database
  - Optimized storage (30k char chunks)
  - Fast retrieval with metadata filtering

## Architecture

### RAG System Overview
The v2.0.0 release introduces a sophisticated Retrieval-Augmented Generation (RAG) system:

1. **Ingestion Pipeline**: Transcripts → Chunking (1500 chars) → Embeddings → Vector Storage
2. **Query Processing**: User Query → Optimization → Multi-Query Expansion → Vector Search
3. **Response Generation**: Retrieved Chunks → Context Building → LLM Enhancement → Response

### Provider Pattern
```
BaseProvider (Abstract)
├── AIProvider Interface
│   ├── OpenRouterProvider (100+ models)
│   └── DeepSeekProvider (legacy)
└── EmbeddingProvider Interface
    └── OpenAIEmbeddingProvider (text-embedding-3-small)
```

### Service Layer Architecture
```
Discord Layer (commands.py, events.py)
     ↓
Service Layer (ai_service.py, db_service.py)
     ↓
Provider Layer (providers/)
     ↓
External APIs (OpenRouter, OpenAI, Pinecone)
```

### Core Components
```
src/
├── models/              # Pydantic v2 data models
│   ├── transcript.py    # Transcript data structures
│   └── ai_models.py     # AI request/response models
├── providers/           # AI provider implementations
│   ├── base.py         # Abstract interfaces
│   ├── openrouter.py   # OpenRouter LLM provider
│   ├── deepseek.py     # Legacy DeepSeek provider
│   └── embeddings.py   # OpenAI embeddings provider
├── ai_service.py       # AI orchestration layer
├── db_service.py       # Vector database operations
├── query_optimizer.py  # RAG query optimization
├── conversation_manager.py # Chat history management
├── commands.py         # Discord slash commands
├── events.py          # Discord event handlers
└── config.py          # Configuration management
```

## Getting Started

### Prerequisites
- Python 3.10+
- Discord Bot Token
- OpenRouter API Key (or DeepSeek API Key)
- Pinecone API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/miyu-data.git
cd miyu-data
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Environment Configuration

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token

# AI Provider Configuration
AI_PROVIDER=openrouter  # Options: openrouter, deepseek
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4o-mini  # Any OpenRouter model
APP_NAME=Miyu-Data Discord Bot
AI_MODEL=  # Optional: Override default model

# Database Configuration
PINECONE_API_KEY=your_pinecone_api_key

# Optional Features
YOLO_MODE=false  # Set to true for unlimited transcript processing
```

### Running the Bot

```bash
python main.py
```

## Discord Commands

### Core Commands

#### `/ingest`
Process channel messages into a searchable transcript.
- `transcript_name`: Name to identify this transcript
- `max_messages`: Maximum messages to ingest (0 for all)

Example: `/ingest transcript_name:"Team Meeting" max_messages:500`

#### `/ingest_file`
Upload and process a text file containing meeting notes.
- `file`: .txt file with the transcript
- `transcript_name`: Name to identify this transcript

### RAG-Powered Search Commands (v2.0.0)

#### `/search` 🔍
Semantic search with AI-powered query optimization.
- `query`: Natural language search query
- `max_results`: Number of results (default: 5)

Example: `/search query:"What decisions were made about authentication?"`

#### `/closerlook` 🔬
Deep analysis using semantic search + AI synthesis.
- `topic`: The topic to explore in depth

Example: `/closerlook topic:"mobile app development"`

#### `/explore` 🗺️
Interactive content discovery with guided exploration.
- `topic`: Optional starting topic (shows overview if empty)
- `depth`: Exploration depth 1-3 (default: 2)

Example: `/explore topic:"action items" depth:3`

### Analysis Commands

#### `/autoreport`
Generate a comprehensive report analyzing all aspects of the transcript.

#### `/execute_notes`
Execute all AI tasks that were noted in the transcript.

#### `/help`
Show all available commands and RAG search capabilities.

### Conversational AI

#### @ Mentions
Chat naturally with the bot using @ mentions. The bot maintains conversation history and intelligently searches transcripts when needed.

Examples:
- `@bot what did we discuss yesterday?`
- `@bot tell me more about that`
- `@bot search for action items`

## AI Provider Configuration

### OpenRouter (Recommended)
Access to 100+ models including GPT-4, Claude, Llama, and more.

```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4o-mini  # Or any model
```

Popular models:
- `openai/gpt-4o-mini` - Fast and capable
- `anthropic/claude-3-haiku` - Quick responses
- `google/gemini-pro` - Balanced performance
- `meta-llama/llama-3-70b` - Open source powerhouse

### DeepSeek (Legacy)
For backward compatibility:

```env
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key
```

## YOLO Mode 🚀

Enable unlimited transcript processing without the 16k character limit:

```env
YOLO_MODE=true
```

**Normal Mode (default)**:
- Transcripts truncated to ~16k characters for AI
- Protects against token limits
- Cost-effective

**YOLO Mode**:
- No truncation - processes entire transcripts
- Handles massive conversations
- ⚠️ Higher API costs
- ⚠️ May hit model token limits

## Database Architecture

### Pinecone Configuration
- **Index**: `miyu-testa`
- **Dimensions**: 3072
- **Metric**: Cosine similarity
- **Cloud**: AWS us-east-1

### Storage Strategy
- Transcripts chunked into 30k character segments
- Metadata includes all parsed sections
- Placeholder vectors (not using embeddings currently)
- Filter-based retrieval by channel ID

## Documentation

- **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
- **[Developer Onboarding](ONBOARDING.md)** - Complete developer guide
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment with Docker
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## Development

### Getting Started
- **Quick Setup**: See [QUICKSTART.md](QUICKSTART.md)
- **Full Developer Guide**: See [ONBOARDING.md](ONBOARDING.md)

### Code Quality
- **Type Safety**: Pydantic v2 models throughout
- **Clean Architecture**: Functions <20 lines
- **SOLID Principles**: Single responsibility, dependency injection
- **Provider Pattern**: Easy AI provider switching
- **RAG Pipeline**: Modular query optimization and retrieval

### Contributing Guidelines

1. **Fork & Clone**
   ```bash
   git clone https://github.com/yourusername/miyu-data.git
   cd miyu-data
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Follow Conventions**
   - Use conventional commits (feat:, fix:, docs:)
   - Update VERSION file for releases
   - Add tests for new features
   - Update CHANGELOG.md

4. **Test Thoroughly**
   ```bash
   python main.py  # Test locally
   # Test in Discord server
   ```

5. **Submit PR**
   - Clear description of changes
   - List tested scenarios
   - Update documentation if needed

### Testing

```bash
# Test OpenRouter integration
python test_openrouter.py

# Test semantic search
python test_semantic_search.py

# Test query optimization
python test_query_optimizer.py

# Test Pinecone connection
python test_pinecone.py
```

### Adding a New AI Provider

1. Create provider in `src/providers/`:
```python
from src.providers.base import AIProvider
from src.models.ai_models import AIRequest, AIResponse

class YourProvider(AIProvider):
    async def chat_completion(self, request: AIRequest) -> AIResponse:
        # Your implementation
        pass
```

2. Register in `src/providers/__init__.py`
3. Set `AI_PROVIDER=yourprovider` in `.env`

## Troubleshooting

### Common Issues

#### Bot Not Responding
- **Check Discord Token**: Verify `DISCORD_TOKEN` is correct
- **Permissions**: Ensure bot has message read/write permissions
- **Intents**: Enable message content intent in Discord Developer Portal
- **Logs**: Check console output or `docker-compose logs`

#### Search Returns No Results
- **Ingest First**: Ensure transcript was ingested with `/ingest`
- **Pinecone Index**: Verify index exists with 3072 dimensions
- **API Keys**: Check `OPENAI_API_KEY` for embeddings
- **Threshold**: Lower similarity threshold if needed

#### High API Costs
- **YOLO Mode**: Set `YOLO_MODE=false` to enable truncation
- **Chunk Size**: Reduce `RAG_CHUNK_SIZE` to 1000
- **Model Selection**: Use cheaper models like `gpt-4o-mini`
- **Query Limits**: Reduce `max_results` in searches

### Performance Tuning

#### Memory Usage
```env
# Reduce chunk size
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=100
```

#### Response Speed
- Use faster models (`claude-3-haiku`, `gpt-4o-mini`)
- Reduce search depth in `/explore`
- Limit conversation history window

#### Embedding Quality
- Ensure Pinecone index uses cosine similarity
- Verify dimension padding (1536 → 3072)
- Check embedding model consistency

### Connection Issues

#### Pinecone
- Verify API key is valid and active
- Check index name matches configuration
- Ensure index region is accessible
- Confirm dimension count (3072)

#### OpenRouter
- Verify API key format: `sk-or-v1-...`
- Check model name is valid
- Monitor rate limits and quotas
- Try different models if one fails

#### OpenAI (Embeddings)
- Separate API key from OpenRouter
- Check organization limits
- Verify model access (`text-embedding-3-small`)

## Environment Variables

### Required Configuration
```env
# Discord
DISCORD_TOKEN=your_discord_bot_token

# AI Provider (choose one)
AI_PROVIDER=openrouter  # or deepseek
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=openai/gpt-4o-mini

# Embeddings (required for RAG)
OPENAI_API_KEY=your_openai_key
EMBEDDING_MODEL=text-embedding-3-small

# Vector Database
PINECONE_API_KEY=your_pinecone_key
```

### Optional Configuration
```env
# Performance
YOLO_MODE=false  # true = no truncation
RAG_CHUNK_SIZE=1500  # Characters per chunk
RAG_CHUNK_OVERLAP=200  # Overlap for context

# Advanced
AI_MODEL=  # Override provider default
EMBEDDING_PROVIDER=openai  # Future: support others
```

## Docker Deployment

### Quick Deploy
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Build Custom Image
```bash
./build.sh 2.0.0  # Or specify version
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Roadmap

### In Progress 🚧
- [x] RAG implementation with semantic search
- [x] Conversational AI with chat history
- [x] Query optimization engine
- [x] Docker containerization

### Planned Features 📋
- [ ] Hybrid search (vector + keyword)
- [ ] Multi-language support
- [ ] Voice transcription integration
- [ ] Web dashboard for analytics
- [ ] Scheduled summary generation
- [ ] Export to PDF/Markdown
- [ ] Cost tracking per user/channel
- [ ] Custom embedding models
- [ ] Local LLM support (Ollama)
- [ ] Webhook integrations

### Future Vision 🔮
- [ ] Multi-modal analysis (images, documents)
- [ ] Real-time collaboration features
- [ ] Meeting action item tracking
- [ ] Integration with project management tools
- [ ] Automated follow-up reminders

## Contributing

We welcome contributions! Please see our [Developer Guide](ONBOARDING.md) for detailed information.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## Support

### Getting Help
- **Documentation**: Start with [QUICKSTART.md](QUICKSTART.md)
- **Developer Guide**: See [ONBOARDING.md](ONBOARDING.md)
- **Issues**: [GitHub Issues](https://github.com/arealicehole/miyu-data/issues)
- **Logs**: Use `docker-compose logs` or check console output

### Community
- Report bugs via GitHub Issues
- Request features with detailed use cases
- Share your experience and improvements

## License
MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments
- OpenRouter for unified AI model access
- OpenAI for embedding models
- Pinecone for vector database infrastructure
- Discord.py community for the excellent framework
- LangChain for RAG orchestration tools

## Version History

### v2.0.0 (Current)
- Complete RAG implementation
- Semantic search with vector embeddings
- Conversational AI with context
- Query optimization engine
- Docker support

### v1.0.0
- Initial release
- Basic transcript analysis
- Multi-provider support
- Pinecone integration

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Built with ❤️ for better meeting intelligence**

*Transform your Discord conversations into actionable insights with AI-powered RAG technology.*