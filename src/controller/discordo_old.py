import asyncio
import json
import aiohttp
import discord
import re
import os
from typing import List, Optional, Union
from urllib.parse import urlparse
from src.controller import config
from src.models.queue import QueueItem
from src.models.aicharacter import AICharacter
from src.utils.image_embed import ImageGalleryView
from src.utils.image_eval import describe_image, strip_thinking


class DiscordHandler:
    """Handles Discord interactions including message history, sending, and webhooks."""
    
    def __init__(self):
        self.message_chunk_size = 1999
        self.captions_file = "res/captions.jsonl"
        self.captions_cache = self._load_captions()
        self.temp_image_dir = "temp_images"
        os.makedirs(self.temp_image_dir, exist_ok=True)

    def _load_captions(self) -> dict:
        """Loads message_id:caption pairs from the jsonl file."""
        cache = {}
        if not os.path.exists(self.captions_file):
            return cache
        try:
            with open(self.captions_file, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    cache[data["message_id"]] = data["caption"]
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load captions file: {e}")
        return cache
    
    def _save_caption(self, message_id: int, caption: str):
        """Saves a new caption to the jsonl file and in-memory cache."""
        self.captions_cache[message_id] = caption
        entry = {"message_id": message_id, "caption": caption}
        try:
            with open(self.captions_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError as e:
            print(f"Error: Could not save caption to file: {e}")
    
    async def _get_image_caption(self, message: discord.Message) -> Optional[str]:
        """
        Gets an image caption for a message, relying solely on the captions.jsonl file.
        If not found, it generates and saves a new one.
        Processes only the first valid image attachment.
        """
        if not message.attachments:
            return None

        # ### MODIFIED ###
        # Search the captions.jsonl file directly instead of checking the cache.
        if os.path.exists(self.captions_file):
            try:
                with open(self.captions_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if data.get("message_id") == message.id:
                                # Found in the file, return the caption.
                                return data.get("caption")
                        except json.JSONDecodeError:
                            # Ignore corrupted lines
                            continue
            except IOError as e:
                print(f"Warning: Could not read captions file during lookup: {e}")

        # If not found in the file, proceed to generate a new one.
        image_attachment = None
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                image_attachment = attachment
                break

        if not image_attachment:
            return None

        # Download, describe, and save
        temp_path = os.path.join(self.temp_image_dir, f"{message.id}_{image_attachment.filename}")
        try:
            # Asynchronously download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(image_attachment.url) as resp:
                    if resp.status == 200:
                        with open(temp_path, "wb") as f:
                            f.write(await resp.read())
                    else:
                        return "[Could not download image for description]"

            # Get description from the downloaded file
            print(f"Generating new caption for message {message.id}...")
            caption = strip_thinking(await describe_image(temp_path))
            print(caption)

            # ### MODIFIED ###
            # Save the new caption directly to the file, bypassing the cache.
            # Note: This is less efficient but fulfills the request.
            entry = {"message_id": message.id, "caption": caption}
            try:
                if "<ERROR>" not in caption:
                    with open(self.captions_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry) + "\n")
                    # Also add to cache so the original _save_caption method isn't needed
                    # and to prevent potential inconsistencies if other methods use it.
                    self.captions_cache[message.id] = caption
            except IOError as e:
                print(f"Error: Could not save caption to file: {e}")

            return caption

        except Exception as e:
            print(f"Failed during caption generation for message {message.id}: {e}")
            return "[Error generating image description]"
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    
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
        Includes descriptions for messages with image attachments.
        """
        context = self.get_context(message)

        # Fetch messages first
        messages = [msg async for msg in context.history(limit=limit)]

       # Create formatting tasks to run concurrently
        tasks = [self._format_message(msg) for msg in messages]
        formatted_messages = await asyncio.gather(*tasks)

        # Filter out any ignored messages (which return None)
        history = [fm for fm in formatted_messages if fm]

        # Reverse to get chronological order
        history.reverse()

        # Join messages and apply reset logic
        content = "\n\n".join(history)
        content = self._apply_reset_logic(content)
        return content + "\n\n"
    
    async def _format_message(self, message: discord.Message) -> Optional[str]:
        """
        Format a Discord message, adding image descriptions if attachments exist.
        """
        name = self._sanitize_name(message.author.display_name)
        content = self._clean_content(message.content)

        # ### NEW ###: Get image caption if an image is attached
        image_caption = await self._get_image_caption(message)
        if image_caption:
            # Append the description to the message content
            content += f" [Attached File/Image Description: {image_caption}]"

        if content.startswith("[System"):
            return content.strip()
        elif content.startswith("//"):
            return None
        elif content.startswith("^"):
            content = content[1:]
            return f"[Reply]{name}: {content.strip()}[End]"
        else:
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
    history = await discord_handler.get_history(message, limit)
    return history

async def send(bot, message: discord.Message, queue_item: QueueItem):
    """Backward compatibility function."""
    await discord_handler.send_message(bot, message, queue_item)