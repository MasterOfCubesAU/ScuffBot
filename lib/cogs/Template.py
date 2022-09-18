from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from lib.bot import config, logger, SCUFFBOT, DEV_GUILD
from typing import Literal, Union, Optional
import discord



class Template(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[COG] Loaded {self.__class__.__name__}")
        

async def setup(bot):
    await bot.add_cog(Template(bot))
