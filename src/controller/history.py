import asyncio
import re
import discord
import os
import uuid
from typing import Optional

# Adjust import paths to match your project structure
from api.db.database import Database
from api.models.models import BotConfig
from src.utils.image_eval import describe_image
from src.utils.web_eval import fetch_body
from src.utils.discord_utils import extract_valid_urls


def get_bot_config(db: Database) -> BotConfig:
    """Helper to fetch all config key-values from the DB and return a BotConfig object."""
    return BotConfig(**db.list_configs())


class _HistoryFormatter:
    """Internal class to fetch and format Discord message history for an AI model."""

    def __init__(self, db: Database):
        self.db = db
        self.bot_config = get_bot_config(db)

    async def format_history(self, context: discord.abc.Messageable, limit: int = 100) -> str:
        """Retrieve and format message history from a Discord channel."""
        # Fetch messages in reverse chronological order (newest first)
        messages = [msg async for msg in context.history(limit=limit)]
        
        tasks = [self._format_message(msg) for msg in messages]
        formatted_messages = await asyncio.gather(*tasks)

        # Filter out None values (e.g., ignored comments)
        history = [fm for fm in formatted_messages if fm]
        history.reverse()  # Put back into chronological order (oldest first)

        content = "\n\n".join(history)
        return self._apply_reset_logic(content) + "\n\n"

    async def _format_message(self, message: discord.Message) -> Optional[str]:
        """Formats a single Discord message."""
        name = self._sanitize_name(message.author.display_name)
        content = self._clean_content(message.content)

        # Combine image and link captions into the content
        image_caption = await self._get_image_caption(message)
        if image_caption:
            content += f" [Attached Image Description: {image_caption}]"
    
        link_caption = await self._get_link_caption(message)
        if link_caption:
            content += link_caption

        if content.startswith("//"):
            return None  # Ignore comments

        prefix = "[Reply]"
        if content.startswith("^"):
            content = content[1:]
        
        return f"{prefix} {name}: {content.strip()} [End]"

    async def _get_image_caption(self, message: discord.Message) -> Optional[str]:
        """
        Gets an image caption. Checks the database first. Only generates a new one
        if multimodal is enabled in the bot's config.
        """
        if not message.attachments:
            return None

        message_id_str = str(message.id)
        # 1. Always check the database first for an existing caption
        caption = self.db.get_caption(message_id_str)
        if caption:
            return caption

        # 2. If no caption exists, check if we are allowed to generate one
        if not self.bot_config.multimodal_enable:
            return None  # Generation is disabled, so we return nothing

        # 3. If enabled, proceed with generation
        image_attachment = next((att for att in message.attachments if att.content_type and att.content_type.startswith("image/")), None)
        if not image_attachment:
            return None

        temp_image_path = None
        try:
            # Create a unique temporary filename to avoid conflicts
            ext = image_attachment.filename.split('.')[-1]
            temp_image_path = f"temp_caption_{uuid.uuid4()}.{ext}"
            await image_attachment.save(temp_image_path)
            
            # Generate new caption using our standalone, database-aware function
            new_caption = await describe_image(temp_image_path, self.db)
            
            # Save the new caption to the database for future use
            if new_caption and "<ERROR>" not in new_caption:
                self.db.set_caption(message_id_str, new_caption)
            
            return new_caption
        finally:
            # Crucially, ensure the temporary file is always deleted
            if temp_image_path and os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    
    async def _get_link_caption(self, message: discord.Message) -> Optional[str]:
        """Gets a summary of links in a message. Checks database first."""
        message_id_str = str(message.id)
        # Check database first
        caption = self.db.get_caption(message_id_str)
        if caption:
            return caption

        links = extract_valid_urls(message.content)
        if not links:
            return None

        tasks = [fetch_body(link) for link in links]
        captions = await asyncio.gather(*tasks, return_exceptions=True)

        clean_captions = [c for c in captions if isinstance(c, str) and c.strip()]
        if not clean_captions:
            return None

        new_caption = "<site_content>\n" + "\n".join(clean_captions) + "\n</site_content>"

        if new_caption and "<ERROR>" not in new_caption:
            self.db.set_caption(message_id_str, new_caption)

        return new_caption
        
    @staticmethod
    def _sanitize_name(name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_-]', '', str(name))

    @staticmethod
    def _clean_content(content: str) -> str:
        return re.sub(r'<@!?\d+>', '', content).strip()

    @staticmethod
    def _apply_reset_logic(history: str) -> str:
        last_reset = history.rfind("[RESET]")
        return history[last_reset + len("[RESET]"):].strip() if last_reset != -1 else history.strip()

# --- Public API Function ---
async def get_history(context: discord.abc.Messageable, db: Database, limit: int = 100) -> str:
    """
    The main entry point for fetching and formatting message history.
    It initializes and uses the internal _HistoryFormatter class.
    
    Args:
        context: The Discord channel or DM to fetch history from.
        db: An active database connection instance.
        limit: The number of messages to fetch.
        
    Returns:
        A fully formatted string of the conversation history.
    """

    formatter = _HistoryFormatter(db)
    return await formatter.format_history(context, limit=limit)