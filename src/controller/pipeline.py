# src/controller/think.py

import asyncio
import traceback
import discord
from src.controller.messenger import DiscordMessenger
from src.models.aicharacter import ActiveCharacter
from src.models.dimension import ActiveChannel
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from api.models.models import BotConfig
from api.db.database import Database

# --- NEW WORKER FUNCTION ---
# This contains the logic that used to be inside the while loop
async def process_message(viel, db: Database, message: discord.Message, messenger: DiscordMessenger, queue: asyncio.Queue):
    try:
        bot_config = BotConfig(**db.list_configs())

        # --- 1. Check Permission & Load Channel ---
        is_dm = isinstance(message.channel, discord.DMChannel)
        
        if is_dm:
            allowed_users = bot_config.dm_list or []
            if message.author.name not in allowed_users:
                print(f"Denied DM access to {message.author.name}")
                await message.channel.send("🚫 You do not have permission to talk to this bot in DM.")
                return # Exit worker

            channel = ActiveChannel.from_dm(message.channel, message.author, db)
        else:
            channel = ActiveChannel.from_id(str(message.channel.id), db)

        if not channel:
            return # Exit worker

        # --- 2. Determine Active Character ---
        message_content_with_context = message.content
        character = ActiveCharacter.from_message(message_content_with_context, db)
        
        # Handle Mentions/Defaults
        if not character and (is_dm or (message.guild and message.guild.me in message.mentions)):
            default_char_name = bot_config.default_character
            if default_char_name:
                char_data = db.get_character(default_char_name)
                if char_data:
                    character = ActiveCharacter(char_data, db)

        if character.name.lower() == message.author.display_name.lower():
            return

        if not character:
            return # Exit worker

        # --- 3. Generate Response ---
        await message.add_reaction('✨')
        
        prompter = PromptEngineer(character, message, channel)
        prompt = await prompter.create_prompt()

        queue_item = QueueItem(
            prompt=prompt,
            bot=character.name,
            user=message.author.display_name,
            stop=prompter.stopping_strings,
            message=message
        )
        
        print(f"Processing chat for {character.name} in {channel.name}...")
        
        # This is the slow part that we want to run in parallel!
        queue_item = await generate_response(queue_item, db)

        if not queue_item.result:
            queue_item.result = "//[OOC: The AI failed to generate a response.]"

        # --- 4. Clean Up The Response ---

        clean_up(queue_item)
        
        await messenger.send_message(character, message, queue_item)

        try:
            await message.remove_reaction('✨', viel.user)
        except Exception:
            pass

    except Exception as e:
        print(f"Error processing message: {e}\n{traceback.format_exc()}")
        try:
            await message.add_reaction('❌')
        except:
            pass
    
    finally:
        # CRITICAL: Mark the queue item as done, regardless of success or error
        queue.task_done()

# --- UPDATED MANAGER FUNCTION ---
async def think(viel, db: Database, queue: asyncio.Queue) -> None:
    messenger = DiscordMessenger(viel)
    
    # Keep track of running tasks
    background_tasks = set()

    print("🧠 AI Core started. Waiting for messages...")

    while True:
        # 1. Clean up finished tasks
        # (removes tasks that have finished execution from our set)
        background_tasks = {t for t in background_tasks if not t.done()}

        # 2. Get dynamic config
        # We fetch this every loop so if you change DB to '10', it updates instantly.
        try:
            bot_config = BotConfig(**db.list_configs())
            concurrency_limit = bot_config.concurrency
            if concurrency_limit < 1: 
                concurrency_limit = 1
        except Exception:
            concurrency_limit = 1

        # 3. Check Concurrency Limit
        # If we have met or exceeded the limit, wait for at least one task to finish
        if len(background_tasks) >= concurrency_limit:
            # This pauses the loop here until a spot opens up
            await asyncio.wait(background_tasks, return_when=asyncio.FIRST_COMPLETED)
            continue 

        # 4. Get Message
        # This waits for a message from observer.py
        message: discord.Message = await queue.get()

        # 5. Spawn Worker
        # Instead of processing here, we create a background task
        task = asyncio.create_task(
            process_message(viel, db, message, messenger, queue)
        )
        
        # Add to set to prevent Python garbage collection from killing it early
        background_tasks.add(task)

def clean_up(queue_item: QueueItem) -> QueueItem:
    """
    Removes LLM artifacts/stop strings from the generated result.
    Modifies the QueueItem in place.
    """
    if not queue_item.result:
        return queue_item

    # List of artifacts to scrub from the text
    artifacts = ["[End]", "[Reply]"]

    for artifact in artifacts:
        # We use replace to remove the substring
        queue_item.result = queue_item.result.replace(artifact, "")

    # Strip removes leading/trailing whitespace (newlines, spaces)
    # that might be left over after removing the tags.
    queue_item.result = queue_item.result.strip()

    return queue_item