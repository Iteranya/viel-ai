import discord

class ImageGalleryView(discord.ui.View):
    def __init__(self, images, title="Image Gallery", timeout=300):
        super().__init__(timeout=timeout)
        self.images = images
        self.current_index = 0
        self.title = title
        
        # Disable buttons if only one image
        if len(images) <= 1:
            self.previous_button.disabled = True
            self.next_button.disabled = True
    
    def create_embed(self):
        embed = discord.Embed(
            title=self.title,
            color=0x3498db  # Blue color, you can change this
        )
        
        # Set the current image
        if self.images:
            embed.set_image(url=self.images[self.current_index])
            embed.set_footer(text=f"Page {self.current_index + 1}/{len(self.images)}")
        
        return embed
    
    @discord.ui.button(label='◀', style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.images) - 1  # Loop to last image
        
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label='▶', style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
        else:
            self.current_index = 0  # Loop to first image
        
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label='🔀', style=discord.ButtonStyle.secondary)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        import random
        # Go to a random image
        self.current_index = random.randint(0, len(self.images) - 1)
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label='❌', style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Disable all buttons and edit message
        for item in self.children:
            item.disabled = True
        
        embed = self.create_embed()
        embed.set_footer(text="Gallery closed")
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()