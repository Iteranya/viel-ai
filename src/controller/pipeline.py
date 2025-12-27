
# src/controller/think.py

import asyncio
import re
import traceback
import discord
from src.controller.messenger import DiscordMessenger
from src.models.aicharacter import ActiveCharacter
from src.models.dimension import ActiveChannel
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.plugins.manager import PluginManager
from src.utils.llm_new import generate_response
from api.models.models import BotConfig
from api.db.database import Database

# --- HELPER FUNCTIONS FOR MULTI-CHARACTER LOGIC ---

def find_all_triggered_characters(message: discord.Message, channel: ActiveChannel, db: Database) -> list[ActiveCharacter]:
    """
    Scans a message to find ALL whitelisted characters triggered by keywords.
    Instead of returning names, it returns a list of instantiated ActiveCharacter objects.
    """
    if not channel.whitelist:
        return []

    triggered_characters = []
    # Use a set to prevent adding the same character twice if multiple of their triggers match
    triggered_names = set() 
    message_lower = message.content.lower()

    for name in channel.whitelist:
        char_data = db.get_character(name)
        if not char_data or char_data['name'] in triggered_names:
            continue

        name_trigger = char_data.get("name", "").lower()
        raw_triggers = char_data.get("triggers") or []
        triggers = [t.lower() for t in raw_triggers]
        extended_triggers = triggers + ([name_trigger] if name_trigger else [])

        for trigger in extended_triggers:
            if not trigger:
                continue
            # Use whole-word matching for better accuracy
            if re.search(r'\b' + re.escape(trigger) + r'\b', message_lower):
                # We found a match, so create the character object and add it
                triggered_characters.append(ActiveCharacter(char_data, db))
                triggered_names.add(char_data['name'])
                break # Move to the next character in the whitelist

    return triggered_characters


def get_bot_config(db: Database) -> BotConfig:
    """Fetches all config key-values from the DB and returns a BotConfig object."""
    all_db_configs = db.list_configs()
    # Pydantic validates and provides default values for any missing keys
    return BotConfig(**all_db_configs)


async def _generate_and_send_for_character_streaming(
    character: ActiveCharacter, # Now we pass the full object
    viel, db: Database, 
    message: discord.Message, 
    channel: ActiveChannel,
    messenger: DiscordMessenger,
    plugin_manager: PluginManager
):
    """
    Contains the core logic for generating and sending a message for ONE character with streaming.
    """
    # Avoid character talking to themselves
    if character.name.lower() == message.author.display_name.lower():
        return

    print(f"Processing chat for {character.name} in {channel.name}...")
    
    prompter = PromptEngineer(character, message, channel, plugin_manager, messenger)
    prompt = await prompter.create_prompt()

    queue_item = QueueItem(
        prompt=prompt,
        bot=character.name,
        user=message.author.display_name,
        stop=prompter.stopping_strings,
        message=message
    )
    
    # For streaming, we'll handle this at the LLM level but provide progress updates
    try:
        # Send initial thinking message
        response_message = await message.channel.send(f"**{character.name}** is thinking...")
        
        # Get the bot config
        bot_config = get_bot_config(db)
        
        # Create the async OpenAI client
        client = AsyncOpenAI(
            base_url=bot_config.ai_endpoint,
            api_key=bot_config.ai_key,
        )
        
        # Prepare messages
        system_prompt = prompt
        user_message = clean_string(message.content)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Add prefill if needed
        if bot_config.use_prefill:
            prefill_content = f"[Reply] {character.name}:"
            messages.append({"role": "assistant", "content": prefill_content})
        
        # Stream the response from OpenAI
        completion = await client.chat.completions.create(
            model=bot_config.base_llm,
            stop=queue_item.stop,
            temperature=bot_config.temperature,
            messages=messages,
            stream=True
        )
        
        # Build response incrementally and update Discord as we get chunks
        response_text = ""
        update_count = 0
        chunk_buffer = ""
        
        async for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_buffer += chunk.choices[0].delta.content
                update_count += 1
                
                # Update Discord every few chunks to show progress
                # This prevents the UI from being overwhelmed with updates
                if update_count % 2 == 0 or len(chunk_buffer) > 50:
                    # Clean the text to remove artifacts
                    clean_text = clean_thonk(response_text + chunk_buffer)
                    
                    # Only update if we actually have new content to show
                    if response_message and not response_message.content.endswith(clean_text):
                        try:
                            await response_message.edit(content=f"**{character.name}:** {clean_text}")
                            response_text += chunk_buffer
                            chunk_buffer = ""
                        except discord.HTTPException:
                            # If editing fails, create a new message
                            response_message = await message.channel.send(f"**{character.name}:** {clean_text}")
                            response_text += chunk_buffer
                            chunk_buffer = ""
        
        # Final cleanup and send the complete message
        if response_text or chunk_buffer:
            final_text = clean_thonk(response_text + chunk_buffer)
            try:
                await response_message.edit(content=f"**{character.name}:** {final_text}")
            except discord.HTTPException:
                await message.channel.send(f"**{character.name}:** {final_text}")
        else:
            await response_message.edit(content="**[OOC: No response generated]**")
            
    except Exception as e:
        print(f"Error during streaming for {character.name}: {e}")
        try:
            await message.channel.send(f"**{character.name}:** Error: {e}")
        except:
            pass


