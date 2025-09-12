# Quick Start Guide - Miyu-Data Bot

Get the bot running in 5 minutes! 🚀

## Prerequisites
- Python 3.11+
- Discord Bot Token
- API Keys (OpenRouter, OpenAI, Pinecone)

## Fast Setup

### 1. Clone & Navigate
```bash
git clone https://github.com/arealicehole/miyu-data.git
cd miyu-data
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your keys:
```env
DISCORD_TOKEN=your_discord_bot_token
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
```

### 4. Run the Bot
```bash
python main.py
```

## Docker Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/arealicehole/miyu-data.git
cd miyu-data
cp .env.example .env
# Edit .env with your API keys
```

### 2. Build & Run
```bash
docker-compose up -d
```

### 3. Check Logs
```bash
docker-compose logs -f
```

## First Steps in Discord

1. **Invite bot to your server** with appropriate permissions
2. **Ingest a transcript**: `/ingest "Test Meeting" 100`
3. **Search content**: `/search "important topics"`
4. **Chat with bot**: `@bot what did we discuss?`

## Essential Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/ingest` | Capture channel messages | `/ingest "Meeting" 500` |
| `/search` | Semantic search | `/search "action items"` |
| `/closerlook` | Analyze topic | `/closerlook "decisions"` |
| `/help` | Show all commands | `/help` |

## Environment Variables (Minimum Required)

```env
# Discord
DISCORD_TOKEN=your_bot_token

# AI Provider
OPENROUTER_API_KEY=your_key
AI_PROVIDER=openrouter

# Embeddings
OPENAI_API_KEY=your_key

# Vector Database
PINECONE_API_KEY=your_key
```

## Common Issues

### Bot not responding?
- Check DISCORD_TOKEN is correct
- Verify bot has message permissions
- Ensure bot is online in Discord

### Search returns nothing?
- Confirm transcript was ingested first
- Check Pinecone index exists (3072 dimensions)
- Verify OPENAI_API_KEY is valid

### High API costs?
- Set `YOLO_MODE=false` in .env
- Reduce `RAG_CHUNK_SIZE` to 1000

## Next Steps

1. Read [ONBOARDING.md](ONBOARDING.md) for detailed documentation
2. Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
3. Check [CHANGELOG.md](CHANGELOG.md) for version features

## Getting Help

- **Logs**: `docker-compose logs` or check console output
- **Documentation**: See `/docs` and `*.md` files
- **Issues**: https://github.com/arealicehole/miyu-data/issues

---

**Ready to go!** The bot should now be responding in your Discord server. Try `/help` for all available commands.