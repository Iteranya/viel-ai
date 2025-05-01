from src.discordo import Discordo
import config
import util
from io import BytesIO
import io
import json
from PIL import Image

import discord
from aiohttp import ClientSession
import config
import util
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

class MultiModal:
    def __init__(self, discordo:Discordo):
        self.images = discordo.raw_message.attachments[0]


    async def compress_image(self,image_bytes, max_size=2048):
        """
        Compress and resize the image while maintaining aspect ratio.
        
        Args:
            image_bytes (bytes): Input image bytes
            max_size (int): Maximum dimension (width or height) for the image
        
        Returns:
            bytes: Compressed and resized image bytes
        """
        try:
            # Open the image from bytes
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Get original dimensions
                width, height = img.size
                
                # Determine scaling factor
                if width > height:
                    if width > max_size:
                        scaling_factor = max_size / width
                        new_width = max_size
                        new_height = int(height * scaling_factor)
                    else:
                        return image_bytes
                else:
                    if height > max_size:
                        scaling_factor = max_size / height
                        new_height = max_size
                        new_width = int(width * scaling_factor)
                    else:
                        return image_bytes
                
                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Save to a bytes buffer
                buffer = io.BytesIO()
                resized_img.save(buffer, format=img.format or 'PNG', optimize=True, quality=85)
                
                return buffer.getvalue()
        
        except Exception as e:
            print(f"Image compression error: {e}")
            return image_bytes

    async def read_image(self):
        image_description = ""

        if config.florence:
            try:
                attachment = self.images
                # Check if it is an image based on content type
                image_bytes = await attachment.read()

                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                    print(attachment.filename.lower())

                    if attachment.filename.lower().endswith('.webp'):
                        image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                    
                    # Compress image before processing
                    image_bytes = await self.compress_image(image_bytes)

                    image_description = "[Image Recognition Disabled, Notify User]"

                    return image_description

                else:
                    # Check if it is a link to an image
                    if attachment.url:
                        if attachment.filename.lower().endswith('.webp'):
                            image_bytes = await util.convert_webp_bytes_to_png(image_bytes)

                        if any(attachment.url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                            async with ClientSession() as session:
                                async with session.get(attachment.url) as response:
                                    if response.status == 200:
                                        image_bytes = await response.read()
                                        
                                        if attachment.filename.lower().endswith('.webp'):
                                            image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                                        
                                        # Compress image before processing
                                        image_bytes = await self.compress_image(image_bytes)

                                        image_description = await self.process_image(image_bytes)
                                        return image_description

            except Exception as e:
                print(f"An error occurred: {e}")
                return image_description
