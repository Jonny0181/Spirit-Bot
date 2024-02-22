import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands

class Warnings(commands.GroupCog, name="warnings"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.warnings

    @app_commands.command(name="setup")
    async def setup(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel], warn_kick: int, warn_ban: int):
        """Setup warnings on your server."""
        ...
        
    @app_commands.command(name="warns")
    async def warns(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        """Shows a users current warnings."""
        if not member: member = interaction.user
        ...
        
    @app_commands.command(name="clear")
    async def clear(self, interaction: discord.Interaction, member: discord.Member):
        """Clears a users active warnings."""
        ...
        
    @app_commands.command(name="add")
    async def add(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Adds a warning to a user."""
        ...
        
    @app_commands.command(name="remove")
    async def remove(self, interaction: discord.Interaction, member: discord.Member, warn_id: str):
        """Remove a active warning from a user."""
        ...
        
    async def commit_warning(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        ...
        
    async def log_warning(self, interaction: discord.Interaction, data: dict):
        ...

async def setup(bot: commands.Bot):
    await bot.add_cog(Warnings(bot))