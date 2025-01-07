# Discord Meeting Assistant Bot

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents
- [Features](#features)
- [Commands](#commands)
- [Setup](#setup)
- [Dependencies](#dependencies)
- [Project Structure](#project-structure)
- [Database Structure](#database-structure)
- [Error Handling & Performance](#error-handling--performance)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [License](#license)

## Features

- Ingest meeting transcripts from channel history or uploaded text files
- Generate comprehensive reports with categorized insights:
  - Main Conversation Topics
  - Content Ideas
  - Action Items
  - Notes for AI Tasks
  - Decisions Made
  - Critical Updates
- Execute AI tasks noted during meetings
- Provide detailed analysis of specific topics
- Efficient transcript storage and retrieval using Pinecone vector database
- Handles large transcripts through chunking and batch processing

## Commands

- `/ingest <transcript_name> [max_messages]`: Ingest messages from channel history with a name identifier (optional: limit message count)
- `/ingest_file <file> <transcript_name>`: Upload and ingest a .txt file containing a meeting transcript with a name identifier
- `/closerlook [topic]`: Get detailed analysis of a specific topic from the transcript
- `/autoreport`: Generate detailed reports for each analysis section
- `/execute_notes`: Execute all AI tasks that were noted in the transcript

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file with your API keys:
```
DISCORD_TOKEN=your_discord_token
ANTHROPIC_API_KEY=your_anthropic_api_key
PINECONE_API_KEY=your_pinecone_api_key
```
4. Run the bot:
```bash
python main.py
```

## Dependencies

- discord.py (>=2.3.0): Discord API wrapper
- python-dotenv (>=1.0.0): Environment variable management
- anthropic (>=0.3.0): Claude AI API client
- pinecone-client (>=2.2.4): Vector database client
- datetime (>=5.4): Date/time utilities

## Project Structure

- `main.py`: Entry point that initializes and runs the bot
- `src/`:
  - `__init__.py`: Bot initialization, event registration, and command setup
  - `commands.py`: Implementation of Discord slash commands with centralized error handling
  - `db_service.py`: Optimized Pinecone database operations with configurable parameters
  - `ai_service.py`: Claude AI integration for analysis and responses
  - `events.py`: Discord event handlers
  - `message_handler.py`: Utilities for handling long messages
  - `config.py`: Configuration settings

## Database Structure

The bot uses Pinecone vector database to store:
- Transcript chunks with metadata:
  - Transcript name for easy identification
  - Channel and timestamp information
  - Source tracking (channel history vs file upload)
  - Chunk index and total chunks for reconstruction
- Analysis sections stored with each chunk:
  - Conversation topics
  - Content ideas
  - Action items
  - AI task notes
  - Decisions made
  - Critical updates
- Configurable parameters for optimization:
  - Vector dimension size
  - Chunk size for transcript splitting
  - Batch size for database operations
  - Query result limits

## Error Handling & Performance

- Centralized error handling through decorators:
  - Consistent error messages and recovery
  - Automatic typing indicator management
  - Graceful handling of Discord API limits
- Performance optimizations:
  - Pre-computed values for frequent operations
  - Configurable batch sizes for processing
  - Efficient database querying with filters
  - Rate limit prevention through controlled delays
- Robust input validation:
  - File type checking for uploads
  - Parameter validation for commands
  - Graceful handling of missing data
- Comprehensive logging:
  - Detailed error tracking
  - Operation progress updates
  - Performance monitoring

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeatureName`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeatureName`)
5. Open a pull request

Please ensure your code follows PEP 8 guidelines and includes appropriate tests.

## Roadmap

- [ ] Add support for multiple AI providers
- [ ] Implement transcript summarization
- [ ] Add meeting scheduling features
- [ ] Develop web dashboard for analytics
- [ ] Create mobile-friendly interface
- [ ] Add multi-language support

## FAQ

**Q: What permissions does the bot need?**
A: The bot requires permissions to read messages, send messages, and manage messages in the channels where it will operate.

**Q: How do I handle API rate limits?**
A: The bot includes built-in rate limit handling and will automatically retry requests when possible.

**Q: Can I use a different vector database?**
A: Currently, only Pinecone is supported, but we plan to add support for other databases in the future.

**Q: How are transcripts stored and secured?**
A: Transcripts are stored as vectors in Pinecone with metadata. No raw transcripts are stored permanently.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
