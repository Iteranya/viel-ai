import re
import traceback
from duckduckgo_search import DDGS
from typing import *
import asyncio
import discord
from functools import partial
from src.utils.llm_new import generate_blank

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

async def research(search):
    # Generate search queries using LLM
    search_queries = await generate_blank(
        system=f"Your task is to generate a list of search terms for a given query. For example if the query is: \"Give me latest news on Ohio\" you will then write down in the following format: [(Latest news Ohio), (Events in Ohio), (Ohio News), (Ohio gossips), (Ohio current situation)]. Follow the format, you must put each of the search term between parenthesis.",
        user=f"The query is {search}, based on this query, write down 5 sentence/search term to look up. Use the given example as format.",
        assistant=f"Understood, here are the search query."
    )
    
    # Extract search terms using regex
    pattern = r'\((.*?)\)'
    queries = re.findall(pattern, search_queries)
    
    # If no parentheses found, fallback to the original search
    if not queries:
        queries = [search]
    
    # Perform searches using Bebek class
    all_results = []
    for query in queries:
        bebek = Bebek(query)
        try:
            # Get search results for each query
            results = await bebek.get_top_search_result(max_results=3)
            if results:
                all_results.extend(results)
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            continue
    
    # Concatenate and format results
    formatted_results = []
    for result in all_results:
        if isinstance(result, dict) and 'title' in result and 'href' in result:
            title = result.get('title', 'No title')
            url = result.get('href', '#')
            body = result.get('body', '')[:200] + "..." if result.get('body') else ''
            formatted_results.append(f"**{title}**\n{body}\n[Read more]({url})\n")
    
    # Return concatenated results
    final = "\n".join(formatted_results) if formatted_results else "No results found."
    return f"Web Search Result:\n{final}"