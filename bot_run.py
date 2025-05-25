import asyncio
import logging
import discord
from discord import app_commands
import src.controller.observer as observer
import src.controller.pipeline as pipeline
import src.data.dimension_data as dim
import src.data.card_data as card
import src.data.config_data as config_module
from src.controller import config as conf

# Load config and token
config = config_module.load_or_create_config()
discord_token = config.discord_key
if discord_token is None:
    raise RuntimeError("$DISCORD_TOKEN env variable is not set!")

# Setup Discord client
intents: discord.Intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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
        webhook = None
        
        try:
            # Fetch the original message to ensure it exists
            try:
                self.original_message = await self.original_message.channel.fetch_message(self.original_message.id)
            except discord.NotFound:
                print(f"Message ID {self.original_message.id} not found in channel {self.original_message.channel}.")
                await interaction.response.send_message("The original message was not found.", ephemeral=True)
                return

            # Handle different channel types
            if isinstance(self.original_message.channel, discord.DMChannel):
                # DM channels don't support webhooks, use direct message editing
                if hasattr(self.original_message, 'edit'):
                    await self.original_message.edit(content=self.new_content.value)
                    await interaction.response.send_message("Message edited successfully!", ephemeral=True)
                else:
                    await interaction.response.send_message("Cannot edit this message in DM.", ephemeral=True)
                    
            elif isinstance(self.original_message.channel, discord.Thread):
                # Thread - get webhooks from parent channel
                thread = self.original_message.channel
                webhooks = await thread.parent.webhooks()
                webhook = next((hook for hook in webhooks if hook.id == self.original_message.webhook_id), None)
                
                if webhook:
                    print("ORIGINAL MESSAGE:")
                    print(self.original_message.id)
                    print(self.new_content.value)
                    
                    await webhook.edit_message(
                        message_id=self.original_message.id,
                        content=self.new_content.value,
                        thread=thread
                    )
                    await interaction.response.send_message("Message edited successfully!", ephemeral=True)
                else:
                    # Fallback to direct edit if webhook not found
                    if hasattr(self.original_message, 'edit'):
                        await self.original_message.edit(content=self.new_content.value)
                        await interaction.response.send_message("Message edited successfully!", ephemeral=True)
                    else:
                        await interaction.response.send_message("Cannot edit this message.", ephemeral=True)
                        
            else:
                # Regular text channel
                webhooks = await self.original_message.channel.webhooks()
                webhook = next((hook for hook in webhooks if hook.id == self.original_message.webhook_id), None)
                
                if webhook:
                    print("ORIGINAL MESSAGE:")
                    print(self.original_message.id)
                    print(self.new_content.value)
                    
                    await webhook.edit_message(
                        message_id=self.original_message.id,
                        content=self.new_content.value
                    )
                    await interaction.response.send_message("Message edited successfully!", ephemeral=True)
                else:
                    # Fallback to direct edit if webhook not found
                    if hasattr(self.original_message, 'edit'):
                        await self.original_message.edit(content=self.new_content.value)
                        await interaction.response.send_message("Message edited successfully!", ephemeral=True)
                    else:
                        await interaction.response.send_message("Cannot edit this message.", ephemeral=True)

        except discord.NotFound:
            await interaction.response.send_message("The original message was not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("No permission to edit this message.", ephemeral=True)
        except Exception as e:
            print(f"Error editing message: {e}")
            await interaction.response.send_message("An error occurred while editing the message.", ephemeral=True)
async def delete_message_context(interaction: discord.Interaction, message: discord.Message):
    await delete(message,interaction)

async def edit_message_context(interaction: discord.Interaction, message: discord.Message):
    if message.webhook_i:
        await client.fetch_webhook(message.webhook_id)
        await interaction.response.send_modal(EditMessageModal(message))
    else:
        await interaction.response.send_modal(EditMessageModal(message))
    await interaction.response.send_message("This isn't a bot's message, this is human's message",ephemeral=True)

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

async def start_pipeline():
    # Kick off background thinking loop
    asyncio.create_task(pipeline.think())

@client.event
async def on_ready():
    print(f"Discord Bot is Loading... Logged in as {client.user}")
    conf.bot_user = client.user
    # client.user.display_name = conf.default_character
    # logging.basicConfig(level=logging.DEBUG)
    # Setup commands and events
    # (e.g., context menus, tree.sync, etc.)
    # Command to Edit Message (You Right Click On It)
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
    
    # Initialize the Commands
    tree.add_command(edit_message)
    tree.add_command(delete_message)

    setup_commands()
    await tree.sync(guild=None)
    await start_pipeline()
    print("Discord Bot is up and running.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await observer.bot_behavior(message, client)

if __name__ == "__main__":
    try:
        client.run(discord_token)
    except Exception as e:
        print(f"Failed to run the bot: {e}")