# src/services/history_formatter.py

import asyncio
import re
import discord
from typing import Optional
from src.controller.caption import CaptionManager
from src.controller.image_processor import ImageProcessor
from src.utils.discord_utils import extract_valid_urls
from src.utils.web_eval import fetch_body
class HistoryFormatter:
    """Fetches and formats Discord message history for an AI model."""

    def __init__(self, caption_manager: CaptionManager, image_processor: ImageProcessor):
        self.caption_manager = caption_manager
        self.image_processor = image_processor

    async def get_history(self, context: discord.abc.Messageable, limit: int = 100) -> str:
        """Retrieve and format message history from a Discord channel."""
        messages = [msg async for msg in context.history(limit=limit)]
        
        tasks = [self._format_message(msg) for msg in messages]
        formatted_messages = await asyncio.gather(*tasks)

        history = [fm for fm in formatted_messages if fm]
        history.reverse()  # Chronological order

        content = "\n\n".join(history)
        return self._apply_reset_logic(content) + "\n\n"

    async def _format_message(self, message: discord.Message) -> Optional[str]:
        """Formats a single Discord message, including generating image captions if needed."""
        name = self._sanitize_name(message.author.display_name)
        content = self._clean_content(message.content)

        image_caption = await self._get_image_caption(message)
        if image_caption:
            if "[Error generating image description]" not in image_caption:
                content += f" [Attached File/Image Description: {image_caption}]"
    
        link_caption = await self._get_link_caption(message)
        if link_caption:
            content += link_caption


        # Message routing and formatting logic
        if content.startswith("[System"):
            return content.strip()
        if content.startswith("//"):
            return None  # Ignore comments
        
        prefix = "[Reply]"
        if content.startswith("^"):
            content = content[1:]
        
        return f"{prefix}{name}: {content.strip()}[End]"

    async def _get_image_caption(self, message: discord.Message) -> Optional[str]:
        """
        Gets an image caption for a message.
        1. Checks the cache.
        2. If not found, generates a new one, saves it, and returns it.
        """
        if not message.attachments:
            return None

        # Check cache first for efficiency
        caption = self.caption_manager.get_caption(message.id)
        if caption:
            return caption

        # If not in cache, process the first valid image attachment
        image_attachment = next((att for att in message.attachments if att.content_type and att.content_type.startswith("image/")), None)
        
        if not image_attachment:
            return None

        # Generate new caption
        new_caption = await self.image_processor.describe_attachment(image_attachment)
        
        # Save the new caption to the cache and file
        if new_caption and "[Error" not in new_caption:
            self.caption_manager.save_caption(message.id, new_caption)
        
        return new_caption
    
    async def _get_link_caption(self, message: discord.Message) -> Optional[str]:
        """
        Gets a link caption for a message.
        1. Checks the cache.
        2. If not found, generates a new one, saves it, and returns it.
        """
        # Check cache first
        caption = self.caption_manager.get_caption(message.id)
        if caption:
            return caption

        links = extract_valid_urls(message.content)
        if not links:
            return None

        # Fetch all links concurrently
        tasks = [fetch_body(link) for link in links]
        captions = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None or failed fetches
        clean_captions = [c for c in captions if isinstance(c, str) and c.strip()]
        if not clean_captions:
            return None

        # Format into a consistent caption block
        new_caption = "<site_content>\n" + "\n".join(clean_captions) + "\n</site_content>"

        # Save the new caption to cache
        if new_caption and "[Error" not in new_caption:
            self.caption_manager.save_caption(message.id, new_caption)

        return new_caption
        


    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Remove special characters from display name."""
        return re.sub(r'[^\w]', '', str(name))

    @staticmethod
    def _clean_content(content: str) -> str:
        """Remove user mentions from message content."""
        return re.sub(r'<@!?[0-9]+>', '', content)

    @staticmethod
    def _apply_reset_logic(history: str) -> str:
        """Trim history from last [RESET] marker."""
        last_reset = history.rfind("[RESET]")
        if last_reset != -1:
            return history[last_reset + len("[RESET]"):].strip()
        return history.strip()