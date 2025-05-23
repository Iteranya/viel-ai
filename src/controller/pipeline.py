import asyncio
from src.controller.config import queue_to_process_everything
import discord
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from src.controller.discordo import send
from src.utils.image_gen import generate_sd_prompt
from src.utils.pollination import fetch_image

# GOD Refactoring this gonna be a bitch and a half...

params = {
    "model": "flux",
    "seed": 123,
    "width": 720,
    "height": 1280,
    "nologo": "true",
    "private": "true",
    "enhance": "false",
    "safe": "false",
    "referrer": "ImageGenTest"
}
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

        message_content = str(message.content)

        if message_content.startswith("//"):
            pass
        elif message_content.startswith("enpic>"):
            image_prompt = await generate_sd_prompt(message)
            await fetch_image(image_prompt,"temp.jpg",**params)
            await send_llm_message(bot,message,dimension,plugin = "temp.jpg")
        elif message_content.startswith("pic>"):
            image_prompt = message.content.replace("pic>","")
            image_prompt = image_prompt.replace(bot.bot_name,"")
            await fetch_image(image_prompt,"temp.jpg",**params)
            await send_llm_message(bot,message,dimension,plugin = "temp.jpg")
        else:
            await send_llm_message(bot,message,dimension, plugin="") # Prepping up to make plugins easier to handle, maybe
        queue_to_process_everything.task_done()

async def send_llm_message(bot: AICharacter,message:discord.message.Message,dimension:Dimension, plugin):
    # print("The following is the content of message: \n\n" +str(message.author.display_name))
    dm=False
    # Can we add a 1 second delay here?
    await asyncio.sleep(1)
    prompter = PromptEngineer(bot,message,dimension)
    if isinstance(message.channel,discord.channel.DMChannel):
        dm = True
    queueItem = None
    if plugin == "temp.jpg":
        queueItem = QueueItem(
            prompt=await prompter.create_text_prompt(),
            bot = bot.name,
            user = message.author.display_name,
            stop=prompter.stopping_string,
            prefill=prompter.prefill,
            dm=dm,
            message=prompter.message,
            images=["temp.jpg"]
            )
    else:
        queueItem = QueueItem(
            prompt=await prompter.create_text_prompt(),
            bot = bot.name,
            user = message.author.display_name,
            stop=prompter.stopping_string,
            prefill=prompter.prefill,
            dm=dm,
            message=prompter.message
            )
    print("Chat Completion Processing...")
    queueItem = await generate_response(queueItem)
    if not queueItem.result:
        queueItem.result = "//Something Went Wrong, AI Failed to Generate"
    await send(bot,message,queueItem)
    return
