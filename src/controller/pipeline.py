import asyncio
import traceback
import discord
import os
import uuid  # For creating unique temporary filenames

# Adjust import paths to match your project structure
from api.db.database import Database
from src.controller.messenger import DiscordMessenger
from src.models.aicharacter import ActiveCharacter
from src.models.dimension import ActiveChannel
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from api.models.models import BotConfig


async def think(viel, db: Database, queue: asyncio.Queue) -> None:
    
    messenger = DiscordMessenger(viel)

    while True:
        message: discord.Message = await queue.get()
        bot_config = BotConfig(**db.list_configs())
        
        try:
            # --- 1. Check Permission & Load Channel ---
            is_dm = isinstance(message.channel, discord.DMChannel)
            
            if is_dm:
                # Check Whitelist
                allowed_users = bot_config.dm_list or []
                if message.author.name not in allowed_users:
                    
                    print(f"Denied DM access to {message.author.name}, not in allowed_users {allowed_users}")
                    await message.channel.send("🚫 You do not have permission to talk to this bot in DM.")
                    continue 
                
                # Load (or Auto-Create) the DM Channel from DB
                # We pass 'db' now so it can save/load!
                channel = ActiveChannel.from_dm(message.channel, message.author, db)
            
            else:
                # Regular Server Channel
                channel = ActiveChannel.from_id(str(message.channel.id), db)

            if not channel:
                # This happens for unregistered server channels
                print(f"Ignoring message in unregistered channel: {message.channel.id}")
                continue

            # --- 2. Determine Active Character ---
            message_content_with_context = message.content
            character = ActiveCharacter.from_message(message_content_with_context, db)
            
            # Handle Mentions OR DM default fallback
            if not character and (is_dm or (message.guild and message.guild.me in message.mentions)):
                default_char_name = bot_config.default_character
                if default_char_name:
                    char_data = db.get_character(default_char_name)
                    if char_data:
                        character = ActiveCharacter(char_data, db)

            if not character:
                continue

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
            queue_item = await generate_response(queue_item, db)

            if not queue_item.result:
                queue_item.result = "//[OOC: The AI failed to generate a response.]"
            
            await messenger.send_message(character, message, queue_item)

            try:
                await message.remove_reaction('✨', viel.user)
            except Exception:
                pass

        except Exception as e:
            print(f"Error: {e}\n{traceback.format_exc()}")
            try:
                await message.add_reaction('❌')
            except:
                pass
        
        finally:
            queue.task_done()