import asyncio
import json
import logging
import os
from typing import Optional
import discord
from discord import app_commands
import src.controller.observer as observer
import src.controller.pipeline as pipeline
import src.data.dimension_data as dim
import src.data.card_data as card
import src.data.config_data as config_module
from src.controller import config as conf

# Setup Discord client
intents: discord.Intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
CAPTIONS_FILE  = "res/captions.jsonl"
bot_invite = None
# Modal
class EditMessageModal(discord.ui.Modal, title='Edit Message'):
    def __init__(self, original_message):
        super().__init__()
        self.original_message:discord.Message = original_message
        print(original_message)

        # Set the default value of the TextInput to the content of the original message
        self.new_content = discord.ui.TextInput(
            label='New Content', 
            style=discord.TextStyle.long, 
            required=True, 
            default=self.original_message.content
        )
        # Add the TextInput to the modal
        self.add_item(self.new_content)

    async def on_submit(self, interaction: discord.Interaction):
        thread = None
        dm = None
        webhook = None
        try:
            try:
                self.original_message = await self.original_message.channel.fetch_message(self.original_message.id)
            except discord.NotFound:
                print(f"Message ID {self.original_message.id} not found in thread {self.original_message.channel.name}.")
                await interaction.response.send_message("The original message was not found in this thread.", ephemeral=True)
                return
            # Fetch the webhook associated with the original message
            if isinstance(self.original_message.channel,discord.Thread):
                webhooks = await self.original_message.channel.parent.webhooks()
                thread  = self.original_message.channel
                webhook = next((hook for hook in webhooks if hook.id == self.original_message.webhook_id), None)
            elif not self.original_message.webhook_id:
                dm = self.original_message.channel
            else:
                webhooks = await self.original_message.channel.webhooks()
                webhook = next((hook for hook in webhooks if hook.id == self.original_message.webhook_id), None)

            if webhook:
                await interaction.response.send_message("Webhook not found for this message.", ephemeral=True)
                
                print("ORIGINAL MESSAGE:")
                print(self.original_message.id)
                print(self.new_content.value)
                # Edit the message using the webhook
                if thread is not None:
                    await webhook.edit_message(
                        message_id=self.original_message.id,
                        content=self.new_content.value,
                        thread = thread
                    )
                else:
                    await webhook.edit_message(
                        message_id=self.original_message.id,
                        content=self.new_content.value,
                    )
            else:
                print("Editing DM Message Because Webhook Not Found")
                new_content = self.new_content .value
                print(f"New Message Content: {new_content}")
                await self.original_message.edit(content = new_content)
                await interaction.response.send_message("Message edited successfully!", ephemeral=True)

        except discord.NotFound:

            await interaction.response.send_message("The original message was not found.", ephemeral=True)
        except Exception as e:

            await interaction.response.send_message(f"An error occurred while editing the message: {e}", ephemeral=True)

