import asyncio
import traceback
import discord
import os
import uuid  # For creating unique temporary filenames

# Adjust import paths to match your project structure
from api.db.database import Database
from src.models.aicharacter import ActiveCharacter
from src.models.dimension import ActiveChannel
from src.models.prompts import PromptEngineer
from src.models.queue import QueueItem
from src.utils.llm_new import generate_response
from src.controller.discordo import send  # Assuming this is the function to send messages
from api.models.models import BotConfig


async def think(db: Database, queue: asyncio.Queue) -> None:
    """The main thinking loop of the bot."""
    # Load the bot's configuration once at the start of the loop
    bot_config = BotConfig(**db.list_configs())

    while True:
        try:
            # Get the next message to process from the queue
            message: discord.Message = await queue.get()

            # 1. Get the channel configuration
            channel = ActiveChannel.from_id(str(message.channel.id), db)
            if not channel:
                # If the channel isn't registered, we can't do anything.
                print(f"Ignoring message in unregistered channel: {message.channel.id}")
                queue.task_done()
                continue

            # 2. Determine the active character
            message_content_with_context = message.content
            
            character = ActiveCharacter.from_message(message_content_with_context, db)
            
            # If no trigger found, check if the bot was mentioned.
            # `message.guild.me` is the ClientUser object for the current server
            if not character and message.guild and message.guild.me in message.mentions:
                 # Load the default character from the config
                default_char_name = bot_config.default_character
                if default_char_name:
                    char_data = db.get_character(default_char_name)
                    if char_data:
                        character = ActiveCharacter(char_data, db)
                        print(f"No trigger found. Activated default character '{default_char_name}' due to mention.")

            # If still no character, there's nothing to do.
            if not character:
                queue.task_done()
                continue

            # 4. Generate the prompt
            # Add a thinking reaction to the message
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
                queue_item.result = "//[OOC: Something went wrong and the AI failed to generate a response.]"
            
            # 6. Send the response back to Discord
            await send(character, message, queue_item)

        except Exception as e:
            print(f"An error occurred in the think loop: {e}\n{traceback.format_exc()}")
            # Add a failure reaction if something goes wrong
            try:
                await message.add_reaction('❌')
            except (discord.HTTPException, UnboundLocalError):
                pass # Message might have been deleted or was never assigned
        finally:
            # Signal that this task from the queue is complete
            queue.task_done()