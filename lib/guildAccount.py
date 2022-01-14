# -*- coding: utf-8 -*-

import sys, os, json
from typing import Union
import discord
from discord.ext import commands
from lib.ndiscord import exst, path, saveGuildData, loadGuildData

# WD: Working Directory
WD = sys.path[0]

# manage guilds account
class guildAccount():
    """
    Guild:
    -----
    `id`
    `str_id`
    `name`
    `channels`
    - - `admin`
    - - `check_rank`
    - - `logs`
    - - `game_report`
    
    Methods:
    --------
    `export`: return a dict with the account\n
    `save`: save all infos in the guild `json` """
    
    def __init__(self, guild: discord.Guild):
        guildExist = True

        self.guildData = json.loads(exst(path(WD, "src", "templates", "guild_template.json")))
        if(loadGuildData(guild.id) is not None):
            for key, val in loadGuildData(guild.id).items():
                self.guildData[key] = val

        self.name:str = guild.name
        self.id:int = guild.id
        self.str_id:str = str(guild.id)
        self.guild:discord.Guild = guild
        self._d_role:str = self.guildData["d_role"]
        self.channels:dict = self.guildData["channels"]

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
            "d_role":self._d_role,
            "channels": self.channels
        }
    
    def save(self):
        self.guildData = self.export()
        saveGuildData(self.id, self.guildData)
    
    def getDefaultRole(self):
        if(self._d_role != ""):
            return discord.utils.get(self.guild.roles, id=self._d_role)
        return None