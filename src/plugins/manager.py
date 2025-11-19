# plugins/manager.py
import discord
from typing import Dict, Any, List

from src.plugins.base import BasePlugin
from src.plugins.tarot import TarotPlugin
from src.plugins.search import SearchPlugin

class PluginManager:
    def __init__(self):
        # Register all available plugins here
        self.plugins: List[BasePlugin] = [
            TarotPlugin(),
            SearchPlugin(),
        ]

    async def scan_and_execute(self, message: discord.Message, character, channel,db) -> Dict[str, Any]:
        """
        Scans the message for plugin triggers and executes them.
        Returns a dictionary of all plugin results.
        """
        plugin_outputs = {}
        message_content_lower = message.content.lower()

        for plugin in self.plugins:
            # Check if any of the plugin's triggers are in the message
            if any(trigger in message_content_lower for trigger in plugin.triggers):
                # Use the first trigger's name (without symbols) as the key
                plugin_key = plugin.triggers[0].strip("<>").replace(">", "")
                plugin_outputs[plugin_key] = await plugin.execute(message, character, channel,db)

        return plugin_outputs