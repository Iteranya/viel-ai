from abc import ABC, abstractmethod
from typing import List, Dict, Any
import discord

# Forward-declare the classes to avoid circular imports
class ActiveCharacter: pass
class ActiveChannel: pass

class BasePlugin(ABC):
    """Abstract base class for all plugins."""
    triggers: List[str] = []

    @abstractmethod
    async def execute(self, message: discord.Message, character: ActiveCharacter, channel: ActiveChannel) -> Dict[str, Any]:
        """
        Executes the plugin's logic and returns a dictionary of results.
        This dictionary will be accessible in the Jinja2 template.
        """
        pass