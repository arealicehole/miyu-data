# Deployment Guide - Miyu-Data Bot v2.0.0

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Discord Bot Token
- OpenRouter API Key
- OpenAI API Key (for embeddings)
- Pinecone API Key & Index

### 1. Clone the Repository
```bash
git clone https://github.com/arealicehole/miyu-data.git
cd miyu-data
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Build Docker Image
```bash
# Using the build script
./build.sh 2.0.0

# Or manually
docker build -t miyu-data-bot:2.0.0 -t miyu-data-bot:latest .
```

### 4. Run with Docker Compose
```bash
# Start the bot
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

## 📦 Docker Image Tags

- `miyu-data-bot:latest` - Latest stable version
- `miyu-data-bot:2.0.0` - Specific version with RAG implementation
- `miyu-data-bot:1.0.0` - Legacy version without RAG

## 🔧 Configuration

### Required Environment Variables
```env
# Discord
DISCORD_TOKEN=your_discord_bot_token

# AI Provider (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_key
AI_PROVIDER=openrouter
AI_MODEL=anthropic/claude-3.5-sonnet

# Embeddings (OpenAI)
OPENAI_API_KEY=your_openai_key
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=your_index_name
```

### Optional Settings
```env
# RAG Configuration
RAG_CHUNK_SIZE=1500
RAG_CHUNK_OVERLAP=200

# Performance
YOLO_MODE=true  # Disable truncation limits
```

## 🐳 Docker Commands

### Build
```bash
# Build with specific version
docker build -t miyu-data-bot:2.0.0 .

# Build with multiple tags
docker build -t miyu-data-bot:2.0.0 -t miyu-data-bot:latest .
```

### Run
```bash
# Run with docker-compose (recommended)
docker-compose up -d

# Run standalone
docker run -d \
  --name miyu-bot \
  --env-file .env \
  --restart unless-stopped \
  miyu-data-bot:2.0.0
```

### Manage
```bash
# View logs
docker logs miyu-bot -f

# Stop container
docker stop miyu-bot

# Remove container
docker rm miyu-bot

# Check status
docker ps -a | grep miyu
```

## 📊 Health Monitoring

The Docker image includes a health check that runs every 30 seconds.

```bash
# Check health status
docker inspect miyu-bot --format='{{.State.Health.Status}}'

# View health check logs
docker inspect miyu-bot --format='{{json .State.Health}}' | jq
```

## 🔄 Updating

1. Pull latest changes:
```bash
git pull origin main
```

2. Rebuild image:
```bash
./build.sh $(cat VERSION)
```

3. Restart container:
```bash
docker-compose down
docker-compose up -d
```

## 🐛 Troubleshooting

### Bot not connecting to Discord
- Verify `DISCORD_TOKEN` is correct
- Check bot has proper permissions in Discord server

### RAG search not working
- Ensure `OPENAI_API_KEY` is valid
- Verify Pinecone index exists and is accessible
- Check embedding dimensions match (3072)

### High memory usage
- Adjust Docker memory limits in `docker-compose.yml`
- Consider reducing `RAG_CHUNK_SIZE`

### View detailed logs
```bash
# All logs
docker-compose logs

# Last 100 lines
docker-compose logs --tail=100

# Follow logs
docker-compose logs -f
```

## 📚 Version History

- **2.0.0** - RAG implementation with semantic search
- **1.0.0** - Initial release with basic transcript analysis

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.