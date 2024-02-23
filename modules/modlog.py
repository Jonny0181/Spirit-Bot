import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal, List

class Modlog(commands.GroupCog, name="modlog"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.db.modlog
        
    @app_commands.command(name="enable")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel]):
        """Enables the modlog system."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        data = await self.db.find_one({"_id": interaction.guild.id})
        
        if data:
            if channel is None:
                if not data['channelCreated']:
                    overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)}
                    new_channel = await interaction.guild.create_text_channel(name="mod-log", reason="Enable modlog system.", overwrites=overwrites)
                    
                    await self.db.update_one({"_id": interaction.guild.id}, {"$set": {"channelID": new_channel.id, "channelCreated": True}})
                    return await interaction.followup.send(content=f"The modlog channel has been updated to {new_channel.mention}!")
                else:
                    return await interaction.followup.send(content=f"The modlog system is already enabled in <#{data['channelID']}>!")
            else:
                if channel.id == data['channelID']:
                    return await interaction.followup.send(content="The modlog is already set to send logs to this channel!")
                else:
                    if data['channelCreated']:
                        channel_to_delete = await interaction.guild.fetch_channel(data['channelID'])
                        await channel_to_delete.delete()
                        
                    await self.db.update_one({"_id": interaction.guild.id}, {"$set": {"channelID": channel.id, "channelCreated": False}})
                    return await interaction.followup.send(content=f"The modlog channel has been updated to {channel.mention}!")
        else:
            if channel is None:
                channelCreated = True
                overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)}
                new_channel = await interaction.guild.create_text_channel(name="mod-log", reason="Enable modlog system.", overwrites=overwrites)
            else:
                channelCreated = False
                new_channel = channel
                
            data = {"_id": interaction.guild.id, "enabled": True, "channelID": new_channel.id, "channelCreated": channelCreated, "enabledSettings": []}
            await self.db.insert_one(data)
            return await interaction.followup.send(
                content=f"The modlog has been enabled. Logs will be posted to {new_channel.mention}. Don't forget to toggle on some settings for logs to begin! Use `/modlog toggle` to enable some.")
        
    @app_commands.command(name="disable")
    async def disable(self, interaction: discord.Interaction):
        """Disables the modlog system."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        data = await self.db.find_one({"_id": interaction.guild.id})
        if data:
            if data['channelCreated']:
                channel = await interaction.guild.fetch_channel(data['channelID'])
                await channel.delete()
                await interaction.followup.send(content=f"Modlog has been disabled and channel `{channel.name}` has been deleted!")
            else:
                await interaction.followup.send(content="Modlog has been disabled!")
            
            return await self.db.delete_one({"_id": interaction.guild.id})
        else:
            return await interaction.followup.send(content="Modlog is not enabled in this server!")
        
    @app_commands.command(name="toggle")
    async def toggle(self, interaction: discord.Interaction, setting: str):
        """Toggles a modlog setting on or off."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        data = await self.db.find_one({"_id": interaction.guild.id})
        
        if data:
            if setting in data['enabledSettings']:
                await self.db.update_one({"_id": interaction.guild.id}, {"$pull": {"enabledSettings": setting}})
                return await interaction.followup.send(content=f"Setting `{setting}` has been disabled!")
            else:
                await self.db.update_one({"_id": interaction.guild.id}, {"$push": {"enabledSettings": setting}})
                return await interaction.followup.send(content=f"Setting `{setting}` has been enabled!")
        else:
            return interaction.followup.send(content="Modlog is not enabled on this server try using `/modlog enable` first!")
        
    @toggle.autocomplete('setting')
    async def setting_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        settings = ['Messages', 'Leave', 'Join', 'Channel', 'Guild', 'Voice', 'Emojis', 'Stickers', 'Invites', 'Bans', 'Roles', 'Events', 'Stages', 'Threads']
        return [
            app_commands.Choice(name=setting, value=setting)
            for setting in settings if current.lower() in setting.lower()
        ]
        
    # GUILD
    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        ...
        
    # EMOJIS
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: discord.Emoji, after: discord.Emoji):
        ...
        
    # STICKERS
    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild: discord.Guild, before: discord.GuildSticker, after: discord.GuildSticker):
        ...
        
    #INVITES
    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        ...
        
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        ...
        
    # INTEGERATIONS
    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild: discord.Guild):
        ...
        
    # MEMBERS
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ...
        
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        ...
        
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        ...
        
    # BANS
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        ...
        
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        ...
        
    # MESSAGES
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        ...
        
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        ...
        
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: List[discord.Message]):
        ...
        
    # ROLES
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        ...
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        ...
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        ...
        
    # EVENTS
    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: discord.ScheduledEvent):
        ...
        
    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event: discord.ScheduledEvent):
        ...
        
    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent):
        ...
        
    @commands.Cog.listener()
    async def on_scheduled_event_user_add(self, event: discord.ScheduledEvent, user: discord.User):
        ...
        
    @commands.Cog.listener()
    async def on_scheduled_event_user_remove(self, event: discord.ScheduledEvent, user: discord.User):
        ...
        
    # STAGES
    @commands.Cog.listener()
    async def on_stage_instance_create(self, stage: discord.StageInstance):
        ...
        
    @commands.Cog.listener()
    async def on_stage_instance_delete(self, stage: discord.StageInstance):
        ...
        
    @commands.Cog.listener()
    async def on_stage_instance_update(self, before: discord.StageInstance, after: discord.StageInstance):
        ...
        
    # THREADS
    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        ...
        
    @commands.Cog.listener()
    async def on_thread_join(self, thread: discord.Thread):
        ...
        
    @commands.Cog.listener()
    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        ...
        
    @commands.Cog.listener()
    async def on_thread_remove(self, thread: discord.Thread):
        ...
        
    @commands.Cog.listener()
    async def on_thread_delete(self, thread: discord.Thread):
        ...
        
    @commands.Cog.listener()
    async def on_thread_member_join(self, thread: discord.Thread):
        ...
        
    @commands.Cog.listener()
    async def on_thread_member_remove(self, thread: discord.Thread):
        ...
        
    # VOICE
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        ...
        
    @enable.error
    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        print(interaction, error)
        try:
            return await interaction.response.send_message(error, ephemeral=True)
        except Exception as e:
            print(e)
            return await interaction.followup.send(error)
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Modlog(bot))