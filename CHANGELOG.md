# Changelog

## [2.0.0] - 2024-09-12

### 🚀 Major Release: RAG Implementation

#### Added
- **Retrieval-Augmented Generation (RAG) System**
  - Real embeddings using OpenAI's text-embedding-3-small model
  - Semantic search with vector similarity (Pinecone)
  - Intelligent chunking strategy (1500 chars with 200 char overlap)
  - Query optimization with type detection and expansion

- **New Discord Commands**
  - `/search` - Semantic search with AI optimization
  - `/explore` - Interactive content exploration with depth levels
  - `/help` - Comprehensive command reference

- **Conversational AI for @ Mentions**
  - Chat history tracking (10 messages, 30-min timeout)
  - Smart detection of when to search transcripts
  - Hybrid responses combining conversation + RAG search

- **Enhanced Commands**
  - `/closerlook` - Now uses semantic search before AI analysis
  - Improved efficiency and accuracy across all commands

#### Changed
- Refactored from DeepSeek to OpenRouter as primary AI provider
- Updated chunking from 30,000 to 1,500 characters
- Improved embedding dimensions (1536 → 3072 with padding)
- Enhanced prompt engineering for better responses

#### Technical Improvements
- Modular provider pattern for AI services
- Query optimizer with multi-query processing
- Conversation manager for stateful interactions
- Docker support with proper versioning
- Comprehensive test coverage

#### Dependencies
- Added: langchain, tiktoken, openai
- Updated: OpenRouter integration
- Maintained: Pinecone vector database

## [1.0.0] - Previous Version
- Basic transcript ingestion and analysis
- Simple keyword-based search
- DeepSeek AI integration