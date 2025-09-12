import logging
from .config import bot
from .ai_service import AIService
from .message_handler import split_and_send_message
from .db_service import DBService
from .query_optimizer import MultiQueryProcessor
from .conversation_manager import ConversationalRAGHandler
from discord.utils import find

# Defer initialization to avoid connection issues during imports
ai_service = None
db_service = None
query_processor = None
conversational_handler = None

def _ensure_services():
    """Initialize services if not already done"""
    global ai_service, db_service, query_processor, conversational_handler
    if ai_service is None:
        ai_service = AIService()
    if db_service is None:
        db_service = DBService()
    if query_processor is None:
        query_processor = MultiQueryProcessor(db_service)
    if conversational_handler is None:
        conversational_handler = ConversationalRAGHandler(ai_service, db_service, query_processor)

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
        _ensure_services()  # Initialize services if needed
        channel_id = message.channel.id
        logger.info(f"Channel ID: {channel_id}")

        # Check if any transcript exists for context
        async with message.channel.typing(): 
            transcript_exists = await db_service.get_channel_transcript(channel_id)
        
        if not transcript_exists:
            # Pure conversational mode without transcript context
            logger.info("No transcript found - using pure conversational mode")
            try:
                # Still use the conversational handler but it won't have transcript search available
                response = await conversational_handler.handle_mention(message, channel_id)
                await split_and_send_message(message.channel, response)
            except Exception as e:
                logger.error(f"Error in conversational response: {str(e)}")
                await message.reply("I'm here to help! However, no transcript has been ingested yet. Use /ingest or /ingest_file to add meeting transcripts that I can reference.")
            return
        
        logger.info(f"Transcript available for RAG search")
        
        try:
            logger.info("Processing with conversational RAG handler...")
            # Use the new conversational handler with RAG capabilities
            response = await conversational_handler.handle_mention(message, channel_id)
            logger.info(f"Generated response with context")
            await split_and_send_message(message.channel, response)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            await message.reply(f"Error processing request: {str(e)}")
    else:
        logger.info("Bot not mentioned, ignoring message")