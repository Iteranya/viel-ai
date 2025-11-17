import os
import discord
from dotenv import load_dotenv
import asyncio
from dataclasses import dataclass, asdict
import json

load_dotenv()
queue_to_process_everything = asyncio.Queue()