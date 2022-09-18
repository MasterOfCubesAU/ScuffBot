from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from lib.bot import config, logger, SCUFFBOT, DEV_GUILD
from typing import Literal, Union, Optional
import discord

class Tournaments(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.create_channel_id = config["TOURNAMENT"][self.bot.mode]["CHANNEL"]
        self.category = self.bot.get_channel(config["TOURNAMENT"][self.bot.mode]["CATEGORY"])
        self.channels = []

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[COG] Loaded {self.__class__.__name__}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None and after.channel is not None and before.channel == after.channel:
            return
        if member.bot:
            return

        if before.channel in self.channels and len(before.channel.members) == 0:
            await self.deleteTournamentChannel(before.channel)
        if after.channel.id == self.create_channel_id:
            voice_channel = await self.createTournamentChannel(member)
            await member.move_to(voice_channel)
            
            
    async def createTournamentChannel(self, member):
        voice_channel = await member.guild.create_voice_channel(name=f"RL 3s #{1 if len(self.channels) == 0 else int(self.channels[-1].name.split('#')[-1]) + 1}", user_limit=3, category=self.category, reason=f"{member} created a 3s voice channel.")
        self.channels.append(voice_channel)
        return voice_channel
            
    async def deleteTournamentChannel(self, channel):
        await channel.delete(reason=f"{channel.name} empty.")
        self.channels.remove(channel)

    

        

async def setup(bot):
    await bot.add_cog(Tournaments(bot))
