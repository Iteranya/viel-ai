# src/handlers/discord_messenger.py

import discord
import os
from typing import List, Optional, Union

from src.controller import config
from src.models.queue import QueueItem
from src.models.aicharacter import AICharacter
from src.utils.image_embed import ImageGalleryView
from src.utils.discord_utils import is_valid_url, is_local_file

class DiscordMessenger:
    """Handles the sending of messages, files, and galleries to Discord."""

    def __init__(self, message_chunk_size: int = 1999):
        self.message_chunk_size = message_chunk_size

    async def send_message(self, bot: AICharacter, message: discord.Message, queue_item: QueueItem):
        """Main method to route and send a message based on the queue item."""
        await self._remove_processing_emoji(message)
        
        sanitized_item = self._sanitize_queue_item(queue_item)

        if sanitized_item.error:
            await self._send_regular_message(sanitized_item.error, message.channel)
        elif sanitized_item.dm or sanitized_item.default:
            await self._send_dm_message(sanitized_item, bot, message.author)
        else:
            await self._send_bot_message(sanitized_item, bot, message)
            
    async def _send_bot_message(self, queue_item: QueueItem, bot: AICharacter, message: discord.Message):
        """Sends a message as the bot character, potentially using webhooks."""
        context = message.channel
        response = self._clean_bot_name_from_response(queue_item.result, bot.name)
        chunks = self._chunk_message(response)
        
        webhook_context = await self._get_webhook_context(context, bot)

        # Send text chunks
        for chunk in chunks:
            if chunk.strip():
                await self._send_via_webhook(content=chunk, context=context, **webhook_context)
        
        # Send images if present
        if queue_item.images:
            image_urls, file_paths = self._categorize_images(queue_item.images)
            
            if image_urls:
                await self._send_image_gallery_webhook(image_urls, message, **webhook_context)
            if file_paths:
                await self._send_file_webhook(file_paths, message, **webhook_context)

    async def _get_webhook_context(self, context: discord.abc.Messageable, bot: AICharacter) -> dict:
        """Prepares the context needed for sending a webhook message."""
        channel, thread = self._get_channel_and_thread(context)
        webhook = await self._get_or_create_webhook(channel)
        
        return {
            "webhook": webhook,
            "username": bot.name or config.get_default_name(),
            "avatar_url": bot.avatar if str(bot.avatar) != "none" else config.get_default_avatar(),
            "thread": thread
        }

    async def _send_via_webhook(self, content: str, context, **kwargs):
        """Generic webhook sender."""
        # Extract kwargs passed from _get_webhook_context
        webhook = kwargs.get("webhook")
        thread = kwargs.get("thread")
        
        send_kwargs = {
            "content": content,
            "username": kwargs.get("username"),
            "avatar_url": kwargs.get("avatar_url"),
        }
        if thread:
            send_kwargs["thread"] = thread

        await webhook.send(**send_kwargs)

    async def _send_image_gallery_webhook(self, images: List[str], message: discord.Message, **kwargs):
        """Sends an image gallery via webhook."""
        webhook = kwargs.get("webhook")
        thread = kwargs.get("thread")
        
        if not images:
            await self._send_via_webhook(content="❌ No valid image URLs found.", context=message.channel, **kwargs)
            return
            
        view = ImageGalleryView(images, "Image Gallery")
        embed = view.create_embed()
        
        send_kwargs = {
            "embed": embed,
            "view": view,
            "username": kwargs.get("username"),
            "avatar_url": kwargs.get("avatar_url")
        }
        if thread:
            send_kwargs["thread"] = thread

        try:
            await webhook.send(**send_kwargs)
        except discord.HTTPException as e:
            error_msg = f"❌ Failed to send image gallery: {e}"
            print(f"DEBUG - Discord HTTPException: {e}")
            await self._send_via_webhook(content=error_msg, context=message.channel, **kwargs)
            
    async def _send_file_webhook(self, file_paths: List[str], message: discord.Message, **kwargs):
        """Sends local files via webhook."""
        webhook = kwargs.get("webhook")
        thread = kwargs.get("thread")

        discord_files = [discord.File(fp) for fp in file_paths if os.path.exists(fp)]
        
        if not discord_files:
            await self._send_via_webhook(content="❌ No valid files found to send.", context=message.channel, **kwargs)
            return

        send_kwargs = {
            "files": discord_files,
            "username": kwargs.get("username"),
            "avatar_url": kwargs.get("avatar_url")
        }
        if thread:
            send_kwargs["thread"] = thread

        try:
            await webhook.send(**send_kwargs)
        except discord.HTTPException as e:
            error_msg = f"❌ Failed to send files: {e}"
            await self._send_via_webhook(content=error_msg, context=message.channel, **kwargs)

    async def _send_dm_message(self, queue_item: QueueItem, bot: AICharacter, author: discord.User):
        """Send message as a direct message."""
        response = self._clean_bot_name_from_response(queue_item.result, bot.name)
        for chunk in self._chunk_message(response):
            await author.send(chunk)

    async def _send_regular_message(self, content: str, channel: discord.abc.Messageable):
        """Send a regular Discord message to a channel."""
        await channel.send(content)

    async def _get_or_create_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """Get an existing webhook or create a new one for the bot."""
        webhooks = await channel.webhooks()
        for wh in webhooks:
            if wh.name == config.bot_user.display_name:
                return wh
        return await channel.create_webhook(name=config.bot_user.display_name)
    
    # Helper and utility methods specific to sending
    @staticmethod
    def _categorize_images(images: List) -> tuple[List[str], List[str]]:
        urls, files = [], []
        if not images:
            return urls, files
        for img in images:
            img_str = str(img).strip()
            if not img_str: continue
            if is_local_file(img_str):
                files.append(img_str)
            elif is_valid_url(img_str):
                urls.append(img_str)
            else:
                 # Attempt to fix common URL-like strings
                if img_str.startswith('//'):
                    fixed_url = 'https:' + img_str
                elif '.' in img_str and not img_str.startswith('http'):
                    fixed_url = 'https://' + img_str
                else:
                    fixed_url = img_str

                if is_valid_url(fixed_url):
                    urls.append(fixed_url)
                else:
                    print(f"Warning: Invalid image source skipped: {img_str}")
        return urls, files

    @staticmethod
    def _get_channel_and_thread(context) -> tuple[discord.TextChannel, Optional[discord.Thread]]:
        if isinstance(context, discord.Thread):
            return context.parent, context
        return context, None

    def _chunk_message(self, message: str) -> List[str]:
        return [message[i:i + self.message_chunk_size] for i in range(0, len(message), self.message_chunk_size)]

    @staticmethod
    async def _remove_processing_emoji(message: discord.Message):
        try:
            await message.remove_reaction('✨', config.bot_user)
        except discord.HTTPException:
            pass
    
    @staticmethod
    def _sanitize_queue_item(item: QueueItem) -> QueueItem:
        if hasattr(item, "result") and isinstance(item.result, str):
            item.result = item.result.replace("@everyone", "@/everyone").replace("@here", "@/here")
        return item
        
    @staticmethod
    def _clean_bot_name_from_response(response: str, bot_name: str) -> str:
        return response.replace(f"{bot_name}:", "").strip()