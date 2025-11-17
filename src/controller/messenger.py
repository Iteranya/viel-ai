# In a file like src/controller/discord_messenger.py

import re
import discord
import os
from typing import List, Optional

# Adjust import paths as needed
from src.models.queue import QueueItem
from src.models.aicharacter import ActiveCharacter
from api.models.models import BotConfig
from src.utils.image_embed import ImageGalleryView
from src.utils.discord_utils import is_valid_url, is_local_file


class DiscordMessenger:
    """Handles the sending of messages, files, and galleries to Discord."""

    def __init__(self, bot, message_chunk_size: int = 1999):
        self.bot = bot
        self.db = bot.db
        self.bot_config = BotConfig(**self.db.list_configs())
        self.message_chunk_size = message_chunk_size

    async def send_message(self, character: ActiveCharacter, message: discord.Message, queue_item: QueueItem):
        """Main method to route and send a message based on the queue item."""
        sanitized_item = self._sanitize_queue_item(queue_item)

        if isinstance(message.channel, discord.DMChannel):
            await self._send_dm_message(sanitized_item, character, message.author)
        else:
            await self._send_guild_message(sanitized_item, character, message)
            
    async def _send_guild_message(self, queue_item: QueueItem, character: ActiveCharacter, message: discord.Message):
        """Sends a message as the bot character within a server, using webhooks."""
        context = message.channel
        response = self._clean_bot_name_from_response(queue_item.result, character.name)
        chunks = self._chunk_message(response)
        
        webhook_context = await self._get_webhook_context(context, character)

        for i, chunk in enumerate(chunks):
            if chunk.strip():
                # For the first chunk, include a reply to the user's message
                reply_to = message if i == 0 else None
                await self._send_via_webhook(content=chunk, context=context, reply_to=reply_to, **webhook_context)
        
        # Image sending logic can be added here if needed, similar to the original

    async def _get_webhook_context(self, context: discord.abc.Messageable, character: ActiveCharacter) -> dict:
        """Prepares the context needed for sending a webhook message."""
        channel, thread = self._get_channel_and_thread(context)
        webhook = await self._get_or_create_webhook(channel)
        
        # Use character data, fall back to default character's avatar if needed
        avatar_url = character.avatar
        if not avatar_url or str(avatar_url).lower() == "none":
            default_char = self.db.get_character(self.bot_config.default_character)
            if default_char:
                avatar_url = default_char.get('data', {}).get('avatar')

        return {
            "webhook": webhook,
            "username": character.name,
            "avatar_url": avatar_url,
            "thread": thread
        }

    async def _send_via_webhook(self, content: str, context, reply_to: Optional[discord.Message] = None, **kwargs):
        """Generic webhook sender with reply support."""
        webhook = kwargs.get("webhook")
        thread = kwargs.get("thread")
        
        # Use AllowedMentions to control pings. Replying pings by default.
        allowed_mentions = discord.AllowedMentions(replied_user=True)

        send_kwargs = {
            "content": content,
            "username": kwargs.get("username"),
            "avatar_url": kwargs.get("avatar_url"),
            "allowed_mentions": allowed_mentions
        }
        if thread:
            send_kwargs["thread"] = thread

        # discord.py webhook send does not support `reference` directly.
        # We simulate a reply by mentioning the user at the start of the message.
        if reply_to:
            # We don't need this anymore since we send chunks with replies
            # send_kwargs["content"] = f"> {reply_to.author.mention}\n{content}"
            pass

        await webhook.send(**send_kwargs)

    async def _send_dm_message(self, queue_item: QueueItem, character: ActiveCharacter, author: discord.User):
        """Send message as a direct message."""
        response = self._clean_bot_name_from_response(queue_item.result, character.name)
        for chunk in self._chunk_message(response):
            await author.send(chunk)

    async def _get_or_create_webhook(self, channel: discord.TextChannel) -> discord.Webhook:
        """Get an existing webhook or create a new one for the bot."""
        # Use the bot's actual user info, passed during initialization
        for wh in await channel.webhooks():
            if wh.user == self.bot.user:
                return wh
        # Create a new webhook named after the bot
        return await channel.create_webhook(name=self.bot.user.display_name)
    
    # --- Helper Methods ---
    @staticmethod
    def _get_channel_and_thread(context) -> tuple[discord.TextChannel, Optional[discord.Thread]]:
        if isinstance(context, discord.Thread):
            return context.parent, context
        return context, None

    def _chunk_message(self, message: str) -> List[str]:
        return [message[i:i + self.message_chunk_size] for i in range(0, len(message), self.message_chunk_size)]
        
    @staticmethod
    def _sanitize_queue_item(item: QueueItem) -> QueueItem:
        if hasattr(item, "result") and isinstance(item.result, str):
            item.result = (item.result
                .replace("@everyone", "@\u200beveryone") # Use zero-width space to break ping
                .replace("@here", "@\u200bhere")
                .replace("<|end of sentence|>", ""))
        return item
        
    @staticmethod
    def _clean_bot_name_from_response(response: str, bot_name: str) -> str:
        # Use a regex for case-insensitive and more robust cleaning
        return re.sub(rf'^{re.escape(bot_name)}:\s*', '', response, flags=re.IGNORECASE).strip()