from discord.ext import commands
from discord import app_commands
import logging.config
import requests
import logging.config
import logging
import discord
import yaml
import sys
import os


with open("./config.yml", "r") as f:
    config = yaml.safe_load(f)

DEV_GUILD = discord.Object(id=config["GUILD_IDS"]["DEV"])
MAIN_GUILD = discord.Object(id=config["GUILD_IDS"]["MAIN"])

class SCUFFBOT(commands.Bot):

    def __init__(self, is_dev):
        super().__init__(command_prefix="!", owner_id=169402073404669952, intents=discord.Intents.all(), application_id=(config["APPLICATION_IDS"]["DEVELOPMENT"] if is_dev else config["APPLICATION_IDS"]["PRODUCTION"]))
        self.is_dev = is_dev
        self.mode = "DEVELOPMENT" if is_dev else "PRODUCTION"
        
        
    async def setup_hook(self):
        self.setup_logger()
        await self.load_cog_manager()
        self.appinfo = await super().application_info()
        if self.appinfo.icon is not None:
            self.avatar_url = self.appinfo.icon.url
        else:
            self.avatar_url = f"https://cdn.discordapp.com/embed/avatars/{int(self.user.discriminator) % 5}.png"
        
    def setup_logger(self):
        logging.config.dictConfig(config["LOGGING"])
        self.logger = logging.getLogger(__name__)
        for handler in logging.getLogger().handlers:
            if handler.name == "file" and os.path.isfile('logs/latest.log'):
                handler.doRollover()
        logging.getLogger('discord').setLevel(logging.DEBUG)

    async def load_cog_manager(self):
        await self.load_extension("lib.cogs.Cogs")

    def run(self):
        super().run(config["TOKENS"][self.mode], log_handler=None)

    def create_embed(self, description=None, **kwargs):
        embed = discord.Embed(title=None, description=description if description else None, colour=kwargs.get("colour", 0xDC3145), timestamp=discord.utils.utcnow())
        if (title := kwargs.get("title", None)) is not None:
            embed.set_author(name=title , icon_url=self.avatar_url)
        return embed

    #  Doesn't work, need to look into
    @staticmethod
    def has_permissions(**perms):
        original = app_commands.checks.has_permissions(**perms)
        async def extended_check(interaction):
            if interaction.guild is None:
                return False
            return interaction.user.id in config["DEVELOPERS"] or (interaction.user.id == 169402073404669952) or await original.predicate(interaction)
        return app_commands.check(extended_check)

    @staticmethod
    def is_developer(interaction: discord.Interaction):
        return interaction.user.id in config["Developers"]

    async def on_ready(self):
        self.logger.info(
            f"Connected on {self.user.name} ({self.mode}) | d.py v{str(discord.__version__)}"
        )

    async def on_interaction(self, interaction):
        self.logger.info(f"[COMMAND] [{interaction.guild} // {interaction.guild.id}] {interaction.user} ({interaction.user.id}) used command {interaction.command.name}")

    async def on_message(self, message):
        await self.wait_until_ready()
        if(isinstance(message.channel, discord.DMChannel) and message.author.id == self.owner_id):
            message_components = message.content.lower().split(" ")
            match message_components[0]:
                case "sync":
                    if len(message_components) == 2:
                        result = await self.tree.sync(guild=discord.Object(id=int(message_components[1])))
                    else:
                        result = await self.tree.sync()
                    await message.channel.send(f"Synced {[command.name for command in result]}")
