# plugins/battle.py
import random
from typing import Any, Dict

from api.db.database import Database
from src.plugins.base import BasePlugin, ActiveCharacter, ActiveChannel

class BattlePlugin(BasePlugin):
    triggers = ["<battle_rp>"]

    async def execute(self, message, character: ActiveCharacter, channel: ActiveChannel, db: Database) -> Dict[str, Any]:
        attack_roll = self._roll("attack", character.name)
        defend_roll = self._roll("defend", character.name)
        return {
            "attack_roll": f"[System Note: Attack Roll: {attack_roll}]",
            "defend_roll": f"[System Note: Defend Roll: {defend_roll}]"
        }

    def _roll(self, action_type: str, bot_name: str) -> str:
        # The roll_attack and roll_defend logic would go here.
        # For brevity, I'll simplify it.
        roll = random.randint(1, 20)
        return f"{bot_name} rolled a {roll}/20 for their {action_type} action."