import re
import discord
from src.controller import config
from src.controller.discordo import Discordo
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension

# This is the main code that deals with determining what type of request is being given.
## Also the gateway to LAM

async def bot_behavior(message: discord.Message, client: discord.Client) -> bool:
    if isinstance(message.channel,discord.DMChannel): # Check if DM or Nah
        char = config.default_character
        if message.author.display_name.lower() != char.lower():
            await bot_think(message,char, True)
        return 
    if config.blacklist_mode:
        botlist = None
    else:
        botlist = await function.get_bot_list()

    whitelist = await function.get_channel_whitelist(message.channel.name)
    reply = await function.get_reply(message, client)
    replied = function.get_replied_user(reply)
    # TODO: Specifically work that janky ass replied[0] thing
    if whitelist==None and botlist == None:
        return True
    #If bot's were being replied still broken
    if reply is not None and replied:
            for bot in list(whitelist):
                if str(replied[0])==bot:
                        await bot_think(message, bot.lower())
                        return True
                    
        
    #The Fuzzy Logic Part~
    if message.webhook_id is None: # Check if it's a bot message
        text = message.content
        if text.startswith("//"):
            return True
        if botlist==None and whitelist!=None:
            for bot in whitelist:
                if bot in text:
                    await bot_think(message,bot.lower())
                    return True

        return False

    return False

async def bot_think(message: discord.Message, bot: str, dm=False) -> None:
    discordo = Discordo(message)
    if isinstance(message.channel,discord.DMChannel):
        discordo.dm = dm
    aicharacter = AICharacter(bot)
    if(discordo.get_thread()!=None):
        context = discordo.get_thread()
    elif(discordo.get_dm()!=None):
        context = discordo.get_dm()
    else:
        context = discordo.get_channel()
    if discordo.dm == False: 
        dimension = Dimension(server=str(message.guild.id), channel = str(context.id))
    else: 
        dimension = Dimension(server = "dm", channel = str(message.author.id))

    queue_item = {
        "bot" : aicharacter,
        "discordo":discordo,
        "dimension":dimension
    }
    config.queue_to_process_everything.put_nowait(queue_item)
    return
