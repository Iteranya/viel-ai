import asyncio
from src.controller.config import queue_to_process_everything
import discord
import os
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from src.controller.discordo import send
from src.utils.image_gen import generate_sd_prompt
from src.utils.pollination import fetch_image
from src.utils.hidream import invoke_chute

# GOD Refactoring this gonna be a bitch and a half...

params = {
    "model": "turbo",
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
        try:
            delete_file("temp.jpg") # Hacky Solution, I know
        except Exception as e:
            print("All Clean, Moving on")
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
            await invoke_chute(image_prompt)
            await send_llm_message(bot,message,dimension,plugin = "temp.jpg")
        elif message_content.startswith("hipic>"):
            image_prompt = message.content.replace("pic>","")
            image_prompt = image_prompt.replace(bot.bot_name,"")
            await invoke_chute(image_prompt)
            await send_llm_message(bot,message,dimension,plugin = "temp.jpg")
        elif message_content.startswith("pic>"):
            image_prompt = message.content.replace("pic>","")
            image_prompt = image_prompt.replace(bot.bot_name,"")
            await invoke_chute(image_prompt,"temp.jpg",**params)
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
    if os.path.exists('temp.jpg'):
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
    if not queueItem.images:
        queueItem = await generate_response(queueItem)
    else:
        queueItem.result = f"[System Note: Attached is the generated image by {queueItem.bot}]"
    if not queueItem.result:
        queueItem.result = "//Something Went Wrong, AI Failed to Generate"
    await send(bot,message,queueItem)
    try:
        delete_file(queueItem.images[0]) # Hacky Solution, I know
    except Exception as e:
        print("All Clean, Moving on")
    return

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File {file_path} deleted successfully")
    except FileNotFoundError:
        print(f"File {file_path} not found")
    except PermissionError:
        print(f"Permission denied to delete {file_path}")
    except Exception as e:
        print(f"Error occurred while deleting file: {e}")
