import discord
from discord import app_commands
import asyncio
import functools
from typing import Dict, Optional, Callable, Any, Tuple
from datetime import datetime
from .config import bot, INGESTION_BATCH_SIZE
from .ai_service import AIService
from .message_handler import split_and_send_message
from .db_service import DBService

# Defer initialization to avoid connection issues during imports
ai_service = None
db_service = None
# Import query optimizer
from .query_optimizer import MultiQueryProcessor

# Initialize query processor (lazy loaded)
query_processor = None

def _ensure_query_processor() -> None:
    """Initialize query processor if not already done"""
    global query_processor
    if query_processor is None:
        _ensure_services()
        query_processor = MultiQueryProcessor(db_service)

def _ensure_services() -> None:
    """Initialize services if not already done"""
    global ai_service, db_service
    if ai_service is None:
        ai_service = AIService()
    if db_service is None:
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
    _ensure_services()
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
    _ensure_services()
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

@bot.tree.command(name="closerlook", description="Get a closer look at a specific topic using semantic search + AI analysis")
@app_commands.describe(topic="The topic you want to explore in more depth")
@handle_interaction_errors
async def closerlook(interaction: discord.Interaction, topic: str):
    """Enhanced closerlook using semantic search + AI analysis"""
    _ensure_services()
    _ensure_query_processor()
    
    if not await check_transcript_exists(interaction):
        return
    
    # First, get relevant content using semantic search
    search_results = await query_processor.search_optimized(
        query=topic,
        channel_id=interaction.channel.id,
        max_results=8  # Get more context for AI analysis
    )
    
    if not search_results:
        # Fallback to old method if no semantic results
        transcript = await db_service.get_channel_transcript(interaction.channel.id)
        response = await ai_service.get_closer_look(transcript, topic)
        await split_and_send_message(interaction.channel, response)
        return
    
    # Combine relevant chunks for AI analysis
    relevant_content = []
    for result in search_results:
        relevant_content.append(f"[Relevance: {result['score']:.2f}] {result['text']}")
    
    combined_context = "\n\n---\n\n".join(relevant_content)
    
    # Get AI analysis on the relevant content
    enhanced_prompt = f"Based on the most relevant transcript segments below, provide a detailed analysis of '{topic}':\n\n{combined_context}"
    response = await ai_service.get_closer_look(combined_context, topic)
    
    # Add search context to the response
    context_info = f"*🔍 Analysis based on {len(search_results)} most relevant transcript segments*\n\n"
    full_response = context_info + response
    
    await split_and_send_message(interaction.channel, full_response)

@bot.tree.command(name="search", description="Search transcript content with AI-powered semantic search")
@app_commands.describe(
    query="What you want to search for in the transcript",
    max_results="Maximum number of results to return (default: 5)"
)
@handle_interaction_errors
async def search(interaction: discord.Interaction, query: str, max_results: int = 5):
    """Enhanced semantic search using query optimization"""
    _ensure_services()
    _ensure_query_processor()
    
    if not await check_transcript_exists(interaction):
        return
    
    # Limit max_results to reasonable bounds
    max_results = min(max(max_results, 1), 15)
    
    # Perform optimized search
    results = await query_processor.search_optimized(
        query=query,
        channel_id=interaction.channel.id,
        max_results=max_results
    )
    
    if not results:
        await interaction.followup.send(f"No relevant content found for: '{query}'")
        return
    
    # Format results for display
    response_parts = [f"**Search Results for:** '{query}'\n"]
    
    for i, result in enumerate(results, 1):
        score_bar = "🟢" if result['score'] >= 0.6 else "🟡" if result['score'] >= 0.4 else "🟠"
        
        response_parts.append(
            f"**{i}. {score_bar} Relevance: {result['score']:.2f}**\n"
            f"📝 *{result.get('transcript_name', 'Unknown')}*\n"
            f"```\n{result['text'][:400]}{'...' if len(result['text']) > 400 else ''}\n```\n"
        )
    
    full_response = "\n".join(response_parts)
    await split_and_send_message(interaction.channel, full_response)

