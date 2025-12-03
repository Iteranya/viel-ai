# src/controller/observer.py

import re
import discord
# Adjust import paths as needed
from src.models.dimension import ActiveChannel
from typing import TYPE_CHECKING


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

    # # Reset the auto-reply counter if a human speaks
    # if not message.webhook_id:
    #     bot.auto_reply_count = 0

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

    # C. Activated by a user message containing a trigger word for a WHITELISTED character
    if not message.webhook_id:
        if not channel.whitelist:
            return  # Stop processing immediately.

        characters_to_check = []
        for name in channel.whitelist:
            char_data = bot.db.get_character(name)
            if char_data:
                characters_to_check.append(char_data)

        message_lower = message.content.lower()

        for char in characters_to_check:
            # Grab triggers + the character's own name
            name_trigger = char.get("name", "").lower()
            triggers = [t.lower() for t in char.get("triggers", [])]

            extended_triggers = triggers + ([name_trigger] if name_trigger else [])
            print(triggers)
            channel_name = channel.name.lower()
            channel_name = "#" + channel_name
            print(channel_name)
            for trigger in extended_triggers:
                if not trigger:
                    continue

                # Word-boundary regex check
                if re.search(r'\b' + re.escape(trigger) + r'\b', message_lower):
                    print(
                        f"User message contained trigger '{trigger}' for whitelisted character '{char['name']}'. Queuing message."
                    )
                    
                    await bot.queue.put(message)
                    bot.auto_reply_count = 0
                    return  # Stop after the first match
                
                # Function to permanently make character answer in a channel
                elif re.search(re.escape(trigger), "#"+ channel_name):
                    print(
                        f"User message is inside '{channel.name}' for whitelisted character '{char['name']}'. Queuing message."
                    )
                    message.content = f"[Replying To {char['name']}]\n{message.content}"
                    await bot.queue.put(message)
                    bot.auto_reply_count = 0
                    return
                



    # D. Activated by another bot's message (bot-to-bot interaction)
    if message.webhook_id:
        # Fetch the GLOBAL cap from the bot's loaded configuration
        cap = bot.config.auto_cap
        
        # Check if the GLOBAL auto-reply cap has been reached
        if bot.auto_reply_count >= cap:
            print(f"Global auto-reply cap of {cap} reached. Ignoring bot message from '{message.author.display_name}'.")
            return
            
        # --- FIXED LOGIC STARTS HERE ---
        # Now, respect the channel's whitelist for bot-to-bot messages
        if not channel.whitelist:
            return # No whitelisted characters, nothing to do.

        characters_to_check = []
        for name in channel.whitelist:
            char_data = bot.db.get_character(name)
            if char_data:
                characters_to_check.append(char_data)

        message_lower = message.content.lower()

        for char in characters_to_check:
            # Grab triggers + the character's own name (same as user logic)
            name_trigger = char.get("name", "").lower()
            triggers = [t.lower() for t in char.get("triggers", [])]
            extended_triggers = triggers + ([name_trigger] if name_trigger else [])

            for trigger in extended_triggers:
                if not trigger:
                    continue
                # Use the same precise regex check
                if re.search(r'\b' + re.escape(trigger) + r'\b', message_lower):
                    print(
                        f"Bot '{message.author.display_name}' used trigger '{trigger}' for whitelisted character '{char['name']}'. Queuing message."
                    )
                    # Increment the GLOBAL counter for bot-to-bot talk
                    bot.auto_reply_count += 1
                    await bot.queue.put(message)
                    return # Stop after the first match