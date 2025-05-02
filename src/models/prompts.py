from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.controller.discordo import get_history
from src.controller.filemanager import get_json_file
import discord
import json
import os
import re


class PromptEngineer:
    def __init__(self, bot:AICharacter, message: discord.Message, dimension:Dimension):
        self.bot = bot
        self.user = message.author.name
        self.message = message
        self.dimension = dimension
        self.stopping_string = None
        self.prefill = None

    async def create_text_prompt(self) -> str:
        jb = self.bot.instructions
        character = await self.bot.get_character_prompt()
        #jb = "" # Toggle this to disable JB
        globalvar = self.dimension.getDict().get("global", "")
        locationvar = self.dimension.getDict().get("location", "")
        instructionvar = self.dimension.getDict().get("instruction", "")
        history = await get_history(self.message)
        prompt = character+globalvar +history +locationvar +instructionvar + jb
        self.prefill = f"\n[Replying to {self.user}] " + self.bot.name + ":"
        self.stopping_string = ["[System", "(System", self.user + ":",  "[Reply", "(Reply", "System Note", "[End","[/"] 
        return prompt
