from typing import Any, Dict

from api.db.database import Database
from src.plugins.base import BasePlugin, ActiveCharacter, ActiveChannel
from src.utils.duckduckgo import research # Assuming this exists

class SearchPlugin(BasePlugin):
    triggers = ["search>"]

    async def execute(self, message, character: ActiveCharacter, channel: ActiveChannel, db:Database,messenger) -> Dict[str, Any]:
        search_query = message.content.replace("search>", "").strip()
        search_result = await research(search_query,db)
        return {"result": f"[System Note: The user requested a search. Here are the results for '{search_query}':\n{search_result}]"}