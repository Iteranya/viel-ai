# api/bot_state.py
from typing import Optional, TYPE_CHECKING
import threading

# Use TYPE_CHECKING to avoid circular imports, just like before.

class BotState:
    """A simple class to hold the shared state of the bot instance."""
    def __init__(self):
        self.bot_instance = None
        self.bot_thread: Optional[threading.Thread] = None

# Create a single, global instance of this state object that will be imported everywhere.
bot_state = BotState()