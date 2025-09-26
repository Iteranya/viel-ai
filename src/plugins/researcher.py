
from src.utils.llm_new import generate_blank
import re
import asyncio
from src.utils.duckduckgo import Bebek
from src.controller.plugin_registry import plugin

@plugin
async def research(search):
    """
    Performs a multi-query web research based on an initial search prompt using LLM-generated search variations.

    This function:
      1. Uses a language model to generate related search terms.
      2. Extracts the search terms using regex (expecting parentheses-wrapped phrases).
      3. Performs searches for each term using the `Bebek` search client.
      4. Formats and returns a nicely structured markdown response of top results.
      5. DOES NOT RETURN A LIST, RETURNS A STRING

    Parameters:
        search (str): The initial search query from the user.

    Returns:
        str: A markdown-formatted string of summarized search results. If no results are found, returns a default message.

    Behavior:
        - The LLM is prompted to return a list of 5 search queries in this exact format:
          `[(term1), (term2), (term3), (term4), (term5)]`.
        - Each search is spaced out with polite delays to avoid hammering the search backend.
        - Errors are caught and logged with a brief delay before continuing to the next query.
        - Each valid result includes a title, a short body preview, and a "Read more" link.
        - The results are written out in a single string in neat markdown.

    Example:
        result = await research("Latest trends in AI education")
        print(result)
        # Output includes search results for AI education trends, news, research, and more.
    """
    # Generate search queries using LLM
    search_queries = await generate_blank(
        system=(
            "Your task is to generate a list of search terms for a given query. For example if the query is: "
            "\"Give me latest news on Ohio\" you will then write down in the following format: "
            "[(Latest news Ohio), (Events in Ohio), (Ohio News), (Ohio gossips), (Ohio current situation)]. "
            "Follow the format, you must put each of the search term between parenthesis."
        ),
        user=f"The query is {search}, based on this query, write down 5 sentence/search term to look up. Use the given example as format.",
        assistant="Understood, here are the search query."
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
            await asyncio.sleep(1.5)  # Give the servers some breathing room

        bebek = Bebek(query)
        try:
            print(f"Searching for: '{query}'...")

            # Get top 5 search results
            if "news" in search:
                results = await bebek.get_news()
            else:
                results = await bebek.get_top_search_result(max_results=5)
            if results:
                all_results.extend(results)

            await asyncio.sleep(0.5)  # Chill a bit after success

        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            await asyncio.sleep(0.5)
            continue

    # Format results all fancy-like
    formatted_results = []
    for result in all_results:
        if isinstance(result, dict) and 'title' in result and 'href' in result:
            title = result.get('title', 'No title')
            url = result.get('href', '#')
            body = result.get('body', '')[:200] + "..." if result.get('body') else ''
            formatted_results.append(f"**{title}**\n{body}\n[Read more]({url})\n")

    # Return the final markdown-formatted output
    final = "\n".join(formatted_results) if formatted_results else "No results found."
    return f"Web Search Result:\n{final}"

