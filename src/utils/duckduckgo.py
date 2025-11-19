import re
import traceback
from ddgs import DDGS
from typing import *
import asyncio
import discord
from functools import partial
from src.utils.llm_new import generate_blank
from src.utils.web_eval import fetch_body
from api.db.database import Database

class Bebek:
    def __init__(self, query: str, db:Database,inline=True):
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
                max_results=max_results,
                backend = 'lite'
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
                max_results=max_results,
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
                max_results=max_results,
            )
            return list(results)
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

    def extract_between_quotes(self, input_string):
        import re
        match = re.search(r"\((.*?)\)", input_string)
        return match.group(1) if match else input_string

async def research(search, db):
    # Generate search queries using LLM
    search_queries = await generate_blank(
        system=(
            "Your task is to generate a list of search terms for a given query. "
            "For example if the query is: \"Give me latest news on Ohio\" you will then write down "
            "in the following format: [(Events in Ohio), (Ohio current situation)]. Follow the format, you must put each of "
            "the search term between parenthesis."
        ),
        user=f"The query is {search}, based on this query, write down 3 sentence/search term to look up. Use the given example as format.",
        db = db
    )
   
    # Extract search terms using regex
    pattern = r'\((.*?)\)'
    queries = re.findall(pattern, search_queries)
   
    # If no parentheses found, fallback to the original search
    if not queries:
        queries = [search]
   
    # Perform searches using Bebek class with polite delays
    all_results = []
    for i, query in enumerate(queries):
        if i > 0:
            await asyncio.sleep(1.5)  # Wait 1.5 seconds between searches
            
        bebek = Bebek(query,db)
        try:
            print(f"Searching for: '{query}'...")
            
            results = await bebek.get_top_search_result(max_results=5)
            if results:
                all_results.extend(results)
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            await asyncio.sleep(0.5)
            continue
   
    # Fetch full body text for each result
    formatted_results = []
    for result in all_results:
        if isinstance(result, dict) and 'title' in result and 'href' in result:
            title = result.get('title', 'No title')
            url = result.get('href', '#')
            
            # Try fetching the full body
            body = await fetch_body(url)
            if not body:
                # fallback to snippet
                body = result.get('body', 'No preview available.')
            
            # Truncate long body (optional)
            short_preview = (body[:3800] + "...") if len(body) > 3800 else body
            
            formatted_results.append(
                f"**{title}**\n\n{short_preview}\n\n[Read more]({url})\n"
            )
   
    final = "\n".join(formatted_results) if formatted_results else "No results found."
    return f"Web Search Result:\n{final}"

async def image_research(prompt: str, db,images_per_query: int = 50, safesearch: str = 'off') -> List[str]:
    try:
        # Generate a single image search query using LLM
        image_query = await generate_blank(
            system="Your task is to generate ONE search query from a specific prompt. For example, if the prompt is: \"Fetch me images of fish\" you will write: (fish) and nothing else. Use parentheses around the term.",
            user=f"The prompt is: {prompt}. Based on this prompt, write down ONE image search term to look up. Follow the format.",
            db = db
        )

        # Extract the search term from parentheses
        match = re.search(r'\((.*?)\)', image_query)
        query = match.group(1) if match else prompt

        print(f"Searching images for: '{query}'...")

        bebek = Bebek(query,db)
        image_results = await bebek.get_image_link(
            safesearch=safesearch,
            max_results=images_per_query,
        )

        # Extract image URLs from result dictionaries
        image_urls = [res['image'] for res in image_results if isinstance(res, dict) and 'image' in res]

        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in image_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)

        return unique_urls

    except Exception as e:
        print(f"Error in image_research: {e}")
        traceback.print_exc()
        return []