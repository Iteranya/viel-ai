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
    """The main thinking loop of the bot."""
    # Load the bot's configuration once at the start of the loop
    bot_config = BotConfig(**db.list_configs())

    messenger = DiscordMessenger(viel)

    while True:
        # Wait for a message from the queue
        message: discord.Message = await queue.get()
        
        try:
            print("Got message~")

            # 1. Get the channel configuration
            channel = ActiveChannel.from_id(str(message.channel.id), db)
            
            # Handle DMs explicitly if ActiveChannel doesn't support them, 
            # or ensure your ActiveChannel.from_id returns a dummy object for DMs.
            if not channel and isinstance(message.channel, discord.DMChannel):
                # Logic to handle DMs if necessary, otherwise it falls to 'not channel' below
                pass 

            if not channel:
                # If the channel isn't registered, we can't do anything.
                print(f"Ignoring message in unregistered channel: {message.channel.id}")
                # FIX: Do NOT call queue.task_done() here. 
                # The 'continue' will trigger the 'finally' block which handles it.
                continue

            # 2. Determine the active character
            message_content_with_context = message.content
            character = ActiveCharacter.from_message(message_content_with_context, db)
            
            # 3. Handle Mentions (Fallout to default character)
            if not character and message.guild and message.guild.me in message.mentions:
                default_char_name = bot_config.default_character
                if default_char_name:
                    char_data = db.get_character(default_char_name)
                    if char_data:
                        character = ActiveCharacter(char_data, db)
                        print(f"No trigger found. Activated default '{default_char_name}' via mention.")

            # If still no character, there's nothing to do.
            if not character:
                print("What the fuck?? How is this even possible??? HOW DO YOU GET HERE!?!?!?")
                # FIX: Do NOT call queue.task_done() here.
                continue

            # 4. Generate the prompt
            await message.add_reaction('✨')
            prompter = PromptEngineer(character, message, channel)
            prompt = await prompter.create_prompt()

            # 5. Create a task item and generate the AI response
            queue_item = QueueItem(
                prompt=prompt,
                bot=character.name,
                user=message.author.display_name,
                stop=prompter.stopping_strings,
                message=message
            )
            
            print(f"Processing chat completion for character '{character.name}'...")
            queue_item = await generate_response(queue_item, db)

            if not queue_item.result:
                queue_item.result = "//[OOC: The AI failed to generate a response.]"
            
            # 6. Send the response back to Discord
            await messenger.send_message(character, message, queue_item)

            # Cleanup reaction
            try:
                await message.remove_reaction('✨', viel.user)
            except Exception:
                pass # Ignore if message deleted or permissions missing

        except Exception as e:
            print(f"An error occurred in the think loop: {e}\n{traceback.format_exc()}")
            try:
                await message.add_reaction('❌')
            except (discord.HTTPException, UnboundLocalError, AttributeError):
                pass 
        
        finally:
            # This executes every time the loop cycles, 
            # INCLUDING when you hit 'continue' inside the try block.
            queue.task_done()