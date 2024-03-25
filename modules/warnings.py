import discord
import datetime
from typing import Optional
from discord.ext import commands
from discord import app_commands

class AddWarningModal(discord.ui.Modal):
    def __init__(self, commit_warning, member: discord.Member):
        super().__init__(title="Add Warning")
        self.commit_warning = commit_warning
        self.member = member
        
        self.reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Reason for warning...",
            required=True,
            max_length=100
        )
        self.add_item(self.reason)
        
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.commit_warning(interaction, self.member, self.reason.value)

class Warnings(commands.GroupCog, name="warnings"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.warnings

        @bot.tree.context_menu(name="Add Warning")
        async def add_warning(interaction: discord.Interaction, user: discord.Member):
        
            if user == interaction.user:
                return await interaction.response.send_message("You cannot warn yourself!", ephemeral=True)
            elif user.bot:
                return await interaction.response.send_message("You cannot give a warning to a bot!", ephemeral=True)
            elif user == interaction.guild.owner:
                return await interaction.response.send_message("You can't give the server owner a warning!", ephemeral=True)
            
            return await interaction.response.send_modal(AddWarningModal(self.commit_warning, user))

    @app_commands.command(name="setup")
    async def setup(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel], warn_kick: int, warn_ban: int):
        """Setup warnings on your server."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data:
            if not channel and not data['channelCreated']:
                channel = await self.setup_warning_channel(interaction, channel)
                await self.update_warning_channel(interaction, channel)
                return await interaction.followup.send(f"The warnings log channel has been updated to {channel.mention}!")
            elif channel and channel.id != data['channelID']:
                await self.update_warning_channel(interaction, channel)
                return await interaction.followup.send(f"The warnings log channel has been updated to {channel.mention}!")
            else:
                return await interaction.followup.send(f"Warning logs are already setup to be sent to this channel!")
        else:
            channel = await self.setup_warning_channel(interaction, channel)
            data = {"_id": interaction.guild.id, "enabled": True, "channelID": channel.id, "channelCreated": True, "userWarnings": [], "kickThreshold": warn_kick, "banThreshold": warn_ban}
            await self.db.insert_one(data)
            return await interaction.followup.send(
                content=f"The warning system has been enabled. Logs will be posted to {channel.mention}. To give a user a warning use `/warnings add @member`.")
        
    @app_commands.command(name="warns")
    async def warns(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        """Shows a user's current warnings."""
        await interaction.response.defer(thinking=True)
        member = member or interaction.user
        warnings = await self.get_warnings(interaction.guild.id, member)
        if warnings:
            embed = discord.Embed(title=f"Warnings for {member.display_name}", color=discord.Color.orange())
            for warning in warnings:
                embed.add_field(name=f"Warning ID: {warning['_id']}", value=f"Reason: {warning['reason']}", inline=False)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"{member.display_name} has no active warnings.")
            
    @app_commands.command(name="clear")
    async def clear(self, interaction: discord.Interaction, member: discord.Member):
        """Clears a user's active warnings."""
        await interaction.response.defer(thinking=True)
        
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data and "userWarnings" in data:
            user_warnings = [warning for warning in data["userWarnings"] if warning["user_id"] == member.id]
            if user_warnings:
                await self.db.update_one({"_id": interaction.guild.id}, {"$pull": {"userWarnings": {"user_id": member.id}}})
                await interaction.followup.send(f"{member.display_name}'s warnings have been cleared.")
            else:
                await interaction.followup.send(f"{member.display_name} has no active warnings.")
        else:
            await interaction.followup.send("The warning system is not set up or there are no warnings yet.")

    @app_commands.command(name="add")
    async def add(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Adds a warning to a user."""
        await interaction.response.defer(thinking=True)
        
        if member == interaction.user:
            return await interaction.followup.send(content="You cannot warn yourself!")
        elif member.bot:
            return await interaction.followup.send(content="You cannot give a warning to a bot!")
        elif member == interaction.guild.owner:
            return await interaction.followup.send(content="You can't give the server owner a warning!")
        
        await self.commit_warning(interaction, member, reason)

    @app_commands.command(name="remove")
    async def remove(self, interaction: discord.Interaction, member: discord.Member, warn_id: str, reason: str):
        """Remove an active warning from a user."""
        await interaction.response.defer(thinking=True)
        
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data and "userWarnings" in data:
            user_warnings = [warning for warning in data["userWarnings"] if warning["_id"] == int(warn_id) and warning["user_id"] == member.id]
            if user_warnings:
                await self.db.update_one({"_id": interaction.guild.id}, {"$pull": {"userWarnings": {"_id": int(warn_id)}}})
                await interaction.followup.send(f"Warning `{warn_id}` has been removed from {member.display_name}'s record.")
                return await self.log_warning_remove(interaction, {"user": member, "mod": interaction.user, "reason": reason})
            else:
                await interaction.followup.send(f"Warning `{warn_id}` does not exist for {member.display_name}.")
        else:
            await interaction.followup.send("The warning system is not set up or there are no warnings yet.")
        
    async def setup_warning_channel(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel]):
        if not channel:
            overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)}
            channel = await interaction.guild.create_text_channel(name="warnings-log", reason="Enable warning system.", overwrites=overwrites)
        return channel

    async def update_warning_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data['channelCreated']:
            old_channel = interaction.guild.get_channel(data['channelID'])
            await old_channel.delete()
        await self.db.update_one({"_id": interaction.guild.id}, {"$set": {"channelID": channel.id, "channelCreated": False}})
        
    async def get_warnings(self, guild_id: int, member: discord.Member):
        data = await self.db.find_one({"_id": guild_id})
        return [warning for warning in data.get("userWarnings", []) if warning["user_id"] == member.id]
        
    async def commit_warning(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Commits a warning to the database."""
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data and "userWarnings" in data:
            new_warning = {
                "_id": discord.utils.time_snowflake(datetime.datetime.utcnow()),
                "user_id": member.id,
                "moderator": str(interaction.user.id),
                "reason": reason
            }
            await self.db.update_one({"_id": interaction.guild.id}, {"$push": {"userWarnings": new_warning}}, upsert=True)
            await self.log_warning_add(interaction, {"user": member, "reason": reason, "mod": interaction.user})
            
            actionTaken = await self.check_warnings(interaction, member)
            if not actionTaken:
                await interaction.followup.send(f"{member.display_name} has been warned for: {reason}")

    async def check_warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Check the number of warnings and take appropriate action."""
        guild_data = await self.db.find_one({"_id": interaction.guild.id})
        warnings = await self.get_warnings(interaction.guild.id, member)
        
        if len(warnings) >= guild_data['kickThreshold']:
            await member.kick(reason="Exceeded warning threshold.")
            await interaction.followup.send(f"{member.display_name} has been kicked due to exceeding the warning threshold.")
            return True
        elif len(warnings) >= guild_data['banThreshold']:
            await member.ban(reason="Exceeded warning threshold.")
            await interaction.followup.send(f"{member.display_name} has been banned due to exceeding the warning threshold.")
            return True

    async def log_warning_add(self, interaction: discord.Interaction, data: dict):
        """Logs a warning to the warning log channel."""
        guild_data = await self.db.find_one({"_id": interaction.guild.id})
        if guild_data:
            channel_id = guild_data["channelID"]
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                e = discord.Embed(colour=discord.Colour.red())
                e.set_author(name=f"{data['user'].display_name} has been given a warning:", icon_url=data["user"].display_avatar)
                e.add_field(name="Moderator", value=data['mod'].mention)
                e.add_field(name="User", value=data["user"].mention)
                e.add_field(name="Reason", value=data["reason"], inline=False)
                await channel.send(embed=e)
                
    async def log_warning_remove(self, interaction: discord.Interaction, data: dict):
        guild_data = await self.db.find_one({"_id": interaction.guild.id})
        if guild_data:
            channel_id = guild_data['channelID']
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                e = discord.Embed(colour=discord.Colour.green())
                e.set_author(name=f"{data['user'].display_name} lost a warning:", icon_url=data['user'].display_avatar)
                e.add_field(name="Moderator", value=data['mod'].mention)
                e.add_field(name="Reason for Removal", value=data['reason'], inline=False)
                await channel.send(embed=e)
                
async def setup(bot: commands.Bot):
    await bot.add_cog(Warnings(bot))