import aiohttp
from bs4 import BeautifulSoup
import re

async def fetch_body(url: str) -> str | None:
    """Fetch and clean the meaningful text content from a webpage asynchronously.
       Returns None if the fetch or parsing fails."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
    except Exception:
        return None  # failed request

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Remove junk elements
        for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside"]):
            tag.decompose()

        # Grab only the main body text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = re.sub(r"\n\s*\n+", "\n\n", text)  # collapse multiple blank lines
        text = re.sub(r"[ \t]+", " ", text)       # collapse spaces/tabs
        print (text)
        return text if text.strip() else None
    except Exception:
        return None
