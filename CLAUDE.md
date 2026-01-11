# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Miyu-Data is a RAG-powered Discord bot that analyzes meeting transcripts using AI. It ingests conversations from Discord channels or uploaded files, stores them in Pinecone vector database with semantic embeddings, and provides AI-powered analysis using DeepSeek V3.2 or OpenRouter.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py

# Build Docker image
./build.sh
# or
docker build -t miyu-data .
```

## Architecture

### Entry Point
- `main.py` → calls `run()` from `src/__init__.py`
- `src/__init__.py` bootstraps: loads env, creates bot, registers commands/events, runs bot

### Provider System (`src/providers/`)
Factory pattern for AI providers via `AI_PROVIDER` env var:
- `deepseek.py` - DeepSeek V3.2 API (supports thinking mode)
- `openrouter.py` - OpenRouter API
- `embeddings.py` - OpenAI embeddings for semantic search

### Core Services

**AIService** (`src/ai_service.py`)
- Wraps provider calls with retry logic
- Supports two modes via `thinking` parameter:
  - `deepseek-chat` (non-thinking): Fast responses, 8K max output, 30s timeout
  - `deepseek-reasoner` (thinking): Complex reasoning, 32K max output, 120s timeout
- `YOLO_MODE` env var disables all token limits

**DBService** (`src/db_service.py`)
- Pinecone vector database with semantic embeddings
- 1500 char chunks with OpenAI embeddings
- Metadata filtering by channel_id, transcript_name

**MultiQueryProcessor** (`src/query_optimizer.py`)
- Optimizes semantic search with query expansion
- Used by `/search`, `/closerlook`, `/explore`

### Discord Commands

All analysis commands support optional `thinking` parameter to override defaults:

| Command | Default Mode | Description |
|---------|--------------|-------------|
| `/ingest` | non-thinking | Ingest messages from channel history |
| `/ingest_file` | non-thinking | Upload .txt file as transcript |
| `/closerlook <topic>` | **thinking** | Semantic search + AI deep analysis |
| `/autoreport` | **thinking** | Generate detailed report for all items |
| `/execute_notes` | **thinking** | Execute AI tasks from notes_for_ai |
| `/search` | N/A | Pure semantic search (no AI) |
| `/explore` | thinking@depth3 | Interactive exploration with AI at depth 3 |
| `/help` | N/A | Show command help |

@mention queries use non-thinking mode for fast responses.

### Conversation Manager (`src/conversation_manager.py`)
- Maintains conversation history for @mention interactions
- 10 message context, 30 min timeout

## Environment Variables

Required in `.env`:
- `DISCORD_TOKEN` - Discord bot token
- `PINECONE_API_KEY` - Pinecone API key
- `OPENAI_API_KEY` - For embeddings

AI Provider (choose one):
- `AI_PROVIDER=deepseek` + `DEEPSEEK_API_KEY`
- `AI_PROVIDER=openrouter` + `OPENROUTER_API_KEY`

Optional:
- `AI_MODEL` - Override default model
- `YOLO_MODE=true` - Disable token limits

## Key Files

- `Dockerfile` - Container build (optimized ~198MB)
- `docker-compose.yml` - Local development
- `akash-simple.yaml` - Akash Network deployment
- `VERSION` - Semantic version tracking
