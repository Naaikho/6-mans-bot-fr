# -*- coding: utf-8 -*-

import sys, os, json
from typing import Union
import discord
from discord.ext import commands
from lib.ndiscord import exst, path, pathAcc, saveUsersData, loadUsersData

# WD: Working Directory
WD = sys.path[0]

# manage users account
class userAccount():
    """
    User:
    -----
    `name`
    `id`
    `str_id`
    `rank`
    `rl_rank`
    `points`
    `platform`
    `6mans`
    - `wins`
    - `loses`
    - `current_game`
    
    Methods:
    --------
    `export`: return a dict with the account\n
    `save`: save all infos in the user `json` """
    
    def __init__(self, user: discord.Member):
        self.usersData = json.loads(exst(path(WD, "src", "templates", "users_template.json")))
        if(loadUsersData(user.id) is not None):
            for key, val in loadUsersData(user.id).items():
                self.usersData[key] = val

        self.name:str = user.display_name
        self.id:int = user.id
        self.str_id:str = str(user.id)
        self.member:discord.Member = user
        self.mention:str = user.mention
        self.rank:str = self.usersData["rank"]
        self.rl_rank:str = self.usersData["rl_rank"]
        self.points:int = self.usersData["points"]
        self.platform:str = self.usersData["platform"]
        self.game_id:str = self.usersData["game_id"]
        self.six_mans:dict = self.usersData["six_mans"]

        self.save()
    
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other.id

    def export(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "str_id": self.str_id,
            "rl_rank": self.rl_rank,
            "rank": self.rank,
            "points": self.points,
            "platform": self.platform,
            "game_id": self.game_id,
            "six_mans": self.six_mans
        }
    
    def save(self):
        self.usersData = self.export()
        saveUsersData(self.id, self.usersData)