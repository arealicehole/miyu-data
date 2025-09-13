#!/usr/bin/env python3
"""
One-time script to ingest README into Pinecone for /help command reference
"""
import asyncio
import os
from dotenv import load_dotenv
from src.db_service import DBService

async def ingest_readme():
    load_dotenv()
    
    # Initialize database service
    db_service = DBService()
    
    # Read README content
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Add special marker for help command
    marked_content = "[BOT_DOCUMENTATION]\n" + readme_content
    
    # Save to database with special name
    await db_service.save_transcript(
        channel_id=0,  # Special channel ID for documentation
        transcript=marked_content,
        source="channel",  # Use 'channel' as source type
        transcript_name="bot-documentation-readme"
    )
    
    print("✅ README successfully ingested into Pinecone!")
    print("The bot can now reference documentation when users use /help")

if __name__ == "__main__":
    asyncio.run(ingest_readme())