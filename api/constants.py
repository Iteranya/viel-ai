# constants.py
"""Constants and configuration values for the application."""

import os

# Constants for file paths
CHARACTERS_DIR = "res/characters"
SERVERS_DIR = "res/servers"
CONFIG_FILE = "configurations/bot_config.json"

# Ensure directories exist
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(SERVERS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)