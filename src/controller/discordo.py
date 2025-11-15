# src/handlers/discord_interface.py

import discord
from typing import Union

# Import your new, refactored classes
from src.controller.caption import CaptionManager
from src.controller.image_processor import ImageProcessor
from src.controller.messenger import DiscordMessenger

# Import the necessary models
from src.models.aicharacter import ActiveCharacter
from src.models.queue import QueueItem

# =============================================================================
# SINGLETON INITIALIZATION
# =============================================================================
# Here, we create a single instance of each class when the module is loaded.
# These instances will be shared across your application wherever you import
# the functions from this file.

print("Initializing Discord interface singletons...")

caption_manager = CaptionManager()
image_processor = ImageProcessor()
discord_messenger = DiscordMessenger()

print("Discord interface initialized.")

async def send(bot: ActiveCharacter, message: discord.Message, queue_item: QueueItem):
    """
    Backward compatibility function.
    Uses the global discord_messenger instance to send a message.
    """
    await discord_messenger.send_message(bot, message, queue_item)