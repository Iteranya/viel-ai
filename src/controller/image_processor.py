# src/services/image_processor.py

import aiohttp
import os
import discord
from src.utils.image_eval import describe_image, strip_thinking

class ImageProcessor:
    """Handles downloading and generating descriptions for images."""

    def __init__(self, temp_dir: str = "temp_images"):
        self.temp_image_dir = temp_dir
        os.makedirs(self.temp_image_dir, exist_ok=True)

    async def describe_attachment(self, attachment: discord.Attachment) -> str:
        """Downloads an image, generates a caption, and cleans up."""
        if not (attachment.content_type and attachment.content_type.startswith("image/")):
            return "[Attachment is not a valid image]"

        temp_path = os.path.join(self.temp_image_dir, f"{attachment.id}_{attachment.filename}")

        try:
            # Asynchronously download the image
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        return f"[Could not download image, status: {resp.status}]"
                    with open(temp_path, "wb") as f:
                        f.write(await resp.read())

            # Get description from the downloaded file
            print(f"Generating new caption for image: {attachment.filename}")
            caption = strip_thinking(await describe_image(temp_path))
            
            if "<ERROR>" in caption:
                print(f"Error generating caption: {caption}")
                return "[Error generating image description]"
            
            print(f"Generated caption: {caption}")
            return caption

        except Exception as e:
            print(f"Failed during caption generation for attachment {attachment.id}: {e}")
            return "[Error generating image description]"
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)