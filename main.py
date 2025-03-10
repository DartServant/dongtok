import os
import discord
import json
from myserver import server_on
from discord.ext import commands, tasks

from datetime import datetime, timedelta
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="d!", intents=intents)

EXP_ROLE_IDS = {
    10: 1345467425499385886,
    20: 1345467017003536384,
    30: 1345802923493298286,
    40: 1348597989760958544,
    50: 1348597995775590450,
    60: 1348597982093774869,
    70: 1348598235861880844,
    80: 1348598239619711079,
    90: 1348598231533355078,
    100: 1348598227246645360
}

EXP_PER_MINUTE = 2.5
EXP_FILE = "exp_data.json"
USER_EXP = {}


def load_exp():
    global USER_EXP
    if os.path.exists(EXP_FILE):
        with open(EXP_FILE, "r") as f:
            USER_EXP = json.load(f)
        USER_EXP = {int(k): (float(v[0]), int(v[1])) for k, v in USER_EXP.items()}


def save_exp():
    with open(EXP_FILE, "w") as f:
        json.dump(USER_EXP, f, indent=4)


@bot.event
async def on_ready():
    load_exp()
    server_on()
    update_exp.start()


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    guild = member.guild
    VC_ROLE_ID = 1348584551261147197

    if after.channel:
        if member.id not in USER_EXP:
            USER_EXP[member.id] = (0, 1)
        role = guild.get_role(VC_ROLE_ID)
        if role and role not in member.roles:
            await member.add_roles(role)

    elif before.channel and not after.channel:
        role = guild.get_role(VC_ROLE_ID)
        if role and role in member.roles:
            await member.remove_roles(role)

    save_exp()


@tasks.loop(minutes=1)
async def update_exp():
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and member.voice.channel:
                exp, level = USER_EXP.get(member.id, (0, 1))
                exp += EXP_PER_MINUTE
                next_level_exp = (level ** 2) * 50
                if exp >= next_level_exp and level < 100:
                    level += 1
                    exp -= next_level_exp
                    await check_and_give_role(member, level)
                USER_EXP[member.id] = (exp, level)
    save_exp()


async def check_and_give_role(member, level):
    guild = member.guild
    for lvl, role_id in EXP_ROLE_IDS.items():
        role = guild.get_role(role_id)
        if level >= lvl and role and role not in member.roles:
            await member.add_roles(role)


@bot.command()
async def exp(ctx):
    user_id = ctx.author.id
    exp, level = USER_EXP.get(user_id, (0, 1))
    next_level_exp = (level ** 2) * 50
    progress = int((exp / next_level_exp) * 10)
    bar = "█" * progress + "-" * (10 - progress)
    percentage = (exp / next_level_exp) * 100
    
    await ctx.send(f"{ctx.author.mention} \u279e เลเวล: {level} | EXP: {int(exp)} / {next_level_exp}\n[{bar}] ({percentage:.1f}%)")


@bot.event
async def on_disconnect():
    save_exp()


bot.run(os.getenv('SYPHON'))
