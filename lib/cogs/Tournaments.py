from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from lib.bot import config, logger, SCUFFBOT, DEV_GUILD
from typing import Literal, Union, Optional
import discord

class Tournaments(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.two_channel = config["TOURNAMENT"][self.bot.mode]["2_CHANNEL"]
        self.threes_channel = config["TOURNAMENT"][self.bot.mode]["3_CHANNEL"]
        self.channels = []

    @commands.Cog.listener()
    async def on_ready(self):
        self.category = self.bot.get_channel(config["TOURNAMENT"][self.bot.mode]["CATEGORY"])
        logger.info(f"[COG] Loaded {self.__class__.__name__}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is not None and after.channel is not None and before.channel == after.channel:
            return
        if member.bot:
            return

        #Channel deletion
        if before.channel in self.channels and len(before.channel.members) == 0:
            await self.deleteTournamentChannel(before.channel)

        #Channel creation
        if after.channel.id == self.two_channel:
            voice_channel = await self.createTournamentChannel(member, 2)
            await member.move_to(voice_channel)
        elif after.channel.id == self.threes_channel:
            voice_channel = await self.createTournamentChannel(member, 3)
            await member.move_to(voice_channel)
            
    async def createTournamentChannel(self, member, limit):
        channel_num = 1 if len(self.channels) == 0 else int([channel for channel in self.channels if f"{limit}'s" in channel.name][-1].name.split('#')[-1]) + 1
        voice_channel = await member.guild.create_voice_channel(name=f"RL {limit}'s #{channel_num}", user_limit=limit, category=self.category, reason=f"{member} created a {limit}'s voice channel.")
        self.channels.append(voice_channel)
        return voice_channel
            
    async def deleteTournamentChannel(self, channel):
        await channel.delete(reason=f"{channel.name} empty.")
        self.channels.remove(channel)

async def setup(bot):
    await bot.add_cog(Tournaments(bot))
