# # src/handlers/discord_interface.py

# import discord
# from typing import Union

# # Import your new, refactored classes
# from src.controller.caption import CaptionManager
# from src.controller.image_processor import ImageProcessor
# from src.controller.messenger import DiscordMessenger

# # Import the necessary models
# from src.models.aicharacter import ActiveCharacter
# from src.models.queue import QueueItem

# # =============================================================================
# # SINGLETON INITIALIZATION
# # =============================================================================
# # Here, we create a single instance of each class when the module is loaded.
# # These instances will be shared across your application wherever you import
# # the functions from this file.

# print("Initializing Discord interface singletons...")



# print("Discord interface initialized.")

# async def _remove_processing_emoji(message: discord.Message, bot_user: discord.User):
#     """Removes the 'thinking' emoji from a message on behalf of the bot."""
#     try:
#         # The second argument is the user whose reaction should be removed.
#         await message.remove_reaction('✨', bot_user)
#     except discord.HTTPException:
#         # This can fail if the message was deleted or permissions changed.
#         # It's safe to ignore.
#         pass

# async def send(bot: ActiveCharacter, message: discord.Message, queue_item: QueueItem, viel):
#     """
#     Backward compatibility function.
#     Uses the global discord_messenger instance to send a message.
#     """
#     await _remove_processing_emoji(message, viel.user)
#     await discord_messenger.send_message(bot, message, queue_item, viel)