import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.modlog

    @app_commands.command(name="ban")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str, messages: app_commands.Range[int, 1, 7]):
        """Ban a user from the server, must give a reason."""
        ...
        
    @app_commands.command(name="kick")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Kick a use from the server, must give a reason."""
        ...

    async def log_action(self, interaction: discord.Interaction):
        ...

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))