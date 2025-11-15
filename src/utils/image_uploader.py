# src/utils/image_uploader.py

import io
import asyncio
from typing import Optional
import discord

from api.db.database import Database
from bot_run import Viel

async def _async_upload_logic(
    image_bytes: bytes, 
    filename: str, 
    bot: Viel, 
    system_channel_id: str
) -> Optional[str]:
    """This is the core async logic that MUST run on the bot's event loop."""
    try:
        target_channel = bot.get_channel(int(system_channel_id))
        if not target_channel:
            print(f"Error (from bot thread): Could not fetch channel with ID {system_channel_id}.")
            return None

        image_file = discord.File(io.BytesIO(image_bytes), filename=filename)
        sent_message = await target_channel.send(file=image_file)

        if not sent_message.attachments:
            print("Error (from bot thread): Message sent, but no attachment URL returned.")
            return None

        return sent_message.attachments[0].url
    except Exception as e:
        print(f"An unexpected error occurred within the bot's event loop during upload: {e}")
        return None

def find_system_channel_id(bot: Viel) -> Optional[str]:
    """Synchronous helper to find the system channel ID."""
    if not bot:
        return None
    for channel_data in bot.db.list_channels():
        if channel_data.get('data', {}).get('is_system_channel', False):
            return channel_data['channel_id']
    return None

def upload_image_to_system_channel(
    image_bytes: bytes, 
    filename: str, 
    bot: Viel
) -> Optional[str]:
    """
    Orchestrates uploading an image to a system channel in a thread-safe way.
    This function is SYNCHRONOUS and can be called from any thread.
    """
    if not bot or not bot.loop.is_running():
        print("Error: Bot event loop is not running.")
        return None
    
    system_channel_id = find_system_channel_id(bot)
    if not system_channel_id:
        print("Error: No system channel found.")
        return None
    
    # Create the coroutine object we want to run on the bot's loop
    coro = _async_upload_logic(image_bytes, filename, bot, system_channel_id)
    
    # Schedule the coroutine to be run on the bot's event loop and get a future
    future = asyncio.run_coroutine_threadsafe(coro, bot.loop)
    
    try:
        # Wait for the future to complete (with a timeout) and get the result
        cdn_url = future.result(timeout=30) # 30-second timeout
        print(f"Successfully uploaded image via thread-safe call. CDN URL: {cdn_url}")
        return cdn_url
    except asyncio.TimeoutError:
        print("Error: The image upload operation timed out.")
        return None
    except Exception as e:
        print(f"An error occurred while waiting for the upload future: {e}")
        return None