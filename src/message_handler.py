import discord
import asyncio
from .config import MAX_MESSAGE_LENGTH

async def split_and_send_message(channel: discord.TextChannel, content: str, char_limit: int = MAX_MESSAGE_LENGTH):
    """Split a long message and send it in chunks."""
    chunks = []
    current_chunk = ""

    for line in content.split('\n'):
        if len(current_chunk) + len(line) + 1 > char_limit:
            chunks.append(current_chunk.strip())
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'

    if current_chunk:
        chunks.append(current_chunk.strip())

    for i, chunk in enumerate(chunks):
        await channel.send(f"{chunk}\n\n(Part {i+1}/{len(chunks)})")
        await asyncio.sleep(1)
