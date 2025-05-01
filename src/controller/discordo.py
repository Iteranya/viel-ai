import discord
import config
import src.textutil as textutil
import util
import re
from src.models import QueueItem
from src.aicharacter import AICharacter
import os
class Discordo:
    def __init__(self, message:discord.Message):
        self.raw_message = message
        self.default_character_url = config.bot_default_avatar
        self.default_character_name = config.bot_display_name
        self.history=None
        self.video_caption = None
        self.dm = False
    async def process_attachment(self):
        if self.raw_message.attachments:
            attachment = self.raw_message.attachments[0]
            image_bytes = await attachment.read()
            #Toggle this to use just combine everything
            if attachment.filename.lower().endswith('.webp'):
                image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
            base64_image = util.encode_image_to_base64(image_bytes)
            return base64_image
        else:
            return None
        
    async def save_attachment(self):
        if self.raw_message.attachments:
            attachment = self.raw_message.attachments[0]

            # Create the attachments directory if it doesn't exist
            attachments_dir = os.path.join(os.getcwd(), 'attachments')
            os.makedirs(attachments_dir, exist_ok=True)

            # Generate the base filepath
            filename = attachment.filename
            filepath = os.path.join(attachments_dir, filename)

            # Save the new attachment if it doesn't exist
            with open(filepath, 'wb') as f:
                attachment_bytes = await attachment.read()
                f.write(attachment_bytes)

            return filepath
        else:
            return None
            

    # Get Raw Message
    def get_raw_user_message(self):
        return self.raw_message
    
    def get_user_message_content(self):
        return self.raw_message.content
    
    def get_user_message_author_name(self):
        return self.raw_message.author.display_name
    
    def get_user_message_author_avatar(self):
        return self.raw_message.author.display_avatar.url
    
    def get_channel(self)->discord.TextChannel:
        channel = self.raw_message.channel
        if isinstance(channel,discord.Thread):
            return channel.parent
        elif isinstance(channel,discord.TextChannel):
            return  channel
        else:
            return None
    
    def get_dm(self)->discord.DMChannel:
        channel = self.raw_message.channel
        if isinstance(channel,discord.DMChannel):
            return channel
        else:
            return None
    
    def get_thread(self)->discord.Thread:
        channel = self.raw_message.channel
        if isinstance(channel,discord.Thread):
            return channel
        else:
            return None
    
    async def send(self,bot,queue_item:QueueItem):
        try:
            await self.raw_message.remove_reaction('✨',config.bot_user)
        except Exception as e:
            print("Hi!")
      
        if queue_item.error:
            await self.send_as_system(queue_item)
        elif self.dm == True:
            await self.send_as_dm(queue_item,bot)
        else:
            await self.send_as_bot(queue_item,bot)

    async def send_as_dm(self,queue_item:QueueItem,bot: AICharacter):
        response = queue_item.result
        response.replace(bot.name+":","")
        response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]
        
        for chunk in response_chunks:
            await self.send_dm(chunk)

        
    async def send_as_bot(self,queue_item:QueueItem,bot: AICharacter):
        response = queue_item.result
        response.replace(bot.name+":","")
        response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

        character_name = bot.name  # Placeholder for character name
        character_avatar_url = bot.avatar  # Placeholder for character avatar URL
        
        for chunk in response_chunks:
            await self.send_webhook_message(chunk, character_avatar_url, character_name)
        if queue_item.images!=None:
            await self.send_webhook_message("[System Note: Attachment]",character_avatar_url, character_name,queue_item.images)

    async def send_as_user(self,content):
        await self.send_webhook_message(content, self.get_user_message_author_avatar(), self.get_user_message_author_name())

    async def send_as_system(self,queue_item:QueueItem):
        await self.send_webhook_message(queue_item.error)

        
    async def send_webhook_message(self,content: str, avatar_url: str=None, username: str=None,images=None) -> None:
        channel = self.get_channel()
        thread = self.get_thread()
        print("Check Avatar URL:"+str(avatar_url))
        if avatar_url == None or str(avatar_url) == "none":
            avatar_url = self.default_character_url
        if username == None:
            username = self.default_character_name
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
    
    async def send_dm(self,content: str) -> None:
        channel = self.get_dm()
        await channel.send(content)
        return

    async def initialize_channel_history(self, limit: int = 50):
        history = []
        dm:discord.DMChannel = self.get_dm()
        channel:discord.TextChannel = self.get_channel()
        thread:discord.Thread = self.get_thread()
        context = None
        if thread!=None:
            context = thread
        elif dm!=None:
            context = dm
        else:
            context = channel
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
        contents = "\n\n".join(history)
        contents = self.reset_from_start(contents)
        contents += "\n\n"
        self.history = contents
        return contents

    def reset_from_start(self,history: str) -> str:
        # Find the last occurrence of "[RESET]"
        last_reset = history.rfind("[RESET]")
        # If found, return everything after "[RESET]"
        if last_reset != -1:
            return history[last_reset + len("[RESET]"):].strip()
        # If not found, return the input string as is
        return history.strip()
