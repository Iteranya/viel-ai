import discord
from src.controller import config
import re
from src.models.queue import QueueItem
from src.models.aicharacter import AICharacter
import os
from src.utils import textutil


# This is the class that lets you interact with Discord Itself 
# So like... Grabbing message, history, etc, etc.

# Fuck it, procedural time

def get_context(message: discord.Message): # Get the channel, regardless of the context.
    channel = message.channel
    return channel

async def get_history(message: discord.Message, limit:int = 50):
    history = []
    context = get_context(message=message)
    async for message in context.history(limit=limit):
        name = str(message.author.display_name)
        # Sanitize the name by removing spaces, special characters, and converting to lowercase
        sanitized_name = re.sub(r'[^\w]', '', name)
        
        content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
        if content.startswith("[System"):
            history.append(content.strip())
        elif content.startswith("//"):
            #do nothing
            pass
        elif content.startswith("^"):
            content = content.replace("^","")
            history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
        else:
            # Add the pseudonym function here
            history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
            
    # Reverse the order of the collected messages
    history.reverse()
    contents = "\n\n".join(history) # Turn history to raw string
    contents = reset_from_start(contents)
    contents += "\n\n"
    history = contents
    return contents

def reset_from_start(history: str) -> str:
    # Find the last occurrence of "[RESET]"
    last_reset = history.rfind("[RESET]")
    # If found, return everything after "[RESET]"
    if last_reset != -1:
        return history[last_reset + len("[RESET]"):].strip()
    # If not found, return the input string as is
    return history.strip()

def sanitize_message(item: QueueItem):
    sanitized_item = item
    if hasattr(sanitized_item, "result") and isinstance(sanitized_item.result, str):
        sanitized_item.result = sanitized_item.result.replace("@everyone", "@/everyone").replace("@here", "@/here")
    return sanitized_item

async def send(bot, message: discord.Message, queue_item:QueueItem):
    try:
        await message.remove_reaction('✨',config.bot_user)
    except Exception as e:
        print("Hi!")

    queue_item = sanitize_message(queue_item)
    
    if queue_item.error:
        await send_as_system(queue_item,message)
    elif queue_item.dm == True:
        await send_as_dm(queue_item,bot,message)
    else:
        await send_as_bot(queue_item,bot,message)

async def send_as_dm(queue_item:QueueItem,bot: AICharacter,message: discord.Message):
    response = queue_item.result
    response.replace(bot.name+":","")
    response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]
    
    for chunk in response_chunks:
        await send_regular_message(chunk,message)
    if queue_item.images:
        for image in queue_item.images:
            await send_attachment(image_link=image,message=message)
            
async def send_as_bot(queue_item:QueueItem,bot: AICharacter,message: discord.Message):
    response = queue_item.result
    response.replace(bot.name+":","")
    response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

    character_name = bot.name  # Placeholder for character name
    character_avatar_url = bot.avatar  # Placeholder for character avatar URL
    
    for chunk in response_chunks:
        await send_webhook_message(chunk, character_avatar_url, character_name,message=message)
    
    if queue_item.images:
        for image in queue_item.images:
            await send_webhook_message(None, character_avatar_url, character_name, images = image,message=message)
    

async def send_as_system(queue_item:QueueItem,message: discord.Message):
    await send_regular_message(queue_item.error,message)
    
async def send_webhook_message(content: str, avatar_url: str=None, username: str=None,images=None,message: discord.Message = None) -> None:
    context = message.channel
    print("Context is: "+str(message.channel))
    if isinstance(context,discord.TextChannel):
        thread = None
        channel = context
    if isinstance(context, discord.Thread):
        channel = context.parent
        thread = context

    if avatar_url == None or str(avatar_url) == "none":
        avatar_url = config.get_default_avatar()
    if username == None:
        username = config.get_default_name()
    webhook_list = await channel.webhooks()
    for webhook in webhook_list:
        if webhook.name == config.bot_user.display_name:
                if thread != None:
                    if images:
                        file = discord.File(images)
                        await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread,file=file)
                    else:
                        await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread)
                    return
                else:
                    if images:
                        file = discord.File(images)
                        await webhook.send(content, username=username, avatar_url=avatar_url,file=file)
                    else:
                        await webhook.send(content, username=username, avatar_url=avatar_url)
                return
    webhook = await channel.create_webhook(name=config.bot_user.display_name)
    if thread!=None:
        if images!=None:
            await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread,files=images)
        else:
            await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread)
    else:
        if images!=None:
                webhook.send(content, username=username, avatar_url=avatar_url,files=images)
        else:
            await webhook.send(content, username=username, avatar_url=avatar_url)
    return

async def send_regular_message(content: str,message: discord.Message) -> None:
    channel = message.channel
    await channel.send(content)
    return

async def send_attachment(image_link: str, message: discord.Message) -> None:
    channel = message.channel
    file = discord.File(image_link)
    await channel.send(file=file)

async def send_webhook_attachment(image_link: str, message: discord.Message) -> None:
    await send_webhook_message(content="[System Note: Image Attachment]",)