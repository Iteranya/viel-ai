# src/plugins/manager.py
import pkgutil
import importlib
import inspect
import sys
import os
import traceback
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
        Robust reloading that handles class identity mismatches.
        """
        print(f"\n--- RELOADING PLUGINS ---")
        self.plugins = []
        found_plugins = []

        try:
            package = importlib.import_module(self.plugin_package)
            package_path = package.__path__
        except ImportError:
            print(f"Error: Could not import {self.plugin_package}")
            return

        for _, name, _ in pkgutil.iter_modules(package_path):
            try:
                full_module_name = f"{self.plugin_package}.{name}"
                
                # 1. Import or Reload the module
                if full_module_name in sys.modules:
                    module = importlib.import_module(full_module_name)
                    module = importlib.reload(module)
                else:
                    module = importlib.import_module(full_module_name)

                # 2. Scan for Plugin Classes
                for member_name, member_obj in inspect.getmembers(module):
                    if inspect.isclass(member_obj):
                        # --- THE FIX: NAME-BASED CHECK ---
                        # We check if 'BasePlugin' is in the inheritance tree (MRO) by name.
                        # This ignores the "Version 1 vs Version 2" memory issue.
                        base_names = [b.__name__ for b in inspect.getmro(member_obj)]
                        
                        if (
                            "BasePlugin" in base_names 
                            and member_name != "BasePlugin"
                            and member_obj.__module__ == full_module_name # Ensure it's defined in THIS file
                        ):
                            try:
                                print(f"  -> Loading {member_name} from {name}.py")
                                plugin_instance = member_obj()
                                self.plugins.append(plugin_instance)
                                found_plugins.append(member_name)
                            except Exception as e:
                                print(f"!!!! Error initializing {member_name}: {e}")
                                import traceback
                                traceback.print_exc()

            except Exception as e:
                print(f"!!!! Failed to load file {name}.py: {e}")
                import traceback
                traceback.print_exc()

        print(f"--- Loaded: {', '.join(found_plugins)} ---\n")

    async def scan_and_execute(self, message, character:ActiveCharacter, channel:ActiveChannel, db) -> Dict[str, Any]:
        plugin_outputs = {}

        look_for_plugins_in = "".join(filter(None, [
            message.content,
            character.persona,
            character.instructions,
            channel.global_note,
            channel.instruction
        ]))

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