from datetime import datetime
from typing import Any, Dict

from api.db.database import Database
from .base import BasePlugin, ActiveCharacter, ActiveChannel

class TimePlugin(BasePlugin):
    triggers = ["<tell_time>"]

    async def execute(self, message, character: ActiveCharacter, channel: ActiveChannel, db: Database) -> Dict[str, Any]:
        now_str = self._get_time()
        return {
            "tell_time": f"[System Note: Current Time: {now_str}]"
        }

    def _get_time(self) -> str:
        # Format it however you like—this one’s human-friendly
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M")