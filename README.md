# Miyu-Data: Discord Meeting Intelligence Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
Miyu-Data is an advanced Discord bot designed to transform meeting conversations into actionable insights. It leverages AI to analyze, categorize, and extract valuable information from meeting transcripts.

## Key Features
- **Intelligent Meeting Analysis**
  - Topic categorization
  - Action item extraction
  - Decision tracking
  - Critical update identification
- **AI-Powered Insights**
  - Claude AI integration
  - Contextual understanding
  - Automated reporting
- **Efficient Data Management**
  - Pinecone vector database
  - Optimized storage
  - Fast retrieval

## Core Components
- **main.py**: Bot entry point
- **src/**: Contains all core functionality
  - ai_service.py: AI integration
  - commands.py: Discord commands
  - db_service.py: Database operations
  - events.py: Event handlers
  - message_handler.py: Message utilities
  - config.py: Configuration settings

## Getting Started
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Configure environment variables in `.env`
4. Run the bot:
```bash
python main.py
```

## Usage
### Basic Commands
- `/ingest`: Process channel messages
- `/ingest_file`: Upload and process text files
- `/closerlook`: Analyze specific topics
- `/autoreport`: Generate comprehensive reports
- `/execute_notes`: Process AI task notes

## Database Architecture
Miyu-Data uses Pinecone for efficient data storage:
- Vector-based transcript storage
- Metadata-rich organization
- Optimized query performance
- Configurable parameters

## Development
### Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

### Coding Standards
- Follow PEP 8 guidelines
- Include comprehensive tests
- Maintain clear documentation

## Roadmap
- Multi-AI provider support
- Enhanced summarization
- Meeting scheduling
- Web dashboard
- Mobile interface
- Multi-language support

## License
MIT License - See [LICENSE](LICENSE) for details
