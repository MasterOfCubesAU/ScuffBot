from enum import Enum
import random
from typing import Literal, Union

import discord
from lib.bot import DB

PARTY_SIZE = 6

class SixMansState(Enum):
    CHOOSE_CAPTAIN_ONE = 1
    CHOOSE_CAPTAIN_TWO = 2
    CHOOSE_1S_PLAYER = 3
    PLAYING = 4
    SCORE_UPLOAD = 5
    POST_MATCH = 6

class SixMansMatchType(Enum):
    PRE_MATCH = 0
    ONE_V_ONE = 1
    TWO_V_TWO = 2
    THREE_V_THREE = 3

class SixMansParty():
    def __init__(self, bot: discord.Client, party_id: int) -> None:
        self.bot = bot
        self.game_id: Union[None, int] = None
        self.party_id = party_id
        self.lobby_id = DB.field("SELECT LobbyID FROM SixManParty WHERE PartyID = %s", self.party_id)
        self.players = self.get_players()
        self.captain_one: Union[None, discord.Member] = None
        self.captain_two: Union[None, discord.Member] = None
        self.generate_captains()
        
        self.reported_scores = {self.captain_one.id: {"1v1": (None, None), "2v2": (None, None), "3v3": (None, None)}, self.captain_two.id: {"1v1": (None, None), "2v2": (None, None), "3v3": (None, None)}}

    async def get_details(self):
        return DB.row("SELECT * FROM SixManLobby WHERE LobbyID = %s", self.lobby_id)
    
    def get_players(self, team: Literal[None, 1, 2] = None):
        return [self.bot.get_user(int(user_id)) for user_id in DB.column("SELECT UserID FROM SixManUsers WHERE PartyID = %s AND Team = %s", self.party_id, 0 if team == None else team)]
    
    def generate_captains(self):
        players = self.get_players()
        self.captain_one = players.pop(random.randint(0, len(players)-1))
        self.captain_two = players.pop(random.randint(0, len(players)-1))
        DB.execute("UPDATE SixManUsers SET Type = 1, Team = 1 WHERE UserID = %s", self.captain_one.id)
        DB.execute("UPDATE SixManUsers SET Type = 2, Team = 2 WHERE UserID = %s", self.captain_two.id)

    def calculate_winner(self) -> Literal[0, 1, 2]:
        if self.game_id == None:
            return 0
        data = [0 if x is None else x for x in DB.row("SELECT 1v1_A, 1v1_B, 2v2_A, 2v2_B, 3v3_A, 3v3_B FROM SixManGames WHERE GameID = %s", self.game_id).values()]

        team_a_wins = sum(data[i] > data[i + 1] for i in range(0, len(data), 2))
        team_b_wins = sum(data[i + 1] > data[i] for i in range(0, len(data), 2))

        match (team_a_wins >= 2, team_b_wins >= 2):
            case (True, False):
                return 1
            case (False, True):
                return 2
            case (False, False):
                return 0