@bot.tree.command(name="explore", description="Explore transcript content with guided search suggestions")
@app_commands.describe(
    topic="Optional starting topic (if not provided, shows overview)",
    depth="How deep to explore (1-3, default: 2)"
)
@handle_interaction_errors
async def explore(interaction: discord.Interaction, topic: Optional[str] = None, depth: int = 2):
    """Interactive exploration of transcript content"""
    _ensure_services()
    _ensure_query_processor()
    
    if not await check_transcript_exists(interaction):
        return
    
    depth = min(max(depth, 1), 3)  # Clamp between 1-3
    
    if not topic:
        # Show overview with key topics from transcript sections
        sections = await db_service.get_all_sections(interaction.channel.id)
        
        overview_parts = ["**📋 Transcript Overview - Key Topics to Explore:**\n"]
        
        # Show topics from different sections
        if sections.get('conversation_topics'):
            overview_parts.append("**🗨️ Main Topics:**")
            for topic in sections['conversation_topics'][:5]:  # Top 5
                overview_parts.append(f"• {topic}")
            overview_parts.append("")
        
        if sections.get('decisions_made'):
            overview_parts.append("**⚡ Key Decisions:**")  
            for decision in sections['decisions_made'][:3]:  # Top 3
                overview_parts.append(f"• {decision}")
            overview_parts.append("")
        
        if sections.get('action_items'):
            overview_parts.append("**✅ Action Items:**")
            for item in sections['action_items'][:3]:  # Top 3  
                overview_parts.append(f"• {item}")
            overview_parts.append("")
        
        overview_parts.append("*💡 Use `/search <topic>` or `/explore <topic>` to dive deeper into any area*")
        
        overview = "\n".join(overview_parts)
        await split_and_send_message(interaction.channel, overview)
        return
    
    # Explore specific topic with increasing depth
    results = await query_processor.search_optimized(
        query=topic,
        channel_id=interaction.channel.id,
        max_results=min(5 + depth * 2, 10)  # More results for deeper exploration
    )
    
    if not results:
        await interaction.followup.send(f"No content found for topic: '{topic}'\n*Try browsing with `/explore` (no topic) first*")
        return
    
    # Create exploration response
    response_parts = [f"**🔍 Exploring: '{topic}'**\n"]
    
    # Show most relevant content
    top_result = results[0]
    response_parts.append(
        f"**📌 Most Relevant ({top_result['score']:.2f} match):**\n"
        f"```\n{top_result['text'][:500]}{'...' if len(top_result['text']) > 500 else ''}\n```\n"
    )
    
    if depth >= 2 and len(results) > 1:
        response_parts.append("**🔗 Related Context:**")
        for result in results[1:min(3, len(results))]:
            preview = result['text'][:150] + "..." if len(result['text']) > 150 else result['text']
            response_parts.append(f"• ({result['score']:.2f}) {preview}")
        response_parts.append("")
    
    if depth >= 3 and len(results) > 3:
        # Generate AI insights for deep exploration
        context = "\n\n".join([r['text'] for r in results[:5]])
        insights = await ai_service.get_closer_look(context, f"key insights and patterns related to {topic}")
        response_parts.append(f"**🧠 AI Insights:**\n{insights}")
    
    full_response = "\n".join(response_parts)
    await split_and_send_message(interaction.channel, full_response)

@bot.tree.command(name="help", description="Show available commands and RAG search capabilities")
@handle_interaction_errors  
async def help_command(interaction: discord.Interaction):
    """Show help for all commands including new RAG features"""
    
    help_text = """
**📚 Miyu-Data Discord Bot - Command Reference**

**📥 Data Ingestion:**
• `/ingest <transcript_name> [max_messages]` - Ingest channel messages
• `/ingest_file <file> <transcript_name>` - Ingest from .txt file

**🔍 Smart Search (RAG-Powered):**
• `/search <query> [max_results]` - Semantic search with AI optimization
• `/closerlook <topic>` - Deep analysis using semantic search + AI
• `/explore [topic] [depth]` - Interactive exploration with suggestions

**📊 Analysis & Reports:**
• `/autoreport` - Generate detailed reports for all transcript sections  
• `/execute_notes` - Execute all AI tasks from transcript analysis

**🧠 RAG Features:**
✨ **Semantic Search** - Finds content by meaning, not just keywords
✨ **Query Optimization** - Automatically expands and improves your queries
✨ **Multi-Query Processing** - Searches multiple query variations for better results
✨ **Smart Scoring** - Ranks results by relevance with confidence indicators

**💡 Search Tips:**
• Use natural language: "What decisions were made about the database?"
• Try different phrasings: "action items", "tasks", "things to do"
• Combine concepts: "mobile app authentication security"
• Use `/explore` without a topic to see what's available to search

**🎯 Score Guide:**
🟢 0.6+ = Highly relevant | 🟡 0.4+ = Good match | 🟠 0.3+ = Related content
    """
    
    await split_and_send_message(interaction.channel, help_text)

@bot.tree.command(name="ingest", description="Ingest meeting transcript from channel history")
@app_commands.describe(
    max_messages="Maximum number of messages to ingest (0 for all)",
    transcript_name="Name to identify this transcript"
)
@handle_interaction_errors
async def ingest(interaction: discord.Interaction, transcript_name: str, max_messages: int = 0):
    _ensure_services()
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
    _ensure_services()
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
    _ensure_services()
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
