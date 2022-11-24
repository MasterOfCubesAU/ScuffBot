from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from lib.bot import config, SCUFFBOT, DEV_GUILD
from typing import Literal, Union, Optional
import discord
import logging

import re

class Tournaments(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.two_channel = config["TOURNAMENT"][self.bot.mode]["2_CHANNEL"]
        self.threes_channel = config["TOURNAMENT"][self.bot.mode]["3_CHANNEL"]
        self.channels = []
        self.logger = logging.getLogger(__name__)

    async def cog_load(self):
        self.logger.info(f"[COG] Loaded {self.__class__.__name__}")

    @commands.Cog.listener()
    async def on_ready(self):
        self.category = self.bot.get_channel(config["TOURNAMENT"][self.bot.mode]["CATEGORY"])
        await self.getLostChannels()

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
            
    async def getLostChannels(self):
        for channel in self.category.channels:
            if re.match("^RL [0-9]'s #[0-9]+$", channel.name):
                if len(channel.members) == 0:
                    await self.deleteTournamentChannel(channel)
                else:
                    self.logger.info(f"[TOURNAMENTS] Found lost channel {channel.name}")
                    self.channels.append(channel)

    async def createTournamentChannel(self, member, limit):
        channels = [channel for channel in self.channels if re.match(f"^RL {limit}'s #[0-9]+$", channel.name)]
        channel_num = 1 if len(channels) == 0 else max([int(channel.name.split('#')[-1]) for channel in channels]) + 1
        voice_channel = await member.guild.create_voice_channel(name=f"RL {limit}'s #{channel_num}", user_limit=limit, category=self.category, reason=f"{member} created a {limit}'s voice channel.")
        self.channels.append(voice_channel)
        return voice_channel
            
    async def deleteTournamentChannel(self, channel):
        await channel.delete(reason=f"{channel.name} empty.")
        self.channels.remove(channel)

async def setup(bot):
    await bot.add_cog(Tournaments(bot))
