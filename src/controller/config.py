import os
import discord
from dotenv import load_dotenv
import asyncio
from dataclasses import dataclass, asdict
import json

load_dotenv()
queue_to_process_everything = asyncio.Queue()

default_character = "Vida-chan"
bot_user = None

CONFIG_PATH = "configurations/bot_config.json"

@dataclass
class Config:
    default_character = "Vida-chan"
    ai_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    base_llm:str= "gemini-2.5-pro-exp-03-25"
    temperature:float = 0.5
    ai_key:str = ""
    discord_key:str = ""

# System Setup

def load_or_create_config(path: str = CONFIG_PATH) -> Config:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = Config(**data)
            current_config.ai_key = "" # Duct Tape Security... Fix In Production (Or Not, Maybe This Is Actually Secure Enough :v)
        return current_config
    else:
        default_config = Config()
        save_config(default_config, path)
        print(f"No config found. Created default at {path}.")
        default_config.ai_key = ""
        return default_config

def get_key(path:str = CONFIG_PATH) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = Config(**data)
            return current_config.ai_key 
    else:
        return ""
    
def save_config(config: Config, path: str = CONFIG_PATH) -> None:
    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)