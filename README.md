# Miyu-Data: Discord Meeting Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
Miyu-Data is an advanced Discord bot that transforms meeting conversations into actionable insights. It leverages AI to analyze, categorize, and extract valuable information from meeting transcripts.

## ✨ New Features (v2.0)
- **🚀 OpenRouter Integration** - Access 100+ AI models through a unified API
- **🏗️ Provider Pattern Architecture** - Easily switch between AI providers
- **📦 Pydantic v2 Models** - Type-safe data handling throughout
- **🎯 YOLO Mode** - Process unlimited transcript sizes without truncation
- **♻️ Refactored Codebase** - All functions <20 lines, following single responsibility

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
```
src/
├── models/          # Pydantic v2 data models
│   ├── transcript.py
│   └── ai_models.py
├── providers/       # AI provider implementations
│   ├── base.py     # Abstract provider interface
│   ├── openrouter.py
│   └── deepseek.py
├── ai_service.py    # AI service with provider pattern
├── db_service.py    # Pinecone vector storage
├── commands.py      # Discord slash commands
├── events.py        # Discord event handlers
└── config.py        # Configuration management
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

### `/ingest`
Process channel messages into a searchable transcript.
- `transcript_name`: Name to identify this transcript
- `max_messages`: Maximum messages to ingest (0 for all)

Example: `/ingest transcript_name:"Team Meeting" max_messages:500`

### `/ingest_file`
Upload and process a text file containing meeting notes.
- `file`: .txt file with the transcript
- `transcript_name`: Name to identify this transcript

### `/closerlook`
Get detailed analysis of a specific topic from the transcript.
- `topic`: The topic to explore in depth

Example: `/closerlook topic:"mobile app development"`

### `/autoreport`
Generate a comprehensive report analyzing all aspects of the transcript.

### `/execute_notes`
Execute all AI tasks that were noted in the transcript.

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

## Development

### Code Quality
- **Type Safety**: Pydantic v2 models throughout
- **Clean Architecture**: Functions <20 lines
- **SOLID Principles**: Single responsibility, dependency injection
- **Provider Pattern**: Easy AI provider switching

### Testing

```bash
# Test OpenRouter integration
python test_openrouter.py

# Test refactoring validation
python test_refactoring.py

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

### Pinecone Connection Issues
- Verify API key is valid and active
- Check index name matches (`miyu-testa`)
- Ensure index region is accessible

### OpenRouter Errors
- Verify API key format: `sk-or-v1-...`
- Check model name is valid
- Monitor rate limits

### Discord Bot Not Responding
- Ensure bot has proper permissions
- Check bot is invited to server
- Verify intents are enabled in Discord Developer Portal

## Roadmap
- [ ] Real embeddings for semantic search
- [ ] Multi-model routing (different models for different tasks)
- [ ] Streaming responses
- [ ] Cost tracking and optimization
- [ ] Web dashboard
- [ ] Export to various formats (PDF, Markdown, etc.)
- [ ] Scheduled meeting summaries
- [ ] Integration with calendar systems

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

## License
MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments
- OpenRouter for unified AI model access
- Pinecone for vector database infrastructure
- Discord.py community for the excellent framework

---

**Built with ❤️ for better meeting intelligence**