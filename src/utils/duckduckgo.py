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
   
    # Perform searches using Bebek class with polite delays
    all_results = []
    for i, query in enumerate(queries):
        # Add delay between searches (except for the first one)
        if i > 0:
            await asyncio.sleep(1.5)  # Wait 1.5 seconds between searches
            
        bebek = Bebek(query)
        try:
            print(f"Searching for: '{query}'...")  # Optional: show progress
            
            # Get search results for each query
            results = await bebek.get_top_search_result(max_results=5)
            if results:
                all_results.extend(results)
                
            # Small delay after each successful search
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            # Even on error, be polite and wait a bit before continuing
            await asyncio.sleep(0.5)
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

async def image_research(prompt: str, images_per_query: int = 3, safesearch: str = 'off') -> List[str]:
    """
    Generate image search queries from a prompt and return a list of image URLs
    
    Args:
        prompt: The input prompt to generate image search queries from
        images_per_query: Number of images to fetch per search query (default: 3)
        safesearch: Safesearch setting ('on', 'moderate', 'off') (default: 'off')
        
    Returns:
        List of image URL strings
    """
    try:
        # Generate image search queries using LLM
        image_queries = await generate_blank(
            system=f"Your task is to generate a list of image search terms for a given prompt. Create specific, visual search queries that would find relevant images. For example if the prompt is: \"Show me beautiful landscapes\" you will write: [(Mountain landscapes), (Ocean scenery), (Forest views), (Desert photography), (Sunset landscapes)]. Follow the format, you must put each search term between parenthesis.",
            user=f"The prompt is: {prompt}. Based on this prompt, write down 5 image search terms to look up. Use the given example as format.",
            assistant=f"Understood, here are the image search queries."
        )
        
        # Extract search terms using regex
        pattern = r'\((.*?)\)'
        queries = re.findall(pattern, image_queries)
        
        # If no parentheses found, fallback to the original prompt
        if not queries:
            queries = [prompt]
        
        # Collect all image URLs
        all_image_urls = []
        
        for i, query in enumerate(queries):
            # Add delay between searches (except for the first one)
            if i > 0:
                await asyncio.sleep(1.5)  # Wait 1.5 seconds between searches
                
            bebek = Bebek(query)
            try:
                print(f"Searching images for: '{query}'...")  # Optional: show progress
                
                # Get image results for each query
                image_results = await bebek.get_image_link(
                    safesearch=safesearch, 
                    max_results=images_per_query
                )
                
                if image_results:
                    # Extract image URLs from the result dictionaries
                    for result in image_results:
                        if isinstance(result, dict) and 'image' in result:
                            all_image_urls.append(result['image'])
                    
                # Small delay after each successful search
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error searching images for '{query}': {e}")
                # Even on error, be polite and wait a bit before continuing
                await asyncio.sleep(0.5)
                continue
        
        # Remove duplicates while preserving order (now working with strings)
        unique_urls = []
        seen = set()
        for url in all_image_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        return unique_urls
        
    except Exception as e:
        print(f"Error in image_research: {e}")
        traceback.print_exc()
        return []