class EditCaptionModal(discord.ui.Modal, title='Edit Image Caption'):
    def __init__(self, original_message: discord.Message):
        super().__init__()
        self.original_message = original_message

        # Helper function to get the current caption from the file
        existing_caption = self._get_caption_from_file(self.original_message.id)

        # Create the text input field
        self.new_caption = discord.ui.TextInput(
            label='Image Caption',
            style=discord.TextStyle.long,
            placeholder='Enter a description for the image in the message...',
            required=False,  # Allow submitting an empty string to remove a caption
            default=existing_caption
        )
        self.add_item(self.new_caption)

    def _get_caption_from_file(self, message_id: int) -> Optional[str]:
        """Reads the jsonl file to find a caption for a specific message ID."""
        if not os.path.exists(CAPTIONS_FILE):
            return None
        try:
            with open(CAPTIONS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get("message_id") == message_id:
                            return data.get("caption")
                    except json.JSONDecodeError:
                        continue # Skip corrupted lines
        except IOError as e:
            print(f"Error reading captions file: {e}")
        return None

    def _save_caption_to_file(self, message_id: int, new_caption: str):
        """
        Updates or adds a caption in the jsonl file.
        This reads all data, modifies it in memory, and rewrites the file.
        """
        lines_to_write = []
        entry_found = False

        # Read existing entries
        if os.path.exists(CAPTIONS_FILE):
            try:
                with open(CAPTIONS_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if data.get("message_id") == message_id:
                                # This is the entry we want to edit
                                if new_caption: # Update if new caption is not empty
                                    data["caption"] = new_caption
                                    lines_to_write.append(data)
                                # If new_caption is empty, we effectively delete it by not appending it
                                entry_found = True
                            else:
                                # Keep all other entries
                                lines_to_write.append(data)
                        except json.JSONDecodeError:
                            continue # Skip corrupted lines
            except IOError as e:
                print(f"Error reading captions file for saving: {e}")
                # Potentially raise an exception here to notify the user
                raise

        # If the entry was not found and the new caption is not empty, add it
        if not entry_found and new_caption:
            lines_to_write.append({"message_id": message_id, "caption": new_caption})

        # Write all the data back to the file
        try:
            with open(CAPTIONS_FILE, "w", encoding="utf-8") as f:
                for entry in lines_to_write:
                    f.write(json.dumps(entry) + "\n")
        except IOError as e:
            print(f"Error writing captions file: {e}")
            raise

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Get the new content from the text input
            new_text = self.new_caption.value.strip()

            # Save the new caption to the jsonl file
            self._save_caption_to_file(self.original_message.id, new_text)

            # Let the user know it was successful
            await interaction.response.send_message("Caption updated successfully!", ephemeral=True)

        except Exception as e:
            print(f"An error occurred while editing the caption: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def delete_message_context(interaction: discord.Interaction, message: discord.Message):
    await delete(message,interaction)

async def edit_message_context(interaction: discord.Interaction, message: discord.Message):
    if message.webhook_id!=None:
        await client.fetch_webhook(message.webhook_id)
        await interaction.response.send_modal(EditMessageModal(message))
    else:
        await interaction.response.send_modal(EditMessageModal(message))
    await interaction.response.send_message("This isn't a bot's message, this is human's message",ephemeral=True)

async def edit_caption_context(interaction: discord.Interaction, message: discord.Message):

    await interaction.response.send_modal(EditCaptionModal(message))

async def edit(message:discord.Message, webhook_id, new_content):
    print(webhook_id)
    webhook = await client.fetch_webhook(webhook_id)
    await webhook.edit_message(message_id=message.id,content=new_content)

async def delete(message:discord.Message,interaction:discord.Interaction):
    
    if isinstance(interaction.channel,discord.Thread):
        webhook = await client.fetch_webhook(message.webhook_id)
        await webhook.delete_message(message.id,thread=interaction.channel)
    elif isinstance(interaction.channel,discord.DMChannel):
        await message.delete()
    else:
        webhook = await client.fetch_webhook(message.webhook_id)
        await webhook.delete_message(message.id)
    await interaction.response.send_message("Deleted~",ephemeral=True)

# Core commands group
class CoreCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="aktiva", description="Main Aktiva command")
        
    @app_commands.command(name="main_char", description="Show Main Character Info")
    async def help(self, interaction: discord.Interaction):
        # response = filemanager.show_main_char()
        response = "Under Construction"
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="register_channel", description="Register a channel into the bot")
    async def register_channel(self,interaction: discord.Interaction):
        dim.init_channel(interaction.guild.name,interaction.channel.name)
        await interaction.response.send_message("Channel registered!", ephemeral=True)

    
# Configuration commands subgroup
class ConfigCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="config", description="Configuration commands")

    @app_commands.command(name="set_instruction", description="Edit Instruction Data")
    async def set_instruction(self, interaction: discord.Interaction, instruction_desc: str):
        response = dim.edit_instruction(interaction, instruction_desc)
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="get_instruction", description="View Current Instruction Data")
    async def get_instruction(self, interaction: discord.Interaction):
        response = dim.get_instruction(interaction)
        await interaction.response.send_message(response, ephemeral=True)
        
    @app_commands.command(name="toggle_battle_rp", description="Toggles Battle RP mode by adding/removing the <battle_rp> tag.")
    async def toggle_battle_rp(self, interaction: discord.Interaction):
        """
        Toggles a specific tag in the instruction string.
        """
        # Define the specific tag for Battle RP
        rp_tag = "<battle_rp>"
        
        # Get the current instruction string from your data manager
        current_instruction = dim.get_instruction(interaction)
        
        new_instruction = ""
        status_message = ""

        # Check if the tag exists in the current instruction
        if rp_tag in current_instruction:
            # If it exists, remove it and set the status to OFF
            new_instruction = current_instruction.replace(rp_tag, "").strip()
            status_message = "Battle RP is now **OFF**."
        else:
            # If it doesn't exist, append it and set the status to ON
            # We add a space before the tag for clean formatting. .strip() handles case where original instruction is empty.
            new_instruction = (current_instruction + " " + rp_tag).strip()
            status_message = "Battle RP is now **ON**."
            
        # Save the modified instruction using your existing edit function
        dim.edit_instruction(interaction, new_instruction)
        
        # Send an ephemeral confirmation message to the user who ran the command
        await interaction.response.send_message(status_message, ephemeral=True)
        
    @app_commands.command(name="set_global", description="Edit Global Data")
    async def set_global(self, interaction: discord.Interaction, global_var: str):
        response = dim.edit_global(interaction, global_var)
        await interaction.response.send_message(response, ephemeral=True)
        
    @app_commands.command(name="get_global", description="View Current Global Data")
    async def get_global(self, interaction: discord.Interaction):
        response = dim.get_global(interaction)
        await interaction.response.send_message(response, ephemeral=True)

