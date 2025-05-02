import os
import discord
from dotenv import load_dotenv
import asyncio


load_dotenv()
global text_api
global image_api
global character_card

global immersive_mode
global blacklist_mode
global openrouter_token
global safesearch
global text_evaluator_model
global llm_type
global gemini_token

queue_to_process_everything = asyncio.Queue()

default_character = "Vida-chan"
bot_user = None

llm_type = "remote"

intents: discord.Intents = discord.Intents.all()
intents.message_content = True
client: discord.Client = discord.Client(command_prefix='/', intents=intents)

