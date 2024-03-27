import discord
import secrets
import string
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
        
class ClearWarningsModal(discord.ui.Modal):
    def __init__(self, clear_warnings, member: discord.Member):
        super().__init__(title="Clear Warnings")
        self.clear_warnings = clear_warnings
        self.member = member
        
        self.reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Reason for clearing warnings...",
            required=True,
            max_length=100
        )
        self.add_item(self.reason)
        
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await self.clear_warnings(interaction, self.member, self.reason.value)

class Warnings(commands.GroupCog, name="warnings"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.warnings
        self.history_db = self.bot.db.warning_history

        @bot.tree.context_menu(name="Add Warning")
        async def add_warning(interaction: discord.Interaction, member: discord.Member):
            return await interaction.response.send_modal(AddWarningModal(self.commit_warning, member))
        
        @bot.tree.context_menu(name="Active Warnings")
        async def active_warnings(interaction: discord.Interaction, member: discord.Member):
            await interaction.response.defer(thinking=True)
            member = member or interaction.user
            warnings = await self.get_warnings(interaction.guild.id, member)
            if warnings:
                embed = discord.Embed(color=discord.Color.orange())
                description = ""
                for warning in warnings:
                    description += f"**Warning ID:** {warning['_id']}\n**Reason:** {warning['reason']}\n\n"
                embed.description = description
                embed.set_thumbnail(url=member.display_avatar)
                embed.set_author(name=f"Active Warnings for {member.display_name}", icon_url=member.display_avatar)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"{member.display_name} has no active warnings.")
                
        @bot.tree.context_menu(name="Clear Warnings")
        async def clear_warnings_context(interaction: discord.Interaction, member: discord.Member):
            warnings = await self.get_warnings(interaction.guild.id, member)
            if warnings:
                return await interaction.response.send_modal(ClearWarningsModal(self.clear_warnings, member))
            else:
                await interaction.response.send_message(f"{member.display_name} has no active warnings.")
                
        @bot.tree.context_menu(name="Warnings History")
        async def warns_history(interaction: discord.Interaction, member: discord.Member):
            await interaction.response.defer(thinking=True)
            
            warnings = await self.get_history_warnings(interaction.guild.id, member)
            if warnings:
                embed = discord.Embed(color=discord.Color.orange())
                description = ""
                for warning in warnings:
                    remover_id = warning.get('remover_id', 'Unknown')
                    removed_at = warning.get('removed_at', 'Unknown')
                    removal_info = f"\n**Removed by:** <@{remover_id}> at {removed_at.strftime('%Y-%m-%d %H:%M')}"
                    description += f"**Warning ID:** {warning['_id']}\n**Reason:** {warning['reason']}{removal_info}\n\n"
                embed.description = description
                embed.set_thumbnail(url=member.display_avatar)
                embed.set_author(name=f"Warning History for {member.display_name}", icon_url=member.display_avatar)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"{member.display_name} has no historical warnings.")

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
        
    @app_commands.command(name="active")
    async def active(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        """Shows a user's current warnings."""
        await interaction.response.defer(thinking=True)
        member = member or interaction.user
        warnings = await self.get_warnings(interaction.guild.id, member)
        if warnings:
            embed = discord.Embed(color=discord.Color.orange())
            description = ""
            for warning in warnings:
                description += f"**Warning ID:** {warning['_id']}\n**Reason:** {warning['reason']}\n\n"
            embed.description = description
            embed.set_thumbnail(url=member.display_avatar)
            embed.set_author(name=f"Active Warnings for {member.display_name}", icon_url=member.display_avatar)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"{member.display_name} has no active warnings.")
            
    @app_commands.command(name="clear")
    async def clear(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Clears a user's active warnings."""
        await interaction.response.defer(thinking=True)
            
        await self.clear_warnings(interaction, member, reason)

    @app_commands.command(name="add")
    async def add(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Adds a warning to a user."""
        await interaction.response.defer(thinking=True)
        await self.commit_warning(interaction, member, reason)

    @app_commands.command(name="remove")
    async def remove(self, interaction: discord.Interaction, member: discord.Member, warn_id: str, reason: str):
        """Remove an active warning from a user."""
        await interaction.response.defer(thinking=True)
        
        success = await self.remove_warning(interaction.guild.id, member.id, warn_id, reason, interaction.user.id)
        if success:
            await interaction.followup.send(f"Warning `{warn_id}` has been removed from {member.display_name}'s record.")
            await self.log_warning_remove(interaction, {"user": member, "mod": interaction.user, "reason": reason, 'id': warn_id})
        else:
            await interaction.followup.send(f"Warning `{warn_id}` does not exist for {member.display_name}.")
            
    @app_commands.command(name="history")
    async def history(self, interaction: discord.Interaction, member: discord.Member):
        """View the historical warnings for a user."""
        await interaction.response.defer(thinking=True)
        
        warnings = await self.get_history_warnings(interaction.guild.id, member)
        if warnings:
            embed = discord.Embed(color=discord.Color.orange())
            description = ""
            for warning in warnings:
                remover_id = warning.get('remover_id', 'Unknown')
                removed_at = warning.get('removed_at', 'Unknown')
                removal_info = f"\n**Removed by:** <@{remover_id}> at {removed_at.strftime('%Y-%m-%d %H:%M')}"
                description += f"**Warning ID:** {warning['_id']}\n**Reason:** {warning['reason']}{removal_info}\n\n"
            embed.description = description
            embed.set_thumbnail(url=member.display_avatar)
            embed.set_author(name=f"Warning History for {member.display_name}", icon_url=member.display_avatar)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"{member.display_name} has no historical warnings.")
        
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

    async def get_history_warnings(self, guild_id: int, member: discord.Member):
        """Retrieve historical warnings for a specific member."""
        data = await self.history_db.find_one({"_id": guild_id})
        if data:
            user_warnings = data.get("userWarnings", [])
            return [warning for warning in user_warnings if warning["user_id"] == member.id]
        return []

    async def commit_warning(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Commits a warning to the database."""
        
        if member == interaction.user:
            return await interaction.followup.send("You cannot warn yourself!", ephemeral=True)
        elif member.bot:
            return await interaction.followup.send("You cannot give a warning to a bot!", ephemeral=True)
        elif member == interaction.guild.owner:
            return await interaction.followup.send("You can't give the server owner a warning!", ephemeral=True)
        elif member.guild_permissions.administrator:
            return await interaction.followup.send("You can't give an admin a warning!", ephemeral=True)
        elif member.top_role.position >= interaction.guild.me.top_role.position:
            return await interaction.followup.send("I cannot give that user a warning since they have the same rank or a higher rank than me!")
        
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data and "userWarnings" in data:
            identifier = self.generate_short_id()
            new_warning = {
                "_id": identifier,
                "user_id": member.id,
                "moderator": str(interaction.user.id),
                "reason": reason
            }
            await self.db.update_one({"_id": interaction.guild.id}, {"$push": {"userWarnings": new_warning}}, upsert=True)
            await self.log_warning_add(interaction, {"user": member, "reason": reason, "mod": interaction.user, 'id': identifier})
            
            action_taken = await self.check_warnings(interaction, member)
            if not action_taken:
                await interaction.followup.send(f"{member.display_name} has been warned for: {reason}")
                
    async def remove_warning(self, guild_id: int, member_id: int, warn_id: str, reason: str, remover_id: int):
        """Remove a warning from the active warnings to historical warnings."""
        data = await self.db.find_one({"_id": guild_id})
        if data and "userWarnings" in data:
            user_warnings = data["userWarnings"]
            for warning in user_warnings:
                if warning["_id"] == warn_id and warning["user_id"] == member_id:
                    # Include removal timestamp and remover ID
                    warning["removed_at"] = datetime.datetime.utcnow()
                    warning["remover_id"] = remover_id
                    await self.db.update_one({"_id": guild_id}, {"$pull": {"userWarnings": {"_id": warn_id}}})
                    # Move the removed warning to the historical warnings collection
                    await self.history_db.update_one({"_id": guild_id}, {"$push": {"userWarnings": warning}}, upsert=True)
                    return True
        return False

    async def check_warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Check the number of warnings and take appropriate action."""
        guild_data = await self.db.find_one({"_id": interaction.guild.id})
        if not guild_data:
            return False
        
        warnings = await self.get_warnings(interaction.guild.id, member)
        if len(warnings) >= guild_data.get('kickThreshold', 3):
            if interaction.guild.me.guild_permissions.kick_members:
                await member.kick(reason="Exceeded warning threshold.")
                await interaction.followup.send(f"{member.display_name} has been kicked due to exceeding the warning threshold.")
                return True
            else:
                await interaction.followup.send("I don't have permission to kick members.")
        elif len(warnings) >= guild_data.get('banThreshold', 5):
            if interaction.guild.me.guild_permissions.ban_members:
                await member.ban(reason="Exceeded warning threshold.")
                await interaction.followup.send(f"{member.display_name} has been banned due to exceeding the warning threshold.")
                return True
            else:
                await interaction.followup.send("I don't have permission to ban members.")
        return False

    async def clear_warnings(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """Clears a user's active warnings."""
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data and "userWarnings" in data:
            user_warnings = [warning for warning in data["userWarnings"] if warning["user_id"] == member.id]
            if user_warnings:
                current_time = datetime.datetime.utcnow()
                for warning in user_warnings:
                    # Include clearance timestamp and clearer ID
                    warning["removed_at"] = current_time
                    warning["remover_id"] = interaction.user.id
                    # Move the cleared warnings to historical warnings
                    await self.history_db.update_one({"_id": interaction.guild.id}, {"$push": {"userWarnings": warning}}, upsert=True)
                await self.db.update_one({"_id": interaction.guild.id}, {"$pull": {"userWarnings": {"user_id": member.id}}})
                await interaction.followup.send(f"{member.display_name}'s warnings have been cleared.")
                await self.log_warning_clear(interaction, {"mod": interaction.user, "user": member, "reason": reason})
            else:
                await interaction.followup.send(f"{member.display_name} has no active warnings.")
        else:
            await interaction.followup.send("The warning system is not set up or there are no warnings yet.")

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
                e.add_field(name="Warning ID", value=data["id"])
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
                e.add_field(name="Warning ID", value=data['id'])
                e.add_field(name="Reason for Removal", value=data['reason'], inline=False)
                await channel.send(embed=e)
                
    async def log_warning_clear(self, interaction: discord.Interaction, data: dict):
        guild_data = await self.db.find_one({"_id": interaction.guild.id})
        if guild_data:
            channel_id = guild_data['channelID']
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                e = discord.Embed(colour=discord.Colour.green())
                e.set_author(name=f"{data['user'].display_name} warnings have been cleared:", icon_url=data['user'].display_avatar)
                e.add_field(name="Moderator", value=data['mod'].mention)
                e.add_field(name="Reason for Clear", value=data['reason'], inline=False)
                await channel.send(embed=e)
        
    def generate_short_id(self):
        """Generates a 6-character identifier."""
        letters = string.ascii_uppercase
        digits = string.digits
        return ''.join(secrets.choice(letters) for _ in range(3)) + '-' + ''.join(secrets.choice(digits) for _ in range(3))
                
async def setup(bot: commands.Bot):
    await bot.add_cog(Warnings(bot))