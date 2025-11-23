# src/plugins/manager.py
import pkgutil
import importlib
import inspect
import sys
import os
from typing import Dict, Any, List

# Update this import to match your structure
from src.models.aicharacter import ActiveCharacter
from src.models.dimension import ActiveChannel
from src.plugins.base import BasePlugin 

class PluginManager:
    def __init__(self, plugin_package_path: str = "src.plugins"):
        self.plugin_package = plugin_package_path
        self.plugins: List[BasePlugin] = []
        self.reload_plugins()

    def reload_plugins(self):
        """
        Dynamically discovers and loads plugins from the plugins directory.
        Force reloads modules to pick up code changes.
        """
        self.plugins = []
        found_plugins = []

        # 1. Resolve the directory of the package
        try:
            package = importlib.import_module(self.plugin_package)
            package_path = package.__path__
        except ImportError:
            print(f"Could not import package {self.plugin_package}")
            return

        # 2. Iterate over all files in the plugins folder
        for _, name, _ in pkgutil.iter_modules(package_path):
            try:
                full_module_name = f"{self.plugin_package}.{name}"
                
                # Import the module
                module = importlib.import_module(full_module_name)
                
                # --- THE FIX IS HERE ---
                # Force Python to re-read the file from disk
                importlib.reload(module) 
                # -----------------------

                # 3. Inspect the module for classes
                for member_name, member_obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(member_obj) 
                        and issubclass(member_obj, BasePlugin) 
                        and member_obj is not BasePlugin
                    ):
                        # Instantiate the class and add to list
                        plugin_instance = member_obj()
                        self.plugins.append(plugin_instance)
                        found_plugins.append(member_name)
            except Exception as e:
                print(f"Failed to load plugin module {name}: {e}")

        print(f"Loaded plugins: {', '.join(found_plugins)}")

    async def scan_and_execute(self, message, character:ActiveCharacter, channel:ActiveChannel, db) -> Dict[str, Any]:
        plugin_outputs = {}

        look_for_plugins_in =""

        look_for_plugins_in += message.content
        look_for_plugins_in += character.persona
        look_for_plugins_in += character.instructions
        look_for_plugins_in += channel.global_note
        look_for_plugins_in += channel.instruction

        for plugin in self.plugins:
            # Safe check for triggers
            if not plugin.triggers:
                continue
                
            if any(trigger in look_for_plugins_in for trigger in plugin.triggers):
                plugin_key = plugin.__class__.__name__
                try:
                    result = await plugin.execute(message, character, channel, db)
                    plugin_outputs[plugin_key] = result
                except Exception as e:
                    print(f"Error in plugin {plugin_key}: {e}")
                    plugin_outputs[plugin_key] = {"error": str(e)}

        return plugin_outputs