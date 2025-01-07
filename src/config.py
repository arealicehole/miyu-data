import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Message constants
MAX_MESSAGE_LENGTH = 1900
INGESTION_BATCH_SIZE = 1000
