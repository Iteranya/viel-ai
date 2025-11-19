from abc import ABC, abstractmethod
from typing import List, Dict, Any
import discord

from api.db.database import Database

# Forward-declare the classes to avoid circular imports
class ActiveCharacter: pass
class ActiveChannel: pass
class Database: pass

class BasePlugin(ABC):
    """Abstract base class for all plugins."""
    triggers: List[str] = []

    @abstractmethod
    async def execute(self, message: discord.Message, character: ActiveCharacter, channel: ActiveChannel, db:Database) -> Dict[str, Any]:
        """
        Executes the plugin's logic and returns a dictionary of results.
        This dictionary will be accessible in the Jinja2 template.
        """
        pass