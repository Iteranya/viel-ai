import asyncio
from src.controller.config import queue_to_process_everything
import discord
import os
import sys
import traceback
from src.models.aicharacter import AICharacter
from src.models.dimension import Dimension
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from src.controller.discordo import send
from src.utils.image_gen import generate_sd_prompt
from src.utils.pollination import fetch_image
from src.utils.hidream import invoke_chute
from src.utils.duckduckgo import research,image_research

def format_traceback(error: Exception, *, _print: bool = False) -> str:
    # https://github.com/InterStella0/stella_bot/blob/896c94e847829575d4699c0dd9d9b925d01c4b44/utils/useful.py#L132~L140
    if _print:
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    etype = type(error)
    trace = error.__traceback__
    lines = traceback.format_exception(etype, error, trace)
    return "".join(lines)

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
        try:
            if message_content.startswith("//"):
                pass
            elif message_content.startswith("img_search>"):
                search_query = message.content.replace("img_search>","")
                search_query = search_query.lower()
                search_query = search_query.replace(bot.bot_name.lower(),"") # Wait, why is it not working???
                print(search_query)
                search_result = await image_research(search_query,50,'on')
                await send_llm_message(bot,message,dimension,plugin = search_result)
            elif message_content.startswith("nsfw_search>"):
                search_query = message.content.replace("nsfw_search>","")
                search_query = search_query.lower()
                search_query = search_query.replace(bot.bot_name.lower(),"") # Wait, why is it not working???
                print(search_query)
                search_result = await image_research(search_query,50,'off')
                await send_llm_message(bot,message,dimension,plugin = search_result)
            elif message_content.startswith("search>"):
                search_query = message.content.replace("search>","")
                search_query = search_query.lower()
                search_query = search_query.replace(bot.bot_name.lower(),"") # Wait, why is it not working???
                print(search_query)
                search_result = await research(search_query)
                await send_llm_message(bot,message,dimension,plugin = search_result)
            elif message_content.startswith("enpic>"):
                image_prompt = await generate_sd_prompt(message)
                await invoke_chute(image_prompt) # Use Chutes
                await send_llm_message(bot,message,dimension)
            elif message_content.startswith("hipic>"):
                image_prompt = message.content.replace("pic>","")
                image_prompt = image_prompt.replace(bot.bot_name,"")
                await invoke_chute(image_prompt) # Use Chutes
                await send_llm_message(bot,message,dimension)
            elif message_content.startswith("pic>"):
                image_prompt = message.content.replace("pic>","")
                image_prompt = image_prompt.replace(bot.bot_name,"")
                await fetch_image(image_prompt,"temp.jpg",**params) # Use Pollination
                await send_llm_message(bot,message,dimension)
            else:
                await send_llm_message(bot,message,dimension, plugin="") # Prepping up to make plugins easier to handle, maybe
        except Exception as e:
            print(f"Something went wrong: {format_traceback(e)}")
            try:
                await message.add_reaction('❌')
            except Exception as e:
                print("Hi!")
        queue_to_process_everything.task_done()

async def send_llm_message(bot: AICharacter,message:discord.message.Message,dimension:Dimension, plugin = None):
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
    elif isinstance(plugin,str):
        queueItem = QueueItem(
            prompt=await prompter.create_text_prompt(),
            bot = bot.name,
            user = message.author.display_name,
            stop=prompter.stopping_string,
            prefill=prompter.prefill,
            dm=dm,
            message=prompter.message,
            plugin=plugin
            )
    elif isinstance(plugin,list):
        queueItem = QueueItem(
            prompt=await prompter.create_text_prompt(),
            bot = bot.name,
            user = message.author.display_name,
            stop=prompter.stopping_string,
            prefill=prompter.prefill,
            dm=dm,
            message=prompter.message,
            images=plugin
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
