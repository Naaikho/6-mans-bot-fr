# -*- coding: utf-8 -*-

import sys, os, json
from typing import Union
import discord
from discord.ext import commands
from .pathParser import *
from .Exeptions import *

def exst(file) -> Union[str, None]:
    """ Check if the path of ``file`` exist and open it. """
    if os.path.exists(file):
        with open(file, "r") as data:
            return data.read()
    else:
        return None

def saveGuildData(guild: Union[str, int], data:dict) -> None:
    """ Save the data of a guild in a ``.json`` with the ``id`` of the guild in name """
    with open(pathGuild(guild), "w") as f:
        json.dump(data, f, indent=4)

def saveUsersData(user: Union[str, int], data:dict) -> None:
    """ Save the data of a user in a ``.json`` with the ``id`` of the user in name """
    with open(pathAcc(user), "w") as f:
        json.dump(data, f, indent=4)

def loadGuildData(guild: Union[str, int]) -> Union[dict, None]:
    """ Load the guilds data """
    if(exst(pathGuild(guild))):
        with open(pathGuild(guild), "r") as f:
            return json.load(f)
    return None

def loadUsersData(user: Union[str, int]) -> Union[dict, None]:
    """ Load the users data """
    if(exst(pathAcc(user))):
        with open(pathAcc(user), "r") as f:
            return json.load(f)
    return None

def loadMmr() -> Union[dict, None]:
    """ Load the mmr steps """
    if(exst(rocketPath("mmr.json"))):
        with open(rocketPath("mmr.json"), "r") as data:
            return json.loads(data.read())
    return None

def addId(id:str):
    id = id.lower()
    if(not exst(path(sys.path[0], "src", "rocket_league", "accountId"))):
        open(path(sys.path[0], "src", "rocket_league", "accountId"), "w")
    with open(rocketPath("accountId"), "r") as data:
        for epic_id in data.readlines():
            if(epic_id.strip() == id):
                raise IdError("L'id renseigné est déjà utilisé.")

    with open(rocketPath("accountId"), "a") as data:
        data.write(id + "\n")