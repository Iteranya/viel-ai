# plugins/tarot.py
from typing import Any, Dict

from api.db.database import Database
from src.plugins.base import BasePlugin, ActiveCharacter, ActiveChannel
from src.utils.tarot import generate_tarot_reading # Assuming this exists

class TarotPlugin(BasePlugin):
    triggers = ["<tarot>"]

    async def execute(self, message, character: ActiveCharacter, channel: ActiveChannel, db:Database) -> Dict[str, Any]:
        reading = generate_tarot_reading(message.content)
        return {"reading": reading}

