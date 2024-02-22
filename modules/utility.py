import discord
import time
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.hybrid_command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Ping the bot and get the latency."""
        start_time = time.monotonic()
        message = await ctx.send("Pong!")
        end_time = time.monotonic()
        latency = (end_time - start_time) * 1000
        await message.edit(content=f"Pong! {round(latency)}ms")
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
