import discord
import re
import os
from typing import List, Optional, Union
from urllib.parse import urlparse
from src.controller import config
from src.models.queue import QueueItem
from src.models.aicharacter import AICharacter
from src.utils.image_embed import ImageGalleryView


class DiscordHandler:
    """Handles Discord interactions including message history, sending, and webhooks."""
    
    def __init__(self):
        self.message_chunk_size = 1999
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if a string is a valid URL."""
        try:
            result = urlparse(str(url))
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
    @staticmethod
    def _is_local_file(path: str) -> bool:
        """Check if a string represents a local file path."""
        try:
            # Check if it's a file path (contains file extension and exists)
            path_str = str(path).strip()
            return (
                not path_str.startswith(('http://', 'https://')) and
                '.' in path_str and
                os.path.exists(path_str)
            )
        except Exception:
            return False
    
    @staticmethod
    def _categorize_images(images: List) -> tuple[List[str], List[str]]:
        """Categorize images into URLs and local files."""
        if not images:
            return [], []
        
        urls = []
        files = []
        
        for img in images:
            img_str = str(img).strip()
            
            # Skip empty strings
            if not img_str:
                continue
            
            # Check if it's a local file first
            if DiscordHandler._is_local_file(img_str):
                files.append(img_str)
                continue
            
            # Process as URL
            # Add https:// if missing protocol but looks like a URL
            if img_str.startswith('//'):
                img_str = 'https:' + img_str
            elif not img_str.startswith(('http://', 'https://')) and '.' in img_str:
                img_str = 'https://' + img_str
            
            # Validate URL
            if DiscordHandler._is_valid_url(img_str):
                urls.append(img_str)
            else:
                print(f"Warning: Invalid image URL skipped: {img_str}")
        
        return urls, files
    
    @staticmethod
    def _sanitize_image_urls(images: List) -> List[str]:
        """Sanitize and validate image URLs."""
        urls, _ = DiscordHandler._categorize_images(images)
        return urls
    
    @staticmethod
    def get_context(message: discord.Message) -> Union[discord.TextChannel, discord.Thread]:
        """Get the channel context from a Discord message."""
        return message.channel
    
    async def get_history(self, message: discord.Message, limit: int = 100) -> str:
        """
        Retrieve and format message history from a Discord channel.
        
        Args:
            message: The Discord message to get context from
            limit: Maximum number of messages to retrieve
            
        Returns:
            Formatted history string
        """
        history = []
        context = self.get_context(message)
        
        async for msg in context.history(limit=limit):
            formatted_message = self._format_message(msg)
            if formatted_message:
                history.append(formatted_message)
        
        # Reverse to get chronological order
        history.reverse()
        
        # Join messages and apply reset logic
        content = "\n\n".join(history)
        content = self._apply_reset_logic(content)
        return content + "\n\n"
    
    def _format_message(self, message: discord.Message) -> Optional[str]:
        """
        Format a Discord message based on its content and prefix.
        
        Args:
            message: The Discord message to format
            
        Returns:
            Formatted message string or None if message should be ignored
        """
        name = self._sanitize_name(message.author.display_name)
        content = self._clean_content(message.content)
        
        if content.startswith("[System"):
            return content.strip()
        elif content.startswith("//"):
            # Ignore comments
            return None
        elif content.startswith("^"):
            # Reply format
            content = content[1:]  # Remove ^ prefix
            return f"[Reply]{name}: {content.strip()}[End]"
        else:
            # Regular message
            return f"[Reply]{name}: {content.strip()}[End]"
    
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
        """Apply reset logic to trim history from last [RESET] marker."""
        last_reset = history.rfind("[RESET]")
        if last_reset != -1:
            return history[last_reset + len("[RESET]"):].strip()
        return history.strip()
    
    @staticmethod
    def _sanitize_queue_item(item: QueueItem) -> QueueItem:
        """Sanitize queue item to prevent @everyone and @here mentions."""
        if hasattr(item, "result") and isinstance(item.result, str):
            item.result = item.result.replace("@everyone", "@/everyone").replace("@here", "@/here")
        return item
    
    async def send_message(self, bot: AICharacter, message: discord.Message, queue_item: QueueItem):
        """
        Main method to send a message based on queue item type.
        
        Args:
            bot: The AI character bot
            message: Original Discord message
            queue_item: Queue item containing response data
        """
        # Remove processing emoji
        await self._remove_processing_emoji(message)
        
        # Sanitize the queue item
        queue_item = self._sanitize_queue_item(queue_item)
        
        # Route to appropriate sender based on queue item properties
        if queue_item.error:
            await self._send_error_message(queue_item, message)
        elif queue_item.dm:
            await self._send_dm_message(queue_item, bot, message)
        elif queue_item.default:
            await self._send_dm_message(queue_item, bot, message)
        else:
            await self._send_bot_message(queue_item, bot, message)
    
    async def _remove_processing_emoji(self, message: discord.Message):
        """Remove processing emoji from message."""
        try:
            await message.remove_reaction('✨', config.bot_user)
        except Exception:
            # Silently ignore emoji removal failures
            pass
    
    async def _send_error_message(self, queue_item: QueueItem, message: discord.Message):
        """Send error message as system message."""
        await self._send_regular_message(queue_item.error, message)
    
    async def _send_dm_message(self, queue_item: QueueItem, bot: AICharacter, message: discord.Message):
        """Send message as direct message."""
        response = self._clean_bot_name_from_response(queue_item.result, bot.name)
        chunks = self._chunk_message(response)
        
        for chunk in chunks:
            await self._send_regular_message(chunk, message)
    
    async def _send_bot_message(self, queue_item: QueueItem, bot: AICharacter, message: discord.Message):
        """Send message as bot character using webhooks."""
        response = self._clean_bot_name_from_response(queue_item.result, bot.name)
        chunks = self._chunk_message(response)
        
        # Send text chunks
        for chunk in chunks:
            await self._send_webhook_message(
                content=chunk,
                avatar_url=bot.avatar,
                username=bot.name,
                message=message
            )
        
        # Send images if present
        if queue_item.images:
            # Categorize images into URLs and files
            image_urls, file_paths = self._categorize_images(queue_item.images)
            
            # Send URL-based images as gallery
            if image_urls:
                await self._send_webhook_message(
                    content=None,
                    avatar_url=bot.avatar,
                    username=bot.name,
                    images=image_urls,
                    message=message
                )
            
            # Send local files as attachments
            if file_paths:
                await self._send_webhook_message(
                    content=None,
                    avatar_url=bot.avatar,
                    username=bot.name,
                    files=file_paths,
                    message=message
                )
    
    @staticmethod
    def _clean_bot_name_from_response(response: str, bot_name: str) -> str:
        """Remove bot name prefix from response."""
        return response.replace(f"{bot_name}:", "")
    
    def _chunk_message(self, message: str) -> List[str]:
        """Split message into chunks of specified size."""
        return [message[i:i + self.message_chunk_size] 
                for i in range(0, len(message), self.message_chunk_size)]
    
    async def _send_regular_message(self, content: str, message: discord.Message):
        """Send a regular Discord message."""
        await message.channel.send(content)
    
    async def _send_webhook_message(
        self,
        content: Optional[str] = None,
        avatar_url: Optional[str] = None,
        username: Optional[str] = None,
        images: Optional[List] = None,
        files: Optional[List] = None,
        message: discord.Message = None
    ):
        """
        Send message through Discord webhook.
        
        Args:
            content: Message content
            avatar_url: Avatar URL for the webhook
            username: Username for the webhook
            images: List of image URLs to send as gallery
            files: List of local file paths to send as attachments
            message: Original Discord message for context
        """
        if not message:
            return
        
        context = message.channel
        channel, thread = self._get_channel_and_thread(context)
        
        # Set defaults if not provided
        avatar_url = avatar_url if avatar_url and str(avatar_url) != "none" else config.get_default_avatar()
        username = username or config.get_default_name()
        
        # Get or create webhook
        webhook = await self._get_or_create_webhook(channel)
        
        # Send content
        if images:
            await self._send_image_gallery_webhook(images, avatar_url, username, message)
        elif files:
            await self._send_file_webhook(files, avatar_url, username, message)
        else:
            await self._send_text_webhook(webhook, content, username, avatar_url, thread)
    
    @staticmethod
    def _get_channel_and_thread(context) -> tuple:
        """Extract channel and thread from context."""
        if isinstance(context, discord.TextChannel):
            return context, None
        elif isinstance(context, discord.Thread):
            return context.parent, context
        else:
            return context, None
    
    async def _get_or_create_webhook(self, channel) -> discord.Webhook:
        """Get existing webhook or create new one."""
        webhook_list = await channel.webhooks()
        
        # Look for existing webhook
        for webhook in webhook_list:
            if webhook.name == config.bot_user.display_name:
                return webhook
        
        # Create new webhook if not found
        return await channel.create_webhook(name=config.bot_user.display_name)
    
    async def _send_text_webhook(
        self,
        webhook: discord.Webhook,
        content: str,
        username: str,
        avatar_url: str,
        thread: Optional[discord.Thread]
    ):
        """Send text content through webhook."""
        kwargs = {
            "content": content,
            "username": username,
            "avatar_url": avatar_url
        }
        
        if thread:
            kwargs["thread"] = thread
        
        await webhook.send(**kwargs)
    
    async def _send_file_webhook(
        self,
        file_paths: List[str],
        avatar_url: str,
        username: str,
        message: discord.Message
    ):
        """Send file attachments through webhook."""
        context = message.channel
        channel, thread = self._get_channel_and_thread(context)
        
        # Get or create webhook
        webhook = await self._get_or_create_webhook(channel)
        
        try:
            # Create Discord File objects from file paths
            discord_files = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    discord_files.append(discord.File(file_path))
                else:
                    print(f"Warning: File not found: {file_path}")
            
            if not discord_files:
                # Send error message if no valid files found
                await self._send_webhook_message(
                    content="❌ No valid files found to send.",
                    avatar_url=avatar_url,
                    username=username,
                    message=message
                )
                return
            
            # Send files through webhook
            kwargs = {
                "files": discord_files,
                "username": username,
                "avatar_url": avatar_url
            }
            
            if thread:
                kwargs["thread"] = thread
            
            await webhook.send(**kwargs)
            
        except discord.HTTPException as e:
            # If file sending fails, send error message
            error_msg = f"❌ Failed to send files: {str(e)}"
            print(f"DEBUG - Discord HTTPException when sending files: {e}")
            await self._send_webhook_message(
                content=error_msg,
                avatar_url=avatar_url,
                username=username,
                message=message
            )
        except Exception as e:
            # Handle other exceptions
            error_msg = f"❌ Unexpected error sending files: {str(e)}"
            print(f"DEBUG - Unexpected error when sending files: {e}")
            await self._send_webhook_message(
                content=error_msg,
                avatar_url=avatar_url,
                username=username,
                message=message
            )
    
    async def send_image_gallery(
        self,
        images: List,
        message: discord.Message,
        title: str = "Image Gallery"
    ):
        """Send image gallery as regular message."""
        if not images:
            return
        
        # Only handle URLs for gallery, files should be sent as attachments
        sanitized_images = self._sanitize_image_urls(images)
        if not sanitized_images:
            await message.channel.send("❌ No valid image URLs found.")
            return
        
        view = ImageGalleryView(sanitized_images, title)
        embed = view.create_embed()
        await message.channel.send(embed=embed, view=view)
    
    async def _send_image_gallery_webhook(
        self,
        images: List,
        avatar_url: str,
        username: str,
        message: discord.Message,
        title: str = "Image Gallery"
    ):
        """Send image gallery through webhook."""
        if not images:
            return
        
        # Debug: Print original images
        print(f"DEBUG - Original images: {images}")
        
        # Sanitize images first (only URLs)
        sanitized_images = self._sanitize_image_urls(images)
        print(f"DEBUG - Sanitized images: {sanitized_images}")
        
        if not sanitized_images:
            # Send error message through webhook instead of failing
            await self._send_webhook_message(
                content="❌ No valid image URLs found.",
                avatar_url=avatar_url,
                username=username,
                message=message
            )
            return
        
        context = message.channel
        channel, thread = self._get_channel_and_thread(context)
        
        # Fallback to regular message for unsupported channel types
        if not isinstance(context, (discord.TextChannel, discord.Thread)):
            await self.send_image_gallery(sanitized_images, message, title)
            return
        
        # Set defaults
        avatar_url = avatar_url if avatar_url and str(avatar_url) != "none" else config.get_default_avatar()
        username = username or config.get_default_name()
        
        # Get or create webhook
        webhook = await self._get_or_create_webhook(channel)
        
        try:
            # Create gallery view and embed with sanitized images
            view = ImageGalleryView(sanitized_images, title)
            embed = view.create_embed()
            
            # Debug: Print embed dict to see what's being sent
            print(f"DEBUG - Embed dict: {embed.to_dict()}")
            
            # Send through webhook
            kwargs = {
                "embed": embed,
                "view": view,
                "username": username,
                "avatar_url": avatar_url
            }
            
            if thread:
                kwargs["thread"] = thread
            
            await webhook.send(**kwargs)
            
        except discord.HTTPException as e:
            # If embed still fails, send a fallback message
            error_msg = f"❌ Failed to send image gallery: {str(e)}"
            print(f"DEBUG - Discord HTTPException: {e}")
            print(f"DEBUG - Error details: {e.response} {e.text if hasattr(e, 'text') else 'No additional text'}")
            await self._send_webhook_message(
                content=error_msg,
                avatar_url=avatar_url,
                username=username,
                message=message
            )


# Convenience functions for backward compatibility
discord_handler = DiscordHandler()

def get_context(message: discord.Message):
    """Backward compatibility function."""
    return discord_handler.get_context(message)

async def get_history(message: discord.Message, limit: int = 100):
    """Backward compatibility function."""
    return await discord_handler.get_history(message, limit)

async def send(bot, message: discord.Message, queue_item: QueueItem):
    """Backward compatibility function."""
    await discord_handler.send_message(bot, message, queue_item)