# Character management subgroup
class CharacterCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="character", description="Character management commands")
        
    @app_commands.command(name="import", description="Import a Character JSON file")
    async def import_character(self, interaction: discord.Interaction, character_json: discord.Attachment):
        try:
            # Attempt to process the attachment
            result = await card.save_character_json(character_json)
            await interaction.response.send_message(f"Result: {result}", ephemeral=True)
        except ValueError as e:
            # Handle invalid file type errors
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        except Exception as e:
            # Catch all other exceptions to avoid crashing
            await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

# Whitelist management subgroup
class WhitelistCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="whitelist", description="Whitelist management commands")
        
    @app_commands.command(name="set", description="Add Characters, Comma Separated")
    async def set(self, interaction: discord.Interaction, character_name: str):
        response = dim.set_whitelist(interaction, character_name)
        await interaction.response.send_message(response, ephemeral=True)
        
    @app_commands.command(name="get", description="Show Available Characters")
    async def get(self, interaction: discord.Interaction):
        response = dim.get_whitelist(interaction)
        await interaction.response.send_message(response, ephemeral=True)
        
    @app_commands.command(name="clear", description="Clear Whitelist")
    async def clear(self, interaction: discord.Interaction):
        response = dim.clear_whitelist(interaction)
        await interaction.response.send_message(response, ephemeral=True)
        
    @app_commands.command(name="remove", description="Remove a Character")
    async def remove(self, interaction: discord.Interaction, character_name: str):
        response = dim.delete_whitelist(interaction, character_name)
        await interaction.response.send_message(response, ephemeral=True)

def setup_commands():
    
    # Create all the groups
    aktiva_group = CoreCommands()
    config_group = ConfigCommands()
    character_group = CharacterCommands()
    whitelist_group = WhitelistCommands()
    
    # Add all groups to the command tree
    tree.add_command(aktiva_group)
    tree.add_command(config_group)
    tree.add_command(character_group)
    tree.add_command(whitelist_group)

# (All your commands, modal classes, event handlers, etc.)
# ... (copy all modal, context menu, commands groups here) ...

def setup_bot():
    print("Setting up Discord Bot...")

    edit_message = discord.app_commands.ContextMenu(
        name='Edit Bot Message',
        callback=edit_message_context,
        type=discord.AppCommandType.message
    )

    # Command to Delete Message (You Right Click On It)
    delete_message = discord.app_commands.ContextMenu(
        name='Delete Bot Message',
        callback=delete_message_context,
        type=discord.AppCommandType.message
    )

    edit_caption = discord.app_commands.ContextMenu(
        name= 'Edit / View Caption',
        callback=edit_caption_context,
        type=discord.AppCommandType.message
    )
    
    # Initialize the Commands
    tree.add_command(edit_caption)
    tree.add_command(edit_message)
    tree.add_command(delete_message)
    setup_commands()

async def start_bot(config: conf.Config):
    if config.discord_key:
        # Kick off background thinking loop
        asyncio.create_task(pipeline.think())

        await client.start(config.discord_key)
    else:
        raise Exception("Discord Bot Key Empty")

@client.event
async def on_ready():
    global bot_invite
    print(f"Discord Bot is logged in as {client.user}")
    conf.bot_user = client.user
    app_info = await client.application_info()
    await tree.sync(guild=None)
    print("Discord Bot is up and running.")
    bot_invite = f"Bot Invite: https://discord.com/oauth2/authorize?client_id={app_info.id}&permissions=533113207808&integration_type=0&scope=bot"
    print(bot_invite)
    

@client.event
async def on_message(message: discord.Message):
    # if message.author == client.user:
    #     return
    await observer.bot_behavior(message, client)

setup_bot()

if __name__ == "__main__":
    # Load config and token
    config = config_module.load_or_create_config()
    discord_token = config.discord_key
    if not discord_token:
        raise RuntimeError("$DISCORD_TOKEN env variable is not set!")

    try:
        client.run(discord_token)
    except Exception as e:
        print(f"Failed to run the bot: {e}")