# --- CORRECT WORKER FUNCTION ---
async def process_message(viel, db: Database, message: discord.Message, messenger: DiscordMessenger, queue: asyncio.Queue, plugin_manager:PluginManager):
    try:
        bot_config = get_bot_config(db)

        # --- 1. Load Channel ---
        is_dm = isinstance(message.channel, discord.DMChannel)
        if is_dm:
            if message.author.name not in (bot_config.dm_list or []):
                await message.channel.send("🚫 You do not have permission to talk to this bot in DM.")
                return
            channel = ActiveChannel.from_dm(message.channel, message.author, db)
        else:
            channel = ActiveChannel.from_id(str(message.channel.id), db)

        if not channel:
            return

        await message.add_reaction('✨')

        # --- 2. Determine ALL Characters to Respond ---
        responding_characters = find_all_triggered_characters(message, channel, db)
        
        # If no triggers were found, check for fallbacks (mentions, DMs, etc.)
        if not responding_characters:
            is_mention = message.guild and message.guild.me in message.mentions
            if (is_dm or is_mention) and bot_config.default_character:
                char_data = db.get_character(bot_config.default_character)
                if char_data:
                    # Create the default character and add it to our list
                    responding_characters.append(ActiveCharacter(char_data, db))

        if not responding_characters:
            # If still no one to respond, SOMETHING IS WRONG
            print("Something Is Wrong, Observer Found But Pipeline Don't")
            try:
                await message.remove_reaction('✨', viel.user)
            except discord.NotFound: 
                pass
            return

        # --- 3. Loop and Generate Response for Each Character ---
        generation_tasks = []
        for character in responding_characters:
            task = _generate_and_send_for_character_streaming(
                character, viel, db, message, channel, messenger, plugin_manager
            )
            generation_tasks.append(task)
        
        # Run all generation tasks concurrently for speed
        await asyncio.gather(*generation_tasks)

        # --- 4. Final Cleanup ---
        try:
            await message.remove_reaction('✨', viel.user)
        except discord.NotFound: 
            pass

    except Exception as e:
        print(f"Error processing message: {e}\n{traceback.format_exc()}")
        try:
            await message.add_reaction('❌')
        except: pass
    
    finally:
        # Mark the single queue item as done after all characters have responded.
        queue.task_done()

# --- MANAGER FUNCTION (This part was already correct) ---
async def think(viel, db: Database, queue: asyncio.Queue, plugin_manager:PluginManager) -> None:
    messenger = DiscordMessenger(viel)
    
    # Keep track of running tasks
    background_tasks = set()

    print("🧠 AI Core started. Waiting for messages...")

    while True:
        # 1. Clean up finished tasks
        background_tasks = {t for t in background_tasks if not t.done()}

        # 2. Get dynamic config
        try:
            bot_config = get_bot_config(db)
            concurrency_limit = bot_config.concurrency
            if concurrency_limit < 1: 
                concurrency_limit = 1
        except Exception:
            concurrency_limit = 1

        # 3. Check Concurrency Limit
        if len(background_tasks) >= concurrency_limit:
            await asyncio.wait(background_tasks, return_when=asyncio.FIRST_COMPLETED)
            continue 

        # 4. Get Message
        message: discord.Message = await queue.get()

        # 5. Spawn Worker
        task = asyncio.create_task(
            process_message(viel, db, message, messenger, queue,plugin_manager)
        )
        
        background_tasks.add(task)

def clean_up(queue_item: QueueItem) -> QueueItem:
    """
    Removes LLM artifacts/stop strings from the generated result.
    Modifies the QueueItem in place.
    """
    if not queue_item.result:
        return queue_item

    artifacts = ["[End]", "[Reply]"]

    for artifact in artifacts:
        queue_item.result = queue_item.result.replace(artifact, "")

    queue_item.result = queue_item.result.strip()
    return queue_item

# Import required for streaming
from openai import AsyncOpenAI

# --- Utility Functions (Unchanged) ---
def clean_string(s: str) -> str:
    """Removes a 'Username: ' prefix if it exists."""
    return re.sub(r'^[^\s:]+:\s*', '', s) if re.match(r'^[^\s:]+:\s*', s) else s

def clean_thonk(s: str) -> str:
    """Recursively removes <tool_call>...<tool_call> blocks from the AI's output."""
    match = re.search(r'<tool_call>', s, re.IGNORECASE)
    if match:
        # Find the start tag that corresponds to this end tag
        start_match = re.search(r'<tool_call>', s[:match.start()], re.IGNORECASE)
        if start_match:
            # Remove the block and recurse on the rest of the string
            return clean_thonk(s[:start_match.start()] + s[match.end():])
    return s
