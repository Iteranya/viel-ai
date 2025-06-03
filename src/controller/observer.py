import re
import discord
from src.controller.config import queue_to_process_everything
from src.controller.discordo import get_context
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.data.config_data import load_or_create_config
from src.data.dimension_data import get_channel_whitelist

# This is the main code that deals with determining what type of request is being given.
## Also the gateway to LAM

auto_cap = 6 # How many times bot are allowed to auto-trigger, will prolly add this into config menu
current = 0
async def bot_behavior(message: discord.Message, client: discord.Client) -> bool:
    if message.author.display_name == client.user.display_name:
        return
    if isinstance(message.channel,discord.DMChannel): # Check if DM or Nah
        data = load_or_create_config()
        char = data.default_character
        if message.author.display_name.lower() != char.lower():
            await bot_think(message,char)
        return 

    whitelist = await get_channel_whitelist(message.channel.guild.name,message.channel.name)
    print("Author: "+str(message.author.display_name))
    print("User: "+str(client.user.display_name))
    
    # Add another part here to check if any user with the whitelisted bot display name is being replied
    if message.reference:
        try:
            replied_to = await message.channel.fetch_message(message.reference.message_id)
            if replied_to and replied_to.author.display_name in whitelist:
                await bot_think(message, replied_to.author.display_name.lower())
                return True
        except Exception as e:
            print(f"Failed to fetch replied message: {e}")
    
    if message.webhook_id: # Auto Trigger
        if current >= auto_cap:
            return
        text = message.content
        if whitelist!=None:
            for bot in whitelist:
                if bot.lower() == message.author.display_name.lower():
                    return
                if bot in text:
                    await bot_think(message,bot.lower())
                    current += 1
                    #return True

        return False
            
    #The Fuzzy Logic Part~
    if message.webhook_id is None: # Check if it's a bot message
        text = message.content
        if text.startswith("//"):
            return True
        if whitelist!=None:
            for bot in whitelist:
                if bot in text:
                    await bot_think(message,bot.lower())
                    current = 0
                    #return True

        return False

    return False


async def bot_think(message: discord.message.Message, bot: str) -> None:
    channel = get_context(message)
    print(type(channel))
    aicharacter = AICharacter(bot)
    if isinstance(channel,discord.channel.DMChannel) == False: 
        dimension = Dimension(server_name=str(message.guild.name), channel_name = str(channel.name))
    else: 
        dimension = Dimension(server_name = "dm", channel_name = str(message.author.id))

    queue_item = {
        "bot" : aicharacter,
        "message":message, # Yes, the actual message object 
        "dimension":dimension
    }
    queue_to_process_everything.put_nowait(queue_item)
    return