# src/handlers/discord_interface.py

import discord
from typing import Union

# Import your new, refactored classes
from src.controller.caption import CaptionManager
from src.controller.image_processor import ImageProcessor
from src.controller.history import HistoryFormatter
from src.controller.messenger import DiscordMessenger

# Import the necessary models
from src.models.aicharacter import AICharacter
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
history_formatter = HistoryFormatter(caption_manager, image_processor)
discord_messenger = DiscordMessenger()

print("Discord interface initialized.")

# =============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# =============================================================================
# These are the simple functions you can call from anywhere in your code,
# just like you did with the old DiscordHandler.

def get_context(message: discord.Message) -> Union[discord.TextChannel, discord.Thread]:
    """
    Backward compatibility function.
    Gets the channel or thread context from a message.
    """
    return message.channel

async def get_history(message: discord.Message, limit: int = 100) -> str:
    """
    Backward compatibility function.
    Uses the global history_formatter instance to get formatted message history.
    """
    context = get_context(message)
    return await history_formatter.get_history(context, limit)

async def send(bot: AICharacter, message: discord.Message, queue_item: QueueItem):
    """
    Backward compatibility function.
    Uses the global discord_messenger instance to send a message.
    """
    await discord_messenger.send_message(bot, message, queue_item)