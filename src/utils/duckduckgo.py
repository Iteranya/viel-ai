import traceback
import discord.types
import discord.types.embed
from duckduckgo_search import DDGS
from io import BytesIO
from aiohttp import ClientSession
from typing import *
import asyncio
import discord
import config
from functools import partial

class Bebek:
    def __init__(self, query: str, inline=True):
        self.query = self.extract_between_quotes(query)
        self.ddgs = DDGS()

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run synchronous DDGS methods in a thread pool executor"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def get_top_search_result(self, max_results: int = 5) -> dict:
        try:
            # Run the synchronous text search in a thread pool
            results = await self._run_in_executor(
                self.ddgs.text,
                self.query,
                region='wt-wt',
                safesearch="off",
                max_results=max_results
            )
            return list(results)  # Convert generator to list
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred during search: {e}")
            return {}

    async def get_news(self, max_results: int = 5) -> dict:
        try:
            results = await self._run_in_executor(
                self.ddgs.news,
                self.query,
                region='wt-wt',
                safesearch="off",
                max_results=max_results
            )
            return list(results)
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred during search: {e}")
            return {}

    async def get_image_link(self, safesearch: str = 'off', max_results: int = 5) -> list:
        try:
            results = await self._run_in_executor(
                self.ddgs.images,
                self.query,
                region='wt-wt',
                safesearch=safesearch,
                max_results=max_results
            )
            return self.create_embeds(list(results))
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred during search: {e}")
            return []

    async def get_video_link(self, max_results: int = 5) -> str:
        try:
            results = await self._run_in_executor(
                self.ddgs.videos,
                self.query,
                region='wt-wt',
                safesearch='off',
                max_results=max_results
            )
            return self.extract_links(list(results))
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred during search: {e}")
            return []

    def extract_links(self, results):
        links = ["[.]("+result['content']+")" for result in results if 'content' in result]
        return " ".join(links)
    
    def create_embeds(self, results, media_type='image'):
        embeds = []
        for result in results:
            if media_type == 'image':
                embed = discord.Embed(description=result['title'], url=result['image'])
                embed.set_image(url=result['image'])
            elif media_type == 'video':
                embed = discord.Embed(title=result['title'], description=result['content'], url=result['content'], type='video')
            else:
                raise ValueError("media_type must be 'image' or 'video'")
            embeds.append(embed)
        return embeds

    def extract_between_quotes(self, input_string):
        import re
        match = re.search(r"\((.*?)\)", input_string)
        return match.group(1) if match else input_string
