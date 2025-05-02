import re
from src.controller.config import queue_to_process_everything
import discord
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from src.controller.discordo import send

# GOD Refactoring this gonna be a bitch and a half...


async def think() -> None:

    while True:
        content = await queue_to_process_everything.get()
        message:discord.Message = content["message"]
        bot:AICharacter = content["bot"]
        dimension:Dimension = content["dimension"]

        try:
            await message.add_reaction('✨')
        except Exception as e:
            print("Hi!")
        
        message_content = message.content
        
        if message_content.startswith("//"):
            pass
        else:
            await send_llm_message(bot,message,dimension, plugin="") # Prepping up to make plugins easier to handle, maybe
        queue_to_process_everything.task_done()

async def send_llm_message(bot: AICharacter,message:discord.Message,dimension:Dimension):
    prompter = PromptEngineer(bot,message,dimension)
    queueItem = QueueItem(
        prompt=await prompter.create_text_prompt(),
        bot = bot.name,
        user = message.author.display_name,
        stop=prompter.stopping_string,
        prefill=prompter.prefill
        )
    print("Chat Completion Processing...")
    queueItem = await generate_response(queueItem)
    await send(bot,queueItem)
    return
