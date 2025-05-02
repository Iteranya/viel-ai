import asyncio
import discord
from discord import app_commands
import logging
import src.controller.config as config

from discord import app_commands
import src.controller.observer as observer
import src.controller.pipeline as pipeline
import src.controller.filemanager as filemanager

client = config.client
discord_token = config.discord_token

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
            elif isinstance(self.original_message.channel,discord.DMChannel):
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
                self.original_message.edit(self.new_content.value)
                await interaction.response.send_message("Message edited successfully!", ephemeral=True)

        except discord.NotFound:

            await interaction.response.send_message("The original message was not found.", ephemeral=True)
        except Exception as e:

            await interaction.response.send_message("An error occurred while editing the message.", ephemeral=True)

tree = app_commands.CommandTree(client)

async def delete_message_context(interaction: discord.Interaction, message: discord.Message):
    await delete(message,interaction)

async def edit_message_context(interaction: discord.Interaction, message: discord.Message):
    if message.webhook_id!=None:
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

@tree.command(name="register_channel", description="Register a channel into the bot")
async def register_channel(interaction: discord.Interaction):
    # Something Something Register Channel
    # I think I'll use the filemanager thingy
    filemanager.init_channel(interaction.guild.name,interaction.channel.name)
    await interaction.response.send_message("Channel registered!", ephemeral=True)

@client.event
async def on_ready():
    # Let owner known in the console that the bot is now running!
    print(f'Discord Bot is Loading...')
    config.bot_user = client.user
    # Oh right, I have logging...
    logging.basicConfig(level=logging.DEBUG)

    # Setup the Connection with API
    asyncio.create_task(pipeline.think())

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

    await tree.sync(guild=None)  
    print(f'Discord Bot is up and running.')

@client.event
async def on_message(message):
    if message is None:
        return
    
    # Trigger the Observer Behavior (The command that listens to Keyword)
    print("Message Get")
    await observer.bot_behavior(message, client)

# Run the Bot
client.run(discord_token)