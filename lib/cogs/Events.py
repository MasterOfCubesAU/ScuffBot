from discord.ext import commands
from discord import app_commands, Interaction, TextStyle, SelectOption, DMChannel
from discord.ui import View, TextInput, Select, Modal
import discord
import logging
import re
from lib.bot import DEV_GUILD
from typing import Optional
from utils.DBHandler import DBHandler
import base64

class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def cog_load(self):
        self.logger.info(f"[COG] Loaded {self.__class__.__name__}")

    async def addListener(self, message: discord.Message):
        LISTENER_ID = base64.b64encode(str(message.id).encode('utf8'))[:8]
        DBHandler.execute("INSERT INTO Events (ID, MessageID, ChannelID) VALUES (?, ?, ?)", LISTENER_ID, message.id, message.channel.id)
        await message.add_reaction("✅")

        
    EVENT = app_commands.Group(name="event", description="Manage ScuffCord events", guild_ids=[DEV_GUILD.id])

    @EVENT.command(name="create", description="Create a ScuffCord event")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(
        link="The link to the event message"
    )
    async def create(self, interaction: Interaction, link: Optional[str]):
        if link is not None:
            result = matches.groups() if (matches := re.match("^https:\/\/discord.com\/channels\/(.*)\/(.*)\/(.*)$", link)) else None
            if result is None:
                return await interaction.response.send_message(embed=self.bot.create_embed("The link provided is not a valid discord message link.", title="SCUFFBOT EVENTS"), ephemeral=True)
            channel = interaction.guild.get_channel(int(result[-2]))
            message = await channel.fetch_message(int(result[-1]))
            await self.addListener(message)
            return await interaction.response.send_message(embed=interaction.client.create_embed("Event has successfully been created.", title="SCUFFBOT EVENTS"), ephemeral=True)
        await interaction.response.send_modal(EventModal(self))
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction = payload.emoji
        if not isinstance(channel, DMChannel):
            message_id = payload.message_id
            guild = self.bot.get_guild(channel.guild.id)
            user = guild.get_member(payload.user_id)
            if not user.bot:
                if message_id in DBHandler.column("SELECT MessageID FROM Events"):
                    DBHandler.execute("INSERT INTO Registrants (ID, Registrant) VALUES (?, ?)", base64.b64encode(str(message_id).encode('utf8'))[:8], user.id)
                    registerSuccessEmbed = self.bot.create_embed("Thankyou! Your expression of interest has been confirmed. A confirmation message will be sent prior to the event date.\n\n**If you change your mind, you can opt-out by un-reacting to the event message.**\n", colour=0x00ff00)
                    await user.send(embed=registerSuccessEmbed)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction = payload.emoji
        if not isinstance(channel, DMChannel):
            if str(reaction) == "✅":
                message_id = payload.message_id
                guild = self.bot.get_guild(channel.guild.id)
                user = guild.get_member(payload.user_id)
                if not user.bot:
                    if message_id in DBHandler.column("SELECT MessageID FROM Events"):
                        DBHandler.execute("DELETE FROM Registrants WHERE Registrant = ?", user.id)
                        optOutEmbed = self.bot.create_embed("You have successfully opted out of the event.", colour=0x00ff00)
                        await user.send(embed=optOutEmbed)

async def setup(bot):
    await bot.add_cog(Events(bot))

class EventModal(Modal, title="Event Creation"):
    event_message_txt = TextInput(label='Event Announcement Message', style=TextStyle.paragraph, placeholder="We are welcoming all members to a ScuffCord event! blah blah blah...", required=True)

    def __init__(self, events: Events):
        self.events = events
        super().__init__()

    async def on_submit(self, interaction: Interaction):
        event_message = await interaction.channel.send(embed=interaction.client.create_embed(self.event_message_txt.value))
        await self.events.addListener(event_message)
        await interaction.response.send_message(embed=interaction.client.create_embed("Event has successfully been created.", title="SCUFFBOT EVENTS"), ephemeral=True)