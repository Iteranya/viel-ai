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

async def send(bot, message: discord.Message, queue_item:QueueItem):
    try:
        await message.remove_reaction('✨',config.bot_user)
    except Exception as e:
        print("Hi!")
    
    if queue_item.error:
        await send_as_system(queue_item)
    elif queue_item.dm == True:
        await send_as_dm(queue_item,bot)
    else:
        await send_as_bot(queue_item,bot)

async def send_as_dm(queue_item:QueueItem,bot: AICharacter):
    response = queue_item.result
    response.replace(bot.name+":","")
    response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]
    
    for chunk in response_chunks:
        await send_regular_message(chunk)

    
async def send_as_bot(queue_item:QueueItem,bot: AICharacter):
    response = queue_item.result
    response.replace(bot.name+":","")
    response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

    character_name = bot.name  # Placeholder for character name
    character_avatar_url = bot.avatar  # Placeholder for character avatar URL
    
    for chunk in response_chunks:
        await send_webhook_message(chunk, character_avatar_url, character_name)
    if queue_item.images!=None:
        await send_webhook_message("[System Note: Attachment]",character_avatar_url, character_name,queue_item.images)

async def send_as_system(queue_item:QueueItem):
    await send_regular_message(queue_item.error)
    
async def send_webhook_message(content: str, avatar_url: str=None, username: str=None,images=None) -> None:
    context = get_context()
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
                    if images!=None:
                        await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread,embeds=images)
                    else:
                        await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread)
                    return
                else:
                    if images!=None:
                        await webhook.send(content, username=username, avatar_url=avatar_url,embeds=images)
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

async def send_regular_message(content: str) -> None:
    channel = get_context()
    await channel.send(content)
    return

async def get_reply(message: discord.Message, client: discord.Client):
    reply = ""

    # If the message reference is not none, meaning someone is replying to a message
    if message.reference is not None:
        # Grab the message that's being replied to
        referenced_message = message.reference.cached_message
        if referenced_message is None:
            if message.reference.message_id is None:
                print("Message ID is null")
                return reply
            referenced_message = await message.channel.fetch_message(message.reference.message_id)

        # Verify that the author of the message is bot and that it has a reply
        if referenced_message.reference is not None and referenced_message.author == client.user:
            # Grab that other reply as well
            referenced_user_message = referenced_message.reference.cached_message
            if referenced_user_message is None:
                if referenced_message.reference.message_id is None:
                    print("Message ID is null")
                    return reply
                try:
                    referenced_user_message = await message.channel.fetch_message(referenced_message.reference.message_id)
                    # Process the fetched message as needed
                except discord.NotFound:
                    # Handle the case where the message cannot be found
                    print("Message not found or access denied.")
                    return reply

            # If the author of the reply is not the same person as the initial user, we need this data
            if referenced_user_message.author != message.author:
                reply = referenced_user_message.author.display_name + \
                    ": " + referenced_user_message.clean_content + "\n"
                reply = reply + referenced_message.author.display_name + \
                    ": " + referenced_message.clean_content + "\n"
                reply = textutil.clean_user_message(reply)

                return reply

        # If the referenced message isn't from the bot, use it in the reply
        if referenced_message.author != client.user:
            reply = referenced_message.author.display_name + \
                ": " + referenced_message.clean_content + "\n"

            return reply

    return reply

# class Discordo:
#     def __init__(self, message:discord.Message):
#         self.raw_message = message
#         self.default_character_url = config.bot_default_avatar
#         self.default_character_name = config.bot_display_name
#         self.history=None
#         self.video_caption = None
#         self.dm = False
#     async def process_attachment(self):
#         if self.raw_message.attachments:
#             attachment = self.raw_message.attachments[0]
#             image_bytes = await attachment.read()
#             #Toggle this to use just combine everything
#             if attachment.filename.lower().endswith('.webp'):
#                 image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
#             base64_image = util.encode_image_to_base64(image_bytes)
#             return base64_image
#         else:
#             return None
        
#     async def save_attachment(self):
#         if self.raw_message.attachments:
#             attachment = self.raw_message.attachments[0]

#             # Create the attachments directory if it doesn't exist
#             attachments_dir = os.path.join(os.getcwd(), 'attachments')
#             os.makedirs(attachments_dir, exist_ok=True)

#             # Generate the base filepath
#             filename = attachment.filename
#             filepath = os.path.join(attachments_dir, filename)

#             # Save the new attachment if it doesn't exist
#             with open(filepath, 'wb') as f:
#                 attachment_bytes = await attachment.read()
#                 f.write(attachment_bytes)

#             return filepath
#         else:
#             return None
            

#     # Get Raw Message
#     def get_raw_user_message(self):
#         return self.raw_message
    
#     def get_user_message_content(self):
#         return self.raw_message.content
    
#     def get_user_message_author_name(self):
#         return self.raw_message.author.display_name
    
#     def get_user_message_author_avatar(self):
#         return self.raw_message.author.display_avatar.url
    
