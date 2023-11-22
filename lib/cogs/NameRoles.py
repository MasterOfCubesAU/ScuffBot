from discord.ext import commands
import discord
import logging
from lib.bot import config

class NameRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.roles = config["NAME_ROLES"]

    async def cog_load(self):
        self.logger.info(f"[COG] Loaded {self.__class__.__name__}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles and role.id in self.roles]
            if added_roles:
                name = after.display_name.split(" | ")[0]
                rank = self.roles[added_roles[0].id]
                await after.edit(nick=f"{name} | {rank}")

async def setup(bot):
    await bot.add_cog(NameRoles(bot))
