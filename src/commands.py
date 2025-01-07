import discord
from discord import app_commands
import asyncio
import functools
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from .config import bot, INGESTION_BATCH_SIZE
from .ai_service import AIService
from .message_handler import split_and_send_message
from .db_service import DBService

ai_service = AIService()
db_service = DBService()

def handle_interaction_errors(func: Callable) -> Callable:
    """Decorator to handle common interaction error patterns"""
    @functools.wraps(func)
    async def wrapper(interaction: discord.Interaction, *args, **kwargs):
        try:
            await interaction.response.defer(thinking=True)
        except discord.errors.NotFound:
            await interaction.followup.send("Processing your request...", ephemeral=True)
            return
        
        async with interaction.channel.typing():
            try:
                await func(interaction, *args, **kwargs)
            except Exception as e:
                await interaction.followup.send(f"Error processing request: {str(e)}")
    
    return wrapper

async def check_transcript_exists(interaction: discord.Interaction) -> bool:
    """Check if a transcript exists for the channel"""
    transcript = await db_service.get_channel_transcript(interaction.channel.id)
    if not transcript:
        await interaction.followup.send("No transcript has been ingested for this channel. Use /ingest or /ingest_file first!")
        return False
    return True

async def process_channel_messages(interaction: discord.Interaction, max_messages: int) -> tuple[str, int]:
    """Process and collect messages from channel history"""
    messages = []
    message_count = 0
    channel = interaction.channel
    
    async for message in channel.history(limit=None if max_messages == 0 else max_messages):
        messages.append(f"{message.author.name}: {message.content}")
        message_count += 1
        
        if message_count % INGESTION_BATCH_SIZE == 0:
            await interaction.followup.send(f"Ingested {message_count} messages so far...", ephemeral=True)
        
        await asyncio.sleep(0.01)
        
        if 0 < max_messages <= message_count:
            break
    
    return "\n".join(reversed(messages)), message_count

@bot.tree.command(name="execute_notes", description="Execute all AI tasks noted from the transcript")
@handle_interaction_errors
async def execute_notes(interaction: discord.Interaction):
    channel_id = interaction.channel.id
    
    if not await check_transcript_exists(interaction):
        return
    
    transcript = await db_service.get_channel_transcript(channel_id)
    notes = await db_service.get_section_items(channel_id, 'notes_for_ai')
    
    if not notes:
        await interaction.followup.send("No AI tasks were noted in the transcript!")
        return
    
    # Execute each note
    await interaction.followup.send(f"Found {len(notes)} AI tasks to execute. Processing each one...")
    
    for i, note in enumerate(notes, 1):
        await interaction.followup.send(f"**Task {i}/{len(notes)}:** {note}")
        response = await ai_service.get_response(transcript, note)
        await split_and_send_message(interaction.channel, response)
        await asyncio.sleep(1)  # Prevent rate limiting
    
    await interaction.followup.send("✅ All AI tasks have been executed!")

@bot.tree.command(name="closerlook", description="Get a closer look at a specific topic from the transcript")
@app_commands.describe(topic="The topic you want to explore in more depth")
@handle_interaction_errors
async def closerlook(interaction: discord.Interaction, topic: str):
    if not await check_transcript_exists(interaction):
        return
    
    transcript = await db_service.get_channel_transcript(interaction.channel.id)
    response = await ai_service.get_closer_look(transcript, topic)
    await split_and_send_message(interaction.channel, response)

@bot.tree.command(name="ingest", description="Ingest meeting transcript from channel history")
@app_commands.describe(
    max_messages="Maximum number of messages to ingest (0 for all)",
    transcript_name="Name to identify this transcript"
)
@handle_interaction_errors
async def ingest(interaction: discord.Interaction, transcript_name: str, max_messages: int = 0):
    try:
        transcript, message_count = await process_channel_messages(interaction, max_messages)
        
        await db_service.save_transcript(interaction.channel.id, transcript, "channel", transcript_name)
        await interaction.followup.send(f"✅ Meeting transcript ingested successfully! Total messages: {message_count}")
        
        report = await ai_service.generate_comprehensive_report(transcript)
        await split_and_send_message(interaction.channel, report)
    except discord.errors.HTTPException:
        await interaction.followup.send(f"Error: Hit Discord API limit. Ingested {message_count} messages before stopping.")

@bot.tree.command(name="ingest_file", description="Ingest meeting transcript from an attached .txt file")
@app_commands.describe(
    file="The .txt file containing the meeting transcript",
    transcript_name="Name to identify this transcript"
)
@handle_interaction_errors
async def ingest_file(interaction: discord.Interaction, file: discord.Attachment, transcript_name: str):
    if not file.filename.endswith('.txt'):
        await interaction.followup.send("Please upload a .txt file.")
        return
    
    content = await file.read()
    transcript = content.decode('utf-8')
    
    await db_service.save_transcript(interaction.channel.id, transcript, "file", transcript_name)
    await interaction.followup.send(f"✅ Meeting transcript from {file.filename} ingested successfully!")
    
    report = await ai_service.generate_comprehensive_report(transcript)
    await split_and_send_message(interaction.channel, report)

@bot.tree.command(name="autoreport", description="Generate a detailed report for each item from the transcript analysis")
@handle_interaction_errors
async def autoreport(interaction: discord.Interaction):
    if not await check_transcript_exists(interaction):
        return
    
    transcript = await db_service.get_channel_transcript(interaction.channel.id)
    sections = await db_service.get_all_sections(interaction.channel.id)
    
    # Section titles for display
    section_titles = {
        'conversation_topics': 'Main Conversation Topics',
        'content_ideas': 'Content Ideas',
        'action_items': 'Action Items',
        'notes_for_ai': 'Notes for the AI',
        'decisions_made': 'Decisions Made',
        'critical_updates': 'Critical Updates'
    }
    
    # Process each section
    for section_key, items in sections.items():
        if items:  # Only process sections that have items
            await interaction.followup.send(f"**{section_titles[section_key]}**")
            
            # Generate a closer look for each item in the section
            for item in items:
                response = await ai_service.get_closer_look(transcript, item)
                await interaction.followup.send(f"**• {item}**\n\n{response}")
                await asyncio.sleep(1)  # Prevent rate limiting
    
    await interaction.followup.send("✅ Detailed report generation completed!")
