import asyncio
import discord
from discord import app_commands
import traceback
from typing import Optional

from api.db.database import Database
from api.models.models import BotConfig
from src.models.dimension import ActiveChannel
import src.controller.observer as observer
import src.controller.pipeline as pipeline
from src.plugins.manager import PluginManager

# --- Helper to load config from DB ---
def get_bot_config(db: Database) -> BotConfig:
    """Fetches all config key-values from the DB and returns a BotConfig object."""
    return BotConfig(**db.list_configs())


class Viel(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = Database()
        self.config = get_bot_config(self.db)
        self.queue = asyncio.Queue()
        self.plugin_manager = PluginManager(plugin_package_path="src.plugins")
        self.auto_reply_count = 0

    async def setup_hook(self):
        """This is called when the bot is preparing to connect."""
        # --- Context Menus ---
        self.tree.add_command(app_commands.ContextMenu(
            name='Edit Bot Message',
            callback=self.edit_message_context
        ))
        self.tree.add_command(app_commands.ContextMenu(
            name='Delete Bot Message',
            callback=self.delete_message_context
        ))
        self.tree.add_command(app_commands.ContextMenu(
            name='Edit / View Caption',
            callback=self.edit_caption_context
        ))

        # --- Slash Commands ---
        # Register command groups, passing the database instance to them
        self.tree.add_command(CoreCommands(self.db))
        self.tree.add_command(ConfigCommands(self.db))
        self.tree.add_command(WhitelistCommands(self.db))
        
        # Sync commands globally. For development, you might sync to a specific guild.
        await self.tree.sync()

        self.think_task = asyncio.create_task(pipeline.think(self, self.db, self.queue, self.plugin_manager))

    async def on_ready(self):
        print(f"Discord Bot is logged in as {self.user} (ID: {self.user.id})")
        app_info = await self.application_info()
        self.invite_link = f"https://discord.com/oauth2/authorize?client_id={app_info.id}&permissions=533113207808&scope=bot" # Set the attribute here
        invite_link = f"https://discord.com/oauth2/authorize?client_id={app_info.id}&permissions=533113207808&scope=bot"
        print(f"Bot Invite Link: {invite_link}")
        print("Discord Bot is up and running.")

    async def on_message(self, message: discord.Message):
        # We pass the bot instance (self) and db instance (self.db) to the observer
        await observer.bot_behavior(message, self)

    # --- Context Menu Callbacks ---
    async def edit_message_context(self, interaction: discord.Interaction, message: discord.Message):
        if not message.webhook_id and message.author != self.user:
            await interaction.response.send_message("This is not a bot's message.", ephemeral=True)
            return
        await interaction.response.send_modal(EditMessageModal(message))

    async def delete_message_context(self, interaction: discord.Interaction, message: discord.Message):
        if not message.webhook_id and message.author != self.user:
            await interaction.response.send_message("This is not a bot's message.", ephemeral=True)
            return

        try:
            if isinstance(interaction.channel, discord.DMChannel):
                await message.delete()
            else:
                webhook = await self.fetch_webhook(message.webhook_id)
                await webhook.delete_message(message.id, thread=interaction.channel if isinstance(interaction.channel, discord.Thread) else None)
            
            await interaction.response.send_message("Message deleted.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to delete message: {e}", ephemeral=True)
            print(traceback.format_exc())

    async def edit_caption_context(self, interaction: discord.Interaction, message: discord.Message):
        # Pass the database instance to the modal
        await interaction.response.send_modal(EditCaptionModal(message, self.db))

    def run(self, *args, **kwargs):
        """Starts the bot after fetching the token from the database."""
        try:
            token = self.config.discord_key
            if not token:
                raise ValueError("Discord key is not set in the database.")
            
            # Start background tasks
            #asyncio.create_task(pipeline.think(self.db, self.queue))
            
            # Run the bot
            super().run(token, *args, **kwargs)
        except Exception as e:
            print(f"Fatal error during bot startup: {e}")
            print("Please ensure your database is configured correctly via the API/frontend.")

# --- Modals ---
class EditMessageModal(discord.ui.Modal, title='Edit Message'):
    def __init__(self, original_message: discord.Message):
        super().__init__()
        self.original_message = original_message
        self.add_item(discord.ui.TextInput(
            label='New Content', style=discord.TextStyle.long, 
            required=True, default=self.original_message.content
        ))

    async def on_submit(self, interaction: discord.Interaction):
        new_content = self.children[0].value
        try:
            if self.original_message.webhook_id:
                webhook = await interaction.client.fetch_webhook(self.original_message.webhook_id)
                thread = self.original_message.channel if isinstance(self.original_message.channel, discord.Thread) else None
                await webhook.edit_message(self.original_message.id, content=new_content, thread=thread)
            else: # It's a DM or a message sent without a webhook
                await self.original_message.edit(content=new_content)
            
            await interaction.response.send_message("Message edited successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            print(traceback.format_exc())

class EditCaptionModal(discord.ui.Modal, title='Edit Image Caption'):
    def __init__(self, original_message: discord.Message, db: Database):
        super().__init__()
        self.original_message = original_message
        self.db = db
        existing_caption = self.db.get_caption(str(self.original_message.id))
        self.add_item(discord.ui.TextInput(
            label='Image Caption', style=discord.TextStyle.long,
            placeholder='Enter a description for the image...',
            required=False, default=existing_caption
        ))

    async def on_submit(self, interaction: discord.Interaction):
        new_caption = self.children[0].value.strip()
        message_id_str = str(self.original_message.id)
        try:
            if new_caption:
                self.db.set_caption(message_id_str, new_caption)
                await interaction.response.send_message("Caption updated!", ephemeral=True)
            else:
                self.db.delete_caption(message_id_str)
                await interaction.response.send_message("Caption removed!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

# --- Slash Command Groups ---
class CoreCommands(app_commands.Group):
    def __init__(self, db: Database):
        super().__init__(name="aktiva", description="Main bot commands")
        self.db = db

    @app_commands.command(name="register_channel", description="Initializes this channel for the bot.")
    async def register_channel(self, interaction: discord.Interaction):
        server_id = str(interaction.guild.id)
        channel_id = str(interaction.channel.id)
        
        if not self.db.get_server(server_id):
            self.db.create_server(server_id, interaction.guild.name)
        
        if self.db.get_channel(channel_id):
            await interaction.response.send_message("This channel is already registered.", ephemeral=True)
            return

        default_data = {"name": interaction.channel.name, "whitelist": []}
        self.db.create_channel(channel_id, server_id, interaction.guild.name, default_data)
        await interaction.response.send_message(f"Channel '{interaction.channel.name}' has been successfully registered!", ephemeral=True)

class ConfigCommands(app_commands.Group):
    def __init__(self, db: Database):
        super().__init__(name="config", description="Channel configuration commands")
        self.db = db

    @app_commands.command(name="set_instruction", description="Set a special instruction for the AI in this channel.")
    async def set_instruction(self, interaction: discord.Interaction, instruction: str):
        channel = ActiveChannel.from_id(str(interaction.channel.id), self.db)
        if not channel:
            await interaction.response.send_message("This channel is not registered. Use `/aktiva register_channel` first.", ephemeral=True)
            return
        channel.set_instruction(instruction)
        await interaction.response.send_message(f"Instruction for this channel has been set.", ephemeral=True)

    @app_commands.command(name="set_global_note", description="Set a global note (lore) for the AI in this channel.")
    async def set_global_note(self, interaction: discord.Interaction, note: str):
        channel = ActiveChannel.from_id(str(interaction.channel.id), self.db)
        if not channel:
            await interaction.response.send_message("This channel is not registered.", ephemeral=True)
            return
        channel.set_global_note(note)
        await interaction.response.send_message(f"Global note for this channel has been set.", ephemeral=True)

class WhitelistCommands(app_commands.Group):
    def __init__(self, db: Database):
        super().__init__(name="whitelist", description="Manage character whitelist for this channel")
        self.db = db

    @app_commands.command(name="add", description="Add characters to the whitelist (comma-separated).")
    async def add(self, interaction: discord.Interaction, names: str):
        channel = ActiveChannel.from_id(str(interaction.channel.id), self.db)
        if not channel:
            await interaction.response.send_message("This channel is not registered.", ephemeral=True)
            return
        
        new_names = {name.strip() for name in names.split(',')}
        current_whitelist = set(channel.whitelist)
        current_whitelist.update(new_names)
        channel.set_whitelist(sorted(list(current_whitelist)))
        await interaction.response.send_message(f"Added `{', '.join(new_names)}` to the whitelist.", ephemeral=True)

    @app_commands.command(name="remove", description="Remove characters from the whitelist (comma-separated).")
    async def remove(self, interaction: discord.Interaction, names: str):
        channel = ActiveChannel.from_id(str(interaction.channel.id), self.db)
        if not channel:
            await interaction.response.send_message("This channel is not registered.", ephemeral=True)
            return

        names_to_remove = {name.strip() for name in names.split(',')}
        new_whitelist = [name for name in channel.whitelist if name not in names_to_remove]
        channel.set_whitelist(new_whitelist)
        await interaction.response.send_message(f"Removed `{', '.join(names_to_remove)}` from the whitelist.", ephemeral=True)
        
    @app_commands.command(name="view", description="View the current character whitelist for this channel.")
    async def view(self, interaction: discord.Interaction):
        channel = ActiveChannel.from_id(str(interaction.channel.id), self.db)
        if not channel:
            await interaction.response.send_message("This channel is not registered.", ephemeral=True)
            return

        if not channel.whitelist:
            await interaction.response.send_message("The whitelist is empty. All characters are allowed.", ephemeral=True)
        else:
            character_items = [f"- `{name}`" for name in channel.whitelist]
            
            # 2. Join these items with a newline character.
            # This creates a single string like: "- `Alice`\n- `Bob`"
            formatted_list = "\n".join(character_items)
            
            # 3. Now, use the clean, pre-formatted string in your f-string.
            response_text = f"**Whitelisted Characters:**\n{formatted_list}"
            
            await interaction.response.send_message(response_text, ephemeral=True)