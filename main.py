# -*- coding: utf-8 -*-

from discord.embeds import Embed


try:
    import discord
    from discord.ext import commands
    import traceback
    import datetime
    import asyncio
    import os, sys, platform
    import requests
    import json
    import string
    import random
    from typing import Union
    from captcha.image import ImageCaptcha
    from lib.ndiscord import *
    from lib.guildAccount import *
    from lib.userAccount import *
except ImportError:
    import subprocess

    if platform.system() == "Windows":
        installer = "py -m pip install discord.py captcha"
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        installer = "python3 -m pip install discord.py captcha"
    else:
        print("That script require:\n - discord.py\n - captcha\n\npip install <requirements>")
        exit()
    require = subprocess.Popen(installer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(require.communicate()[0].decode())
    import discord
    from discord.ext import commands
    from captcha.image import ImageCaptcha

# ------------------------------ # Glogals Variables # ------------------------------ #

# WD: Working Directory
WD = sys.path[0]
BOT_NAME = "sixBot"
RANK_URL = "http://api.yannismate.de/rank/{}/{}?playlists=ranked_3v3&hideDiv=true"
RANK_URL_2V2 = "http://api.yannismate.de/rank/{}/{}?playlists=ranked_2v2&hideDiv=true"
PLATFORM = "epic"

DELETE_AFTER = {"error":20, "success":15, "color":{
    "success":0x59F265,
    "error":0xF25959
}}
ROLES = {
    "D":"Rank D",
    "C":"Rank C",
    "B":"Rank B",
    "A":"Rank A",
    "X":"Rank X"
    }
CHANNEL = ["report", "logs", "rank", "univ-rank", "commands"] + [x.lower() for x in ROLES.keys()]

# ----------------------------------------------------------------------------------- #

tokend = json.loads(open(os.path.join(sys.path[0], "src", "token.json"), "r").read())

if platform.system() == "Linux" or platform.system() == "Darwin":
    try:
        if sys.argv[1].upper() == "DEBUG":
            mode = "DEBUG"
        else:
            mode = "DEFAULT"
    except IndexError:
        mode = "DEFAULT"

if platform.system() == "Windows":
    with open(os.path.join(sys.path[0], "src", "args.json"), "r") as data:
        args = json.loads(data.read())["args"]
        if args.upper() == "DEBUG":
            mode = args
        else:
            mode = "DEFAULT"

if mode.lower() == "debug":
    token = tokend["testbot"]
    # info = "test"
if mode.lower() == "default":
    token = tokend[BOT_NAME]
    # info = "serv"

dataPath = path(WD, "src", "data")
if not os.path.exists(dataPath):
    os.mkdir(dataPath)

guilsPath = path(WD, "src", "data", "guilds")
if not os.path.exists(guilsPath):
    os.mkdir(guilsPath)

usersPath = path(WD, "src", "data", "users")
if not os.path.exists(usersPath):
    os.mkdir(usersPath)

print("Mode: {}".format(mode.capitalize()))

# allows the bot to see other members of a server
intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

delPath = os.path.join(WD, "src", "data")
for img in os.listdir(delPath):
    if ".png" in img:
        os.remove(path(delPath, img))
del delPath


# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #



# return error with traceback
def print_traceback(error):
    global WD

    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    if not os.path.exists(path(WD, "src", "crash")):
        os.mkdir(path(WD, "src", "crash"))
    date = datetime.datetime.now()
    fileName = "6mans" + "_" + "{}-{}-{}_{}-{}-{}.log".format(date.hour, date.minute,date.second,date.day,date.month,date.year)
    with open(path(WD, "src", "crash", fileName), "w") as data:
        data.write("\n".join(traceback.format_exception(type(error), error, error.__traceback__)))

# remove|replace 
# characters
def sepChar(s:str, chars:str, join:str) -> str:
    for c in chars:
        s = join.join(s.split(c))
    return s

async def getRank(ctx:commands.Context, id:str, mmr:bool=False) -> str:
    platform = "epic"
    r = requests.get(RANK_URL.format(platform, id))
    r_2 = requests.get(RANK_URL_2V2.format(platform, id))
    try:
        userMmr = int(sepChar(r.text.split(" ")[-1], "()", ""))
        userMm_2 = int(sepChar(r_2.text.split(" ")[-1], "()", ""))
    except:
        try:
            await ctx.reply(embed=discord.Embed(title="", description="Id invalide.\nCommande: `!rank <epic_id>`", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
        except discord.errors.DiscordServerError:
            pass
        return "error"
    
    if(userMm_2 > userMmr):
        userMmr = (userMm_2 + userMmr) / 2
    del userMm_2

    if(mmr):
        return str(userMmr)
    
    rankLst = loadMmr()
    userRank = ""
    for rank, rankMmr in rankLst.items():
        if(userMmr >= int(rankMmr)):
            userRank = rank
            continue
        break
    return str(userRank)

async def log(guild:Union[str, int], title:str="", log:str="", color=discord.Embed.Empty):
    try:
        channel_id = int(sepChar(loadGuildData(guild)["channels"]["logs"], "<#>", ""))
        if(channel_id != "" or channel_id != None):
            await client.get_channel(channel_id).send(embed=discord.Embed(title=title, description=log, color=color))
    except ValueError:
        pass
    except Exception as e:
        print_traceback(e)



# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------------------------------------------- #
# --------------------------------------------------------------------------------------------------------------------------------------------------- #




# -------------------------------------------------------------------------------------------------------------------------- #
#                                                       USERS COMMANDS                                                       #
# -------------------------------------------------------------------------------------------------------------------------- #



@client.event
async def on_ready():
    print("target: {0.user}".format(client))
    await client.change_presence(activity=discord.Game('!help | By Naikho'))



@client.command(name="rank")
async def setRank(ctx:commands.Context, *id:str):
    if (ctx.channel.mention != guildAccount(ctx.guild).channels["rank"]):
        return
    
    id = "%20".join(id)

    user = userAccount(ctx.author)

    rank_info = await getRank(ctx, id, mmr=True)
    if(rank_info == "error"):
        return
    user.rl_rank = rank_info

    user.rank = await getRank(ctx, id)

    err = None
    try:
        if(user.game_id != ""):
            raise AlreadyIdError("Vous avez déjà relié un id à ce compte.\nFaites `!update` pour mettre à jour les informations de votre rang.")
        addId(id)
    except IdError as e:
        err = e
    except AlreadyIdError as e:
        err = e

    if(err is not None):
        emb = discord.Embed(title="", description=str(err), color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb, delete_after=DELETE_AFTER["error"])
        return

    user.game_id = id
    user.platform = "epic"
    user.save()

    guild = guildAccount(user.member.guild)
    if guild.getDefaultRole() is not None:
        await user.member.add_roles(guild.getDefaultRole())

    if(user.rank == ""):
        emb = discord.Embed(title="Rank trop bas... 😢".format(user.rank), description="Votre rank est malheureusement trop bas pour rejoindre un rank... **(Champion 1 minimum)**\nCependant, rendez-vous ici pour commencer à jouer: {}".format(guildAccount(ctx.guild).channels["univ-rank"]), color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb)
        return

    member:discord.Member = ctx.message.author
    role:discord.Role = discord.utils.get(member.guild.roles, name=ROLES[user.rank])
    await member.add_roles(role)
    
    emb = discord.Embed(title="Rank **{}** \u200B\u200B 🎉".format(user.rank), description="Votre rank a bien été configuré !\nRendez-vous ici pour commencer à jouer: {}".format(discord.utils.get(ctx.guild.channels, name="rank-" + user.rank.lower()).mention), color=role.color)
    await ctx.reply(embed=emb)
    await log(ctx.guild.id, log="{} est passé rank {}".format(user.mention, user.rank))
    

@setRank.error
async def setRankError(ctx:commands.Context, error):
    if (ctx.channel.mention != guildAccount(ctx.guild).channels["rank"]):
        return

    if(isinstance(error, commands.errors.BadArgument) or isinstance(error, commands.errors.MissingRequiredArgument)):
        await ctx.reply(embed=discord.Embed(description="Commande invalide: `!rank <your_epic_id>`"), delete_after=DELETE_AFTER["error"])
    else:
        print_traceback(error)
        await log(ctx.guild.id, "Error catch", str(error))







@client.command(name="update")
async def updateRank(ctx:commands.Context):
    if (ctx.channel.mention != guildAccount(ctx.guild).channels["rank"]):
        return

    user = userAccount(ctx.message.author)
    if(user.game_id == ""):
        await ctx.reply(embed=discord.Embed(description="Veuillez configurer votre rang avant d'utiliser cette commande.\nPour cela faites: `!rank <your_epic_id>`.", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
        return
    
    oldRank = user.rank
    user.rl_rank = await getRank(ctx, user.game_id, mmr=True)
    user.rank = await getRank(ctx, user.game_id)

    if(user.rank == ""):
        emb = discord.Embed(title="Rank trop bas... 😢".format(user.rank), description="Votre rank est malheureusement trop bas pour rejoindre un rank... **(Champion 1 minimum)**\nCependant, rendez-vous ici pour commencer à jouer: {}".format(guildAccount(ctx.guild).channels["univ-rank"]), color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb)
        return

    member:discord.Member = ctx.message.author
    if(oldRank == user.rank):
        emb = discord.Embed(title="Rank **{}**".format(user.rank), description="Aucune mise à jour necessaire.", color=discord.utils.get(member.guild.roles, name=ROLES[user.rank]).color)
    else:
        user.save()

        if(oldRank != ""):
            oldRole:discord.Role = discord.utils.get(member.guild.roles, name=ROLES[oldRank])
            await member.remove_roles(oldRole)
        
        role:discord.Role = discord.utils.get(member.guild.roles, name=ROLES[user.rank])
        await member.add_roles(role)

        if(oldRank != ""):
            emb = discord.Embed(title="Vous êtes passé au rank **{}**".format(user.rank), description="Nouveau channel disponible: {}".format(discord.utils.get(ctx.guild.channels, name="rank-" + user.rank.lower()).mention), color=role.color)
            await log(ctx.guild.id, log="{} est passé rank {}".format(user.mention, user.rank))
        else:
            emb = discord.Embed(title="Rank **{}**".format(user.rank), description="Status du rank mis à jour: {}".format(discord.utils.get(ctx.guild.channels, name="rank-" + user.rank.lower()).mention), color=role.color)
    
    await ctx.reply(embed=emb)

@updateRank.error
async def setRankError(ctx:commands.Context, error):
    if (ctx.channel.mention != guildAccount(ctx.guild).channels["rank"]):
        return

    print_traceback(error)
    await log(ctx.guild.id, "Error catch", str(error))








@client.command(name="mute")
async def muteRank(ctx:commands.Context):
    if (ctx.channel.mention != guildAccount(ctx.guild).channels["rank"]):
        return

    user = userAccount(ctx.author)
    if(user.game_id == ""):
        await ctx.reply(embed=discord.Embed(description="Veuillez configurer votre rang avant d'utiliser cette commande.\nPour cela faites: `!rank <your_epic_id>`.", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
        return
    if(user.rank == ""):
        await ctx.reply(embed=discord.Embed(description="Mute déjà activé.\nFaites `!update` pour le désactiver.", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
        return
    
    role = discord.utils.get(ctx.guild.roles, name=ROLES[user.rank])
    await user.member.remove_roles(role)
    user.rank = ""
    user.save()
    emb = discord.Embed(title="Mute activé", description="Notifications désactivées.\nPour reactiver les notifications et retrouver l'accès au channel de votre rang faites: `!update`", color=role.color)
    await ctx.reply(embed=emb)

@muteRank.error
async def muteRankError(ctx:commands.Context, error):
    if (ctx.channel.mention != guildAccount(ctx.guild).channels["rank"]):
        return
    
    print_traceback(error)
    await log(ctx.guild.id, "Error catch", str(error))


















# -------------------------------------------------------------------------------------------------------------------------- #
#                                                       ADMIN COMMANDS                                                       #
# -------------------------------------------------------------------------------------------------------------------------- #



@client.command(name="channel")
@commands.has_permissions(administrator=True)
async def setChannel(ctx:commands.Context, c_type:str):
    c_type = c_type.lower()
    if(c_type in CHANNEL):
        guild = guildAccount(ctx.guild)
        guild.channels[c_type] = ctx.channel.mention
        guild.save()

        await ctx.reply(embed=discord.Embed(title="Channel setup !", description="Le channel `{}` à été configuré ({}).".format(c_type, guild.channels[c_type])))
        await log(guild.id, log="{} est maintenant le channel pour: `{}`".format(ctx.channel.mention, c_type))
    else:
        emb = discord.Embed(description="Mode de channel invalide\nModes disponibles: `" + " | ".join(CHANNEL) + "`", color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb, delete_after=DELETE_AFTER["error"])
        return

@setChannel.error
async def setChannelError(ctx:commands.Context, error):
        print_traceback(error)
        await log(ctx.guild.id, "Error catch", str(error))



@client.command(name="setRank")
@commands.has_permissions(administrator=True, manage_roles=True)
async def setPlayerRank(ctx:commands.Context, player:discord.Member, rank:str):
    rank = rank.upper()
    user_m = userAccount(player)
    if( rank not in ROLES.keys()):
        emb = discord.Embed(description="`'Rank {}` invalide.\nListe des rank possible: `" + " | ".join([x for x in ROLES.keys()]) +"`.", color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb, delete_after=DELETE_AFTER["error"])
        return
    if(user_m.game_id == "" or user_m.rank == ""):
        emb = discord.Embed(title="Rank non modifiable", description="Le joueur mentionné s'est mute ou n'a pas encore setup son compte.\nPour setup: `!rank <epic_id>`\nPour se demute: `!update`", color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb, delete_after=DELETE_AFTER["error"])
        return
    if(user_m.rank == rank):
        emb = discord.Embed(title="Oops !", description="Le joueur mentionné possède déjà le {}".format(discord.utils.get(user_m.member.guild.roles, name=ROLES[user_m.rank]).mention), color=DELETE_AFTER["color"]["error"])
        await ctx.reply(embed=emb, delete_after=DELETE_AFTER["error"])
        return
    await user_m.member.remove_roles(discord.utils.get(user_m.member.guild.roles, name=ROLES[user_m.rank]))
    user_m.rank = rank
    user_m.save()
    role:discord.Role = discord.utils.get(user_m.member.guild.roles, name=ROLES[rank])
    await user_m.member.add_roles(role)

    emb = discord.Embed(title="Rank edité !", description="{admin} à passé {player} au {rank}".format(admin=ctx.author.mention, player=user_m.mention, rank=role.mention), color=role.color)
    await ctx.reply(embed=emb)
    await log(ctx.guild.id, "Edition de rank", "{admin} à passé {player} au {rank}".format(admin=ctx.author.mention, player=user_m.mention, rank=role.mention), color=role.color)

@setPlayerRank.error
async def setPlayerRankError(ctx:commands.Context, error):
    if(isinstance(error, commands.errors.BadArgument) or isinstance(error, commands.errors.MissingRequiredArgument)):
        await ctx.reply(embed=discord.Embed(description="Commande invalide: `!setRank <member_mention> <rank>`", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
    else:
        print_traceback(error)
        await log(ctx.guild.id, "Error catch", str(error))



@client.command(name="setRole")
@commands.has_permissions(administrator=True)
async def setRole(ctx:commands.Context, role:discord.Role):
    guild = guildAccount(ctx.guild)
    guild._d_role = role.id
    guild.save()
    await ctx.reply(embed=discord.Embed(description="Le role par defaut est maintenant {}".format(role.mention), color=role.color), delete_after=DELETE_AFTER["success"])
    await log(guild.guild.id, log="Le role par defaut est maintenant {}".format(role.mention), color=role.color)

@setRole.error
async def setRoleError(ctx:commands.Context, error):
    if isinstance(error, commands.errors.RoleNotFound):
        await ctx.reply(embed=discord.Embed(description="Role introuvable: `!setRole <default_role>`", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
    if(isinstance(error, commands.errors.MissingPermissions)):
        return
    print_traceback(error)
    await log(ctx.guild.id, "Error catch", str(error))



@client.command(name="clear")
@commands.has_permissions(administrator=True, manage_roles=True)
async def clearUser(ctx:commands.Context, user:discord.Member):
    user:userAccount = userAccount(user)
    guild:guildAccount = guildAccount(ctx.guild)

    if(user.rank != ""):
        await user.member.remove_roles(discord.utils.get(user.member.guild.roles, name=ROLES[user.rank]))

    with open(rocketPath("accountId"), "r") as data:
        accountId = [x.strip() for x in data.readlines()]
    with open(rocketPath("accountId"), "w") as data:
        i=0
        while i < len(accountId):
            if(user.game_id.lower() == accountId[i].lower()):
                del accountId[i]
                break
            i+=1
        accountId = "\n".join(accountId)
        data.write(accountId + "\n")

    user.rl_rank = ""
    user.rank = ""
    user.game_id = ""
    user.save()
    
    await ctx.reply(embed=discord.Embed(description="Le joueur {} a été clear de la base de donnée.".format(user.mention), color=DELETE_AFTER["color"]["success"]))
    await log(ctx.guild.id, log="Le joueur {} a été clear de la base de donnée.".format(user.mention), color=DELETE_AFTER["color"]["success"])

@clearUser.error 
async def clearUserError(ctx:commands.Context, error):
    if isinstance(error, commands.errors.RoleNotFound):
        await ctx.reply(embed=discord.Embed(description="Role introuvable: `!clear <user_mention>`", color=DELETE_AFTER["color"]["error"]), delete_after=DELETE_AFTER["error"])
    if(isinstance(error, commands.errors.MissingPermissions)):
        return
    print_traceback(error)
    await log(ctx.guild.id, "Error catch", str(error))










# if an unknow error is raised
@client.event
async def on_command_error(ctx, error):
    global delete_after
    return



@client.event
async def on_message(message:discord.Message):

    if(message.author.bot):
        return

    guild = guildAccount(message.guild)
    user = userAccount(message.author)

    await client.process_commands(message)

@client.event
async def on_reaction_add(reaction, user):
    pass



async def stopClient():
    await client.close()
    await asyncio.sleep(3)

def startClient():
    # try_ping = True
    # thread = threading.Thread(target=lambda: isConnected(try_ping, client, info))
    # thread.start()
    client.run(token)

if  __name__ == "__main__":
    startClient()