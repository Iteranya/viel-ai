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
current_num:int = 0
last_bot = ""
async def bot_behavior(message: discord.Message, client: discord.Client) -> bool:
    global current_num
    global last_bot
    data = load_or_create_config()
    if isinstance(message.channel,discord.DMChannel): # Check if DM or Nah
        if message.author.display_name == client.user.display_name:
            return
        
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
                last_bot = replied_to.author.display_name
                return True
        except Exception as e:
            print(f"Failed to fetch replied message: {e}")
            
    #The Fuzzy Logic Part~
    if message.webhook_id is None: # Check if it's a bot message
        text = message.content
        if text.startswith("//"):
            return True
        if "[KNOCK OUT]" in text:
            return True
        if whitelist!=None:
            for bot in whitelist:
                if bot in text:
                    await bot_think(message,bot.lower())
                    last_bot = bot
                    current_num = 0
                    #return True

        return 
    else:
        if current_num >= data.auto_cap:
            print("Auto Trigger Cap Reached")
            return
        text = message.content
        if whitelist!=None:
            if message.author.display_name.lower() not in [bot.lower() for bot in whitelist]:
                print("Not bot Webhook")
                return
            # Check for bot mentions in text
            for bot in whitelist:
                if bot in text and bot.lower()!=message.author.display_name.lower():
                    if bot.lower() == last_bot.lower():
                        continue
                    print("triggering "+bot)
                    await bot_think(message, bot.lower())
                    last_bot = bot
                    current_num += 1

            return 
    return 


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