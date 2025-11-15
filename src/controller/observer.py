# src/controller/observer.py

import re
import discord

# Adjust import paths as needed
from src.models.dimension import ActiveChannel
from typing import TYPE_CHECKING

# This block is FALSE at runtime, but TRUE for type checkers.
# This breaks the circular import!
if TYPE_CHECKING:
    from bot_run import Viel # Your main MyBot/Viel class

async def bot_behavior(message: discord.Message, bot) -> None:
    """
    Observes incoming messages and decides if the bot should process them.
    If a message is deemed relevant, it is placed on the processing queue.
    """
    # 1. Basic Pre-checks
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # 2. Handle Direct Messages (DMs)
    if isinstance(message.channel, discord.DMChannel):
        print(f"DM received from {message.author.display_name}. Queuing for default character.")
        await bot.queue.put(message)
        return

    # 3. Handle Guild Messages
    # Fetch the channel configuration from the database
    channel = ActiveChannel.from_id(str(message.channel.id), bot.db)
    if not channel:
        return # Channel is not registered, so we ignore it.

    # Reset the auto-reply counter if a human speaks
    if not message.webhook_id:
        bot.auto_response_counts[message.channel.id] = 0

    # --- Determine if the bot should activate ---

    # A. Activated by direct mention
    if bot.user in message.mentions:
        print(f"Bot was mentioned by {message.author.display_name}. Queuing message.")
        await bot.queue.put(message)
        return

    # B. Activated by replying to a whitelisted character
    if message.reference and message.reference.message_id:
        try:
            replied_to_message = await message.channel.fetch_message(message.reference.message_id)
            if replied_to_message.author.display_name in channel.whitelist:
                print(f"User replied to whitelisted bot '{replied_to_message.author.display_name}'. Queuing message.")
                await bot.queue.put(message)
                return
        except discord.NotFound:
            pass # Replied-to message might have been deleted

    # --- THIS IS THE CORRECTED BLOCK ---
    # C. Activated by a user message containing a trigger word for a WHITELISTED character
    if not message.webhook_id:
        # --- THIS IS THE CORRECTED LOGIC ---

        # If the whitelist is empty, no characters are allowed to be triggered by ambient text.
        # The bot will only respond to direct mentions or replies in this channel.
        if not channel.whitelist:
            return # Stop processing immediately.

        # If the whitelist is not empty, fetch only the whitelisted characters.
        characters_to_check = []
        for name in channel.whitelist:
            char_data = bot.db.get_character(name)
            if char_data:
                characters_to_check.append(char_data)
        
        # Now, check for triggers only from the specifically allowed characters.
        message_lower = message.content.lower()
        for char in characters_to_check:
            for trigger in char.get('triggers', []):
                # We also need to ensure the trigger isn't just a substring of a larger word.
                # Using word boundaries (\b) in a regex is the most robust way.
                # Example: Prevents 'cat' from triggering in 'caterpillar'.
                if re.search(r'\b' + re.escape(trigger.lower()) + r'\b', message_lower):
                    print(f"User message contained trigger '{trigger}' for whitelisted character '{char['name']}'. Queuing message.")
                    await bot.queue.put(message)
                    return # Stop after the first match

    # D. Activated by another bot's message (bot-to-bot interaction)
    if message.webhook_id and message.author.display_name in channel.whitelist:
        # Check if the auto-reply cap has been reached
        current_cap = bot.auto_response_counts.get(message.channel.id, 0)
        if current_cap >= channel.auto_response_cap:
            print(f"Auto-reply cap of {channel.auto_response_cap} reached in #{message.channel.name}. Ignoring bot message.")
            return

        all_triggers = [char['triggers'] for char in bot.db.list_characters()]
        flat_triggers = [trigger for sublist in all_triggers for trigger in sublist]
        message_lower = message.content.lower()

        # Check if another bot is being triggered
        if any(trigger.lower() in message_lower for trigger in flat_triggers):
            print(f"Bot '{message.author.display_name}' triggered another character. Queuing message.")
            bot.auto_response_counts[message.channel.id] = current_cap + 1 # Increment cap
            await bot.queue.put(message)
            return