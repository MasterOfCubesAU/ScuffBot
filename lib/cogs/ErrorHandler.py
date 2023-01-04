from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from lib.bot import config, SCUFFBOT, DEV_GUILD
from typing import Literal, Union, Optional
import discord
import logging

import traceback



class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error
        self.bot.on_error = self.on_error
        self.logger = logging.getLogger(__name__)

    async def cog_load(self):
        self.logger.info(f"[COG] Loaded {self.__class__.__name__}")
        
    async def on_app_command_error(self, interaction, error):
        embed = self.bot.create_embed("An unexpected error has occurred." , title="SCUFFBOT ERROR", colour=0xFF0000)
        embed.add_field(name="ERROR:", value="> {}\n\nIf this error is a regular occurrence, please contact {}. This error has been logged.".format(str(error), self.appinfo.owner.mention), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        self.logger.error(f"[ERROR] App Command Error: {error}")
        traceback.print_exc()
    
    async def on_error(self, event):       
        self.logger.error(f"[ERROR] Unhandled Error: {event}")
        traceback.print_exc()




async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
