from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.controller.discordo import get_history
from src.controller.filemanager import get_json_file
import discord
import json
import os
import re


class PromptEngineer:
    def __init__(self, bot:AICharacter, message: discord.Message, dimension:Dimension, llm_setting = "text-default.json"):
        self.bot = bot
        self.message = message
        self.dimension = dimension
        self.api:dict = self.set_api(llm_setting)
        self.stopping_string = []

    async def create_text_prompt(self) -> str:
        jb = self.bot.instructions
        character = await self.bot.get_character_prompt()
        #jb = "" # Toggle this to disable JB
        globalvar = self.dimension.getDict().get("global", "")
        locationvar = self.dimension.getDict().get("location", "")
        instructionvar = self.dimension.getDict().get("instruction", "")
        history = await get_history(self.message)
        # content = re.sub(r'<@!?[0-9]+>', '', self.message.content.strip())
        user = re.sub(r'[^\w]', '', self.discordo.get_user_message_author_name().strip())
        # last_message = f"[Reply]{user}: {content}[End]"
        # # history = history.replace(last_message,"")
        prompt = character+globalvar +history +locationvar +instructionvar + jb+f"\n[Replying to {user}] " + self.bot.name + ":"

        stopping_strings = ["[System", "(System", user + ":",  "[Reply", "(Reply", "System Note", "[End","[/"] 
        
        stopping_strings = set(stopping_strings)
        stopping_strings = list(stopping_strings)
        data:dict = self.api
        data = data["parameters"]
        
        data.update({"prompt": prompt})
        data.update({"stop_sequence": stopping_strings})
        data.update({"grammar": ""})
        data.update({"grammar_string": ""})
        data.update({"grammars": ""})
        data_string = json.dumps(data)
        data.update({"images": []})
        self.stopping_string = stopping_strings
        return data_string
    
    def set_api(self,config_file: str) -> dict:
        # Go grab the configuration file for me
        file = os.path.join("configurations", config_file)
        contents = get_json_file(file)
        # If contents aren't none, clear the API and shove new data in
        api = {}

        if contents:
            api.update(contents)

        # Return the API
        return api 
