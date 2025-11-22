# plugins/battle.py
import random
from typing import Any, Dict

from api.db.database import Database
from .base import BasePlugin, ActiveCharacter, ActiveChannel

class DiceRollPlugin(BasePlugin):
    triggers = ["<dice_roll>"]

    async def execute(self, message, character: ActiveCharacter, channel: ActiveChannel, db: Database) -> Dict[str, Any]:
        roll = self._roll("attack", character.name)
        return {
            "dice_roll": f"[System Note: Attack Roll: {roll}]"
        }

    def _roll(self, bot_name: str) -> str:
        # The roll_attack and roll_defend logic would go here.
        # For brevity, I'll simplify it.
        roll = random.randint(1, 20)
        return f"{bot_name} rolled a {roll}/20"