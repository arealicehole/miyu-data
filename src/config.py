import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openrouter')

# Embedding configuration  
EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')

# RAG configuration
RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '1500'))
RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '200'))

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Message constants
MAX_MESSAGE_LENGTH = 1900
INGESTION_BATCH_SIZE = 1000
