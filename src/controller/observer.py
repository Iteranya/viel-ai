import re
import discord
from src.controller.config import queue_to_process_everything, default_character
from src.controller.discordo import get_context
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.controller.filemanager import get_bot_list, get_channel_whitelist

# This is the main code that deals with determining what type of request is being given.
## Also the gateway to LAM

async def bot_behavior(message: discord.Message, client: discord.Client) -> bool:
    if isinstance(message.channel,discord.DMChannel): # Check if DM or Nah
        char = default_character
        if message.author.display_name.lower() != char.lower():
            await bot_think(message,char)
        return 

    whitelist = await get_channel_whitelist(message.channel.name)

    #The Fuzzy Logic Part~
    if message.webhook_id is None: # Check if it's a bot message
        text = message.content
        if text.startswith("//"):
            return True
        if whitelist!=None:
            for bot in whitelist:
                if bot in text:
                    await bot_think(message,bot.lower())
                    return True

        return False

    return False


async def bot_think(message: discord.Message, bot: str) -> None:
    channel = get_context(message)
    aicharacter = AICharacter(bot)
    if isinstance(channel,discord.channel.DMChannel) == False: 
        dimension = Dimension(server=str(message.guild.id), channel = str(channel.id))
    else: 
        dimension = Dimension(server = "dm", channel = str(message.author.id))

    queue_item = {
        "bot" : aicharacter,
        "message":discord.Message, # Yes, the actual message object 
        "dimension":dimension
    }
    queue_to_process_everything.put_nowait(queue_item)
    return