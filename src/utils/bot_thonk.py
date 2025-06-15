import importlib
import inspect
import pkgutil
import textwrap
import src
from src.controller.plugin_registry import PLUGINS
import ast

import src.plugins
# Auto-import all plugin modules to trigger @plugin decorators
for _, module_name, _ in pkgutil.iter_modules(src.plugins.__path__):
    importlib.import_module(f"src.plugins.{module_name}")

def extract_plugin_docs_as_string() -> str:
    """
    Returns a single formatted string of all plugin docstrings, ready for prompt injection.
    """
    formatted = []
    for name, func in PLUGINS.items():
        doc = inspect.getdoc(func) or "No documentation available."
        formatted.append(f"### {name}()\n{doc}\n")
    return "\n".join(formatted)



import re
import textwrap

def extract_all_functions(text: str) -> str | None:
    match = re.search(r"```py\s*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None

def create_script_environment(user_code: str):
    """
    Injects registered plugins into a safe script namespace and returns the create_reply coroutine.
    """
    namespace = {
        **PLUGINS,                    # All registered plugins
        "re": __import__("re"),
        "urllib": __import__("urllib"),
        "asyncio": __import__("asyncio"),
        "math": __import__("math"),
        "time": __import__("time"),
        "datetime": __import__("datetime"),
        "statistics": __import__("statistics"),
    }

    exec(user_code, namespace)

    create_reply = namespace.get("create_reply")
    if not create_reply:
        raise ValueError("Your script must define an async `create_reply()` function.")
    
    return create_reply