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
        bot.auto_reply_count = 0

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
            bot_name = replied_to_message.author.display_name
            if bot_name in channel.whitelist:
                print(f"User replied to whitelisted bot '{bot_name}'. Queuing message.")
                message.content = f"[Replying To {bot_name}]\n{message.content}"
                await bot.queue.put(message)
                return
        except discord.NotFound:
            pass # Replied-to message might have been deleted

    triggered_characters = set()

    if not message.webhook_id:
        if not channel.whitelist:
            return

        characters_to_check = []
        for name in channel.whitelist:
            char_data = bot.db.get_character(name)
            if char_data:
                characters_to_check.append(char_data)

        message_lower = message.content.lower()

        for char in characters_to_check:
            name_trigger = char.get("name", "").lower()
            triggers = [t.lower() for t in char.get("triggers", [])]
            extended_triggers = triggers + ([name_trigger] if name_trigger else [])

            for trigger in extended_triggers:
                if not trigger:
                    continue

                if re.search(r'\b' + re.escape(trigger) + r'\b', message_lower):
                    # Add the character name to the set so duplicates don't re-add
                    triggered_characters.add(char['name'])
                    break  # Stop checking more triggers for *this* character

        # After scanning all, queue each triggered character
        for name in triggered_characters:
            print(
                f"User message triggered whitelisted character '{name}'. Queuing message."
            )
            await bot.queue.put(message)


    # --- MODIFICATION: Updated bot-to-bot logic ---
    # D. Activated by another bot's message (bot-to-bot interaction)
    if message.webhook_id:
        # Fetch the GLOBAL cap from the bot's loaded configuration
        cap = bot.config.auto_cap
        
        # Check if the GLOBAL auto-reply cap has been reached
        if bot.auto_reply_count >= cap:
            print(f"Global auto-reply cap of {cap} reached. Ignoring bot message from '{message.author.display_name}'.")
            return

        all_triggers = [char['triggers'] for char in bot.db.list_characters()]
        flat_triggers = [trigger for sublist in all_triggers for trigger in sublist]
        message_lower = message.content.lower()

        # Check if another bot is being triggered
        if any(trigger.lower() in message_lower for trigger in flat_triggers):
            print(f"Bot '{message.author.display_name}' triggered another character. Queuing message.")
            # Increment the GLOBAL counter
            bot.auto_reply_count += 1
            await bot.queue.put(message)
            return