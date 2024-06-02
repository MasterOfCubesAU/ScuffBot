import asyncio
from discord.ext import commands
from discord.ui import Button, View, UserSelect
from discord import app_commands, Interaction, NotFound, PermissionOverwrite, Status, Object
from lib.bot import config, DB
from typing import Literal, Union, Optional
import discord
import logging
import random
from enum import Enum

PARTY_SIZE = 2

class SixMansState(Enum):
    CAPTAIN_1 = 1
    CAPTAIN_2 = 2
    PLAYING = 3
    SCORE_UPLOAD = 4


class UserDropdown(UserSelect):
    def __init__(self, users, amount):
        super().__init__(placeholder=f"Choose {amount} {'member' if amount == 1 else 'members'} to be on your team", min_values=1, max_values=amount)

class DropdownView(View):
    def __init__(self, users, amount):
        super().__init__(timeout=None)
        dropdown = UserDropdown(users, amount)
        self.add_item(dropdown)
        
        submit_button = discord.ui.Button(label="Submit", style=discord.ButtonStyle.green)
        submit_button.callback = self.submit_button_callback
        self.add_item(submit_button)

class SixMansPrompt(View):
    def __init__(self, bot, lobby_id):
        super().__init__(timeout=None)
        self.state = SixMansState.CAPTAIN_1
        self.bot = bot
        self.lobby_id = lobby_id
        self.captain_1, self.captain_2 = self.generate_captains()
        self.updateOptions()

    async def delete_lobby(self):
        lobby_details = DB.record("SELECT * FROM LobbyDetails WHERE LobbyID = ?", self.lobby_id)
        lobby_name = f"SixMans #{self.lobby_id}"
        await self.bot.get_channel(int(lobby_details[2])).guild.get_role(lobby_details[3]).delete(reason=f"{lobby_name} finished/cancelled")
        await self.bot.get_channel(lobby_details[1]).delete(reason=f"{lobby_name} finished/cancelled")
        await self.bot.get_channel(lobby_details[2]).delete(reason=f"{lobby_name} finished/cancelled")
        DB.execute("DELETE FROM Lobbies WHERE LobbyID = ?", self.lobby_id)

    def generate_captains(self):
        lobby_users = [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM LobbyUsers WHERE LobbyID = ? AND Type = 0", self.lobby_id)]
        captain_one = lobby_users.pop(random.randint(0, len(lobby_users)-1))
        captain_two = lobby_users.pop(random.randint(0, len(lobby_users)-1))
        DB.execute("UPDATE LobbyUsers SET Type = 1 WHERE UserID = ?", captain_one.id)
        DB.execute("UPDATE LobbyUsers SET Type = 2 WHERE UserID = ?", captain_two.id)
        return captain_one, captain_two

    def generate_embed(self):
        match self.state:
            case SixMansState.CAPTAIN_1:
                embed = self.bot.create_embed("SCUFFBOT SIX MANS", f"Hello! Welcome to {self.bot.user.mention} Six Mans!\n\nBelow, you will be able to see the current team configuration.\nTo begin, the first captain needs to select **ONE** member to join their team.", None)
                embed.add_field(name=f"Captain {self.captain_1}", value="\n".join([f"• {member}" for member in [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM LobbyUsers WHERE LobbyID = ? AND Team = 1", self.lobby_id)]]), inline=True)
                embed.add_field(name=f"Captain -", value="\n".join([f"• {member}" for member in ["-"]*3]))
                return embed
            case SixMansState.CAPTAIN_2:
                embed = self.bot.create_embed("SCUFFBOT SIX MANS", f"Hello! Welcome to {self.bot.user.mention} Six Mans!\n\nBelow, you will be able to see the current team configuration.\nNow, the second captain needs to select **TWO** members to join their team.", None)
                embed.add_field(name=f"Captain {self.captain_1}", value="\n".join([f"• {member}" for member in [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM LobbyUsers WHERE LobbyID = ? AND Team = 1", self.lobby_id)]]), inline=True)
                embed.add_field(name=f"Captain {self.captain_2}", value="\n".join([f"• {member}" for member in [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM LobbyUsers WHERE LobbyID = ? AND Team = 2", self.lobby_id)]]), inline=True)
                return embed
            case SixMansState.PLAYING:
                embed = self.bot.create_embed("SCUFFBOT SIX MANS", f"Hello! Welcome to {self.bot.user.mention} Six Mans!\n\nPlease nominate an individual to host a private match. The team configuration can be seen below. Once you have finished your match, click on the **Finish game** button below.", None)
                embed.add_field(name=f"Captain {self.captain_1}", value="\n".join([f"• {member}" for member in [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM LobbyUsers WHERE LobbyID = ? AND Team = 1", self.lobby_id)]]), inline=True)
                embed.add_field(name=f"Captain {self.captain_2}", value="\n".join([f"• {member}" for member in [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM LobbyUsers WHERE LobbyID = ? AND Team = 2", self.lobby_id)]]), inline=True)
                return embed
            case SixMansState.SCORE_UPLOAD:
                return self.bot.create_embed("SCUFFBOT SIX MANS", f"Hello! Welcome to {self.bot.user.mention} Six Mans!\n\nThis section is still under construction.", None)
            case _:
                 return self.bot.create_embed("SCUFFBOT SIX MANS", f"Hello! Welcome to {self.bot.user.mention} Six Mans!\n\nrip.", None)
            
    def updateOptions(self):
        self.clear_items()
        match self.state:
            case SixMansState.CAPTAIN_1:
                choose_button = Button(label="Choose Member", style=discord.ButtonStyle.green, row=1)
                choose_button.callback = self.choose_button_callback
                self.add_item(end_button)
                cancel_button = Button(label="Cancel Game", style=discord.ButtonStyle.grey, row=1)
                cancel_button.callback = self.cancel_button_callback
                self.add_item(cancel_button)
                return
            case SixMansState.CAPTAIN_2:
                choose_button = Button(label="Choose Members", style=discord.ButtonStyle.green, row=1)
                choose_button.callback = self.choose_button_callback
                self.add_item(end_button)
                cancel_button = Button(label="Cancel Game", style=discord.ButtonStyle.grey, row=1)
                cancel_button.callback = self.cancel_button_callback
                self.add_item(cancel_button)
                return
            case SixMansState.PLAYING:
                end_button = Button(label="End Game", style=discord.ButtonStyle.red, row=1)
                end_button.callback = self.end_game
                self.add_item(end_button)
                return
            case SixMansState.SCORE_UPLOAD:
                upload_scores_button = Button(label="Upload Scores", style=discord.ButtonStyle.green, row=1)
                upload_scores_button.callback = self.upload_scores_callback
                self.add_item(upload_scores_button)
                return

    async def update_view(self, embed=None):
        await self.interaction.edit_original_response(embed=embed or self.generate_embed(), view=self)

    async def cancel_button_callback(self):
        await self.delete_lobby()
           


class SixMans(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.queue = list()
        self.category = self.bot.get_channel(config["SIX_MAN"]["CATEGORY"])

    async def cog_load(self):
        self.logger.info(f"[COG] Loaded {self.__class__.__name__}")

    async def checkQueue(self):
        if len(self.queue) == PARTY_SIZE:
            party = self.queue[:PARTY_SIZE]
            del self.queue[:PARTY_SIZE]
            lobby_id = await self.createParty(party)
            await self.startSixMans(lobby_id)
            
    async def createParty(self, members):
        DB.execute("INSERT INTO Lobbies (ID) VALUES (NULL)")
        
        lobby_id = DB.field("SELECT last_insert_rowid() FROM Lobbies")
        lobby_name = f"SixMans #{lobby_id}"
        
        lobby_role = await members[0].guild.create_role(name=lobby_name, reason=f"{lobby_name} created")
        vc_perms = {lobby_role: PermissionOverwrite(speak=True,connect=True,view_channel=True), members[0].guild.default_role: PermissionOverwrite(view_channel=True, connect=False)}
        text_perms = {lobby_role: PermissionOverwrite(read_messages=True, send_messages=True), members[0].guild.default_role: PermissionOverwrite(read_messages=False)}
        voice_channel = await members[0].guild.create_voice_channel(name=lobby_name, overwrites=vc_perms, category=self.category, reason=f"{lobby_name} created")
        text_channel = await members[0].guild.create_text_channel(name=f"six-mans-{lobby_id}", overwrites=text_perms, category=self.category, reason=f"{lobby_name} created")
        lobby_invite_link = str(await voice_channel.create_invite(reason=f"{lobby_name} created"))
        DB.execute("INSERT INTO LobbyDetails (LobbyID, VoiceChannelID, TextChannelID, RoleID) VALUES (?, ?, ?, ?)", lobby_id, voice_channel.id, text_channel.id, lobby_role.id)
        
        # Invite members
        for member in members:
            DB.execute("INSERT INTO LobbyUsers (UserID, LobbyID) VALUES (?, ?)", member.id, lobby_id)
            await member.add_roles(lobby_role, reason=f"{member} added to {lobby_name}")
            await member.send(embed=self.bot.create_embed("SCUFFBOT SIX MANS", f"You have been added into a six mans lobby.", None), view=View().add_item(discord.ui.Button(label="Join lobby",style=discord.ButtonStyle.link, url=lobby_invite_link)))
        return lobby_id
    
    async def startSixMans(self, lobby_id):
        text_channel = self.bot.get_channel(int(DB.field("SELECT TextChannelID FROM LobbyDetails WHERE LobbyID = ?", lobby_id)))
        view = SixMansPrompt(self.bot, lobby_id)
        embed=view.generate_embed()
        await text_channel.send(embed=embed)
        
    @app_commands.command(name="q", description="Joins the six man queue.")
    @app_commands.guilds(Object(id=1165195575013163038))
    async def queue(self, interaction: discord.Interaction):
        if interaction.user in self.queue:
            self.queue.remove(interaction.user)
            await interaction.response.send_message(embed=self.bot.create_embed("SCUFFBOT SIX MANS", f"You have left the six mans queue.", None), ephemeral=True)
        else:
            if str(interaction.user.id) in DB.column("SELECT UserID FROM LobbyUsers WHERE Type = 0"):
                await interaction.response.send_message(embed=self.bot.create_embed("SCUFFBOT SIX MANS", f"You are already in a six mans lobby. Failed to join queue.", None), ephemeral=True)
            else:
                self.queue.append(interaction.user)
                await interaction.response.send_message(embed=self.bot.create_embed("SCUFFBOT SIX MANS", f"You have joined the six mans queue. ({len(self.queue)}/{PARTY_SIZE})", None), ephemeral=True)
                await self.checkQueue()
    
    @app_commands.command(name="leave", description="Leaves the six man queue.")
    @app_commands.guilds(Object(id=1165195575013163038))
    async def leave(self, interaction: discord.Interaction):
        if not interaction.user in self.queue:
            await interaction.response.send_message(embed=self.bot.create_embed("SCUFFBOT SIX MANS", f"You are not in a queue. Type `/q` to join the queue.", None), ephemeral=True)
        else:
            self.queue.remove(interaction.user)
            await interaction.response.send_message(embed=self.bot.create_embed("SCUFFBOT SIX MANS", f"You have left the six mans queue.", None), ephemeral=True)

        

async def setup(bot):
    await bot.add_cog(SixMans(bot))