#     def get_channel(self)->discord.TextChannel:
#         channel = self.raw_message.channel
#         if isinstance(channel,discord.Thread):
#             return channel.parent
#         elif isinstance(channel,discord.TextChannel):
#             return  channel
#         else:
#             return None
    
#     def get_dm(self)->discord.DMChannel:
#         channel = self.raw_message.channel
#         if isinstance(channel,discord.DMChannel):
#             return channel
#         else:
#             return None
    
#     def get_thread(self)->discord.Thread:
#         channel = self.raw_message.channel
#         if isinstance(channel,discord.Thread):
#             return channel
#         else:
#             return None
    
#     async def send(self,bot,queue_item:QueueItem):
#         try:
#             await self.raw_message.remove_reaction('✨',config.bot_user)
#         except Exception as e:
#             print("Hi!")
      
#         if queue_item.error:
#             await self.send_as_system(queue_item)
#         elif self.dm == True:
#             await self.send_as_dm(queue_item,bot)
#         else:
#             await self.send_as_bot(queue_item,bot)

#     async def send_as_dm(self,queue_item:QueueItem,bot: AICharacter):
#         response = queue_item.result
#         response.replace(bot.name+":","")
#         response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]
        
#         for chunk in response_chunks:
#             await self.send_dm(chunk)

        
#     async def send_as_bot(self,queue_item:QueueItem,bot: AICharacter):
#         response = queue_item.result
#         response.replace(bot.name+":","")
#         response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

#         character_name = bot.name  # Placeholder for character name
#         character_avatar_url = bot.avatar  # Placeholder for character avatar URL
        
#         for chunk in response_chunks:
#             await self.send_webhook_message(chunk, character_avatar_url, character_name)
#         if queue_item.images!=None:
#             await self.send_webhook_message("[System Note: Attachment]",character_avatar_url, character_name,queue_item.images)

#     async def send_as_user(self,content):
#         await self.send_webhook_message(content, self.get_user_message_author_avatar(), self.get_user_message_author_name())

#     async def send_as_system(self,queue_item:QueueItem):
#         await self.send_webhook_message(queue_item.error)

        
#     async def send_webhook_message(self,content: str, avatar_url: str=None, username: str=None,images=None) -> None:
#         channel = self.get_channel()
#         thread = self.get_thread()
#         print("Check Avatar URL:"+str(avatar_url))
#         if avatar_url == None or str(avatar_url) == "none":
#             avatar_url = self.default_character_url
#         if username == None:
#             username = self.default_character_name
#         webhook_list = await channel.webhooks()
#         for webhook in webhook_list:
#             if webhook.name == config.bot_user.display_name:
#                     if thread != None:
#                         if images!=None:
#                             await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread,embeds=images)
#                         else:
#                             await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread)
#                         return
#                     else:
#                         if images!=None:
#                             await webhook.send(content, username=username, avatar_url=avatar_url,embeds=images)
#                         else:
#                             await webhook.send(content, username=username, avatar_url=avatar_url)
#                     return
#         webhook = await channel.create_webhook(name=config.bot_user.display_name)
#         if thread!=None:
#             if images!=None:
#                 await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread,files=images)
#             else:
#                 await webhook.send(content, username=username, avatar_url=avatar_url, thread=thread)
#         else:
#             if images!=None:
#                  webhook.send(content, username=username, avatar_url=avatar_url,files=images)
#             else:
#                 await webhook.send(content, username=username, avatar_url=avatar_url)
#         return
    
#     async def send_dm(self,content: str) -> None:
#         channel = self.get_dm()
#         await channel.send(content)
#         return

#     async def initialize_channel_history(self, limit: int = 50):
#         history = []
#         dm:discord.DMChannel = self.get_dm()
#         channel:discord.TextChannel = self.get_channel()
#         thread:discord.Thread = self.get_thread()
#         context = None
#         if thread!=None:
#             context = thread
#         elif dm!=None:
#             context = dm
#         else:
#             context = channel
#         async for message in context.history(limit=limit):
#             name = str(message.author.display_name)

#             # Sanitize the name by removing spaces, special characters, and converting to lowercase
#             sanitized_name = re.sub(r'[^\w]', '', name)
            
#             content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
#             if content.startswith("[System"):
#                 history.append(content.strip())
#             elif content.startswith("//"):
#                 #do nothing
#                 pass
#             elif content.startswith("^"):
#                 content = content.replace("^","")
#                 history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
#             else:
#                 # Add the pseudonym function here
#                 history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
                
#         # Reverse the order of the collected messages
#         history.reverse()
#         contents = "\n\n".join(history)
#         contents = self.reset_from_start(contents)
#         contents += "\n\n"
#         self.history = contents
#         return contents

#     def reset_from_start(self,history: str) -> str:
#         # Find the last occurrence of "[RESET]"
#         last_reset = history.rfind("[RESET]")
#         # If found, return everything after "[RESET]"
#         if last_reset != -1:
#             return history[last_reset + len("[RESET]"):].strip()
#         # If not found, return the input string as is
#         return history.strip()
