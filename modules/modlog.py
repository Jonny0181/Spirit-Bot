import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal

class Modlog(commands.GroupCog, name="modlog"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.modlog
        
    @app_commands.command(name="enable")
    async def enable(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel]):
        """Enables the modlog system."""
        ...
        
    @app_commands.command(name="disable")
    async def disable(self, interaction: discord.Interaction):
        """Disables the modlog system."""
        ...
        
    @app_commands.command(name="toggle")
    async def toggle(self, interaction: discord.Interaction, setting: Literal['Messages', 'Leave', 'Join', 'Channel', 'Guild', 'Voice']):
        """Toggles a modlog setting on or off."""
        ...
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Modlog(bot))