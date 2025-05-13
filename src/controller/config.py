import os
import discord
from dotenv import load_dotenv
import asyncio
from dataclasses import dataclass, asdict
import json
from src.data.const import CONFIG_PATH

load_dotenv()
queue_to_process_everything = asyncio.Queue()

default_character = "Viel"
bot_user = None


@dataclass
class Config:
    default_character: str = "Viel"
    ai_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    base_llm: str = "gemini-2.5-pro-exp-03-25"
    temperature: float = 0.5
    ai_key: str = ""
    discord_key: str = ""