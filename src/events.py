import logging
from .config import bot
from .ai_service import AIService
from .message_handler import split_and_send_message
from .db_service import DBService
from discord.utils import find

ai_service = AIService()
db_service = DBService()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_ready = False
bot_id = None

def set_bot_ready(user_id):
    global bot_ready, bot_id
    bot_ready = True
    bot_id = user_id
    logger.info(f"Bot is now ready to process messages! Bot ID: {bot_id}")

async def on_message(message):
    global bot_ready, bot_id
    logger.info(f"Received message: {message.content}")
    logger.info(f"Message author: {message.author}")
    logger.info(f"Bot mentions: {message.mentions}")
    logger.info(f"Bot ready: {bot_ready}, Bot ID: {bot_id}")
    
    if not bot_ready or bot_id is None:
        logger.warning("Bot is not fully ready yet, ignoring message")
        return

    if message.author.id == bot_id:
        logger.info("Message is from the bot, ignoring")
        return

    bot_mentioned = (
        bot_id in [mention.id for mention in message.mentions] or
        f'<@{bot_id}>' in message.content or
        f'<@!{bot_id}>' in message.content
    )

    logger.info(f"Bot ID: {bot_id}, Mentions: {[mention.id for mention in message.mentions]}, Content: {message.content}")
    logger.info(f"Bot mentioned: {bot_mentioned}")

    if bot_mentioned:
        logger.info("Bot mentioned, processing message...")
        channel_id = message.channel.id
        logger.info(f"Channel ID: {channel_id}")

        async with message.channel.typing(): 
            transcript = await db_service.get_channel_transcript(channel_id)
        
        if not transcript:
            logger.info("No transcript found")
            await message.reply("No transcript has been ingested for this channel. Use /ingest or /ingest_file first!")
            return
        
        logger.info(f"Transcript found, length: {len(transcript)}")
        
        try:
            logger.info("Generating response...")
            response = await ai_service.get_response(transcript, message.content)
            logger.info(f"Generated response: {response}")
            await split_and_send_message(message.channel, response)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            await message.reply(f"Error processing request: {str(e)}")
    else:
        logger.info("Bot not mentioned, ignoring message")