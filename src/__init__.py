import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openrouter')

# Check for required tokens based on provider
if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables.")
    raise ValueError("Missing DISCORD_TOKEN in environment variables.")

# Check AI provider requirements
if AI_PROVIDER == 'openrouter':
    if not os.getenv('OPENROUTER_API_KEY'):
        logger.error("OPENROUTER_API_KEY not found in environment variables.")
        raise ValueError("Missing OPENROUTER_API_KEY for OpenRouter provider.")
elif AI_PROVIDER == 'deepseek':
    if not os.getenv('DEEPSEEK_API_KEY'):
        logger.error("DEEPSEEK_API_KEY not found in environment variables.")
        raise ValueError("Missing DEEPSEEK_API_KEY for DeepSeek provider.")
else:
    logger.warning(f"Unknown AI provider: {AI_PROVIDER}. Defaulting to OpenRouter.")

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Message constants
MAX_MESSAGE_LENGTH = 1900
INGESTION_BATCH_SIZE = 1000

# Import event handlers and commands
from .events import on_message, set_bot_ready
from .commands import closerlook, ingest, ingest_file, autoreport, execute_notes, search, explore, help_command

# Explicitly add commands to the bot's command tree
bot.tree.add_command(closerlook)
bot.tree.add_command(ingest)
bot.tree.add_command(ingest_file)
bot.tree.add_command(autoreport)
bot.tree.add_command(execute_notes)
bot.tree.add_command(search)
bot.tree.add_command(explore)
bot.tree.add_command(help_command)

# Register event handlers
@bot.event
async def on_ready():
    if bot.user is None:
        logger.error("bot.user is None in on_ready. This should not happen.")
        return
    logger.info(f'{bot.user} (ID: {bot.user.id}) has connected to Discord!')
    set_bot_ready(bot.user.id)
    try:
        logger.info("Starting to sync commands...")
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s):")
        for command in synced:
            logger.info(f"  - {command.name}")
        logger.info("Bot is now fully ready!")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}", exc_info=True)

bot.event(on_message)

def run():
    logger.info("Starting bot...")
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
