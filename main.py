import os
import discord
import json
import asyncio
from myserver import server_on
from discord.ext import commands, tasks

EXP_RATE = 2.5
EXP_FILE = "exp_data.json"
EXP_ROLE_IDS = {10: 1345467425499385886, 20: 1345467017003536384, 30: 1345802923493298286,
                40: 1348597989760958544, 50: 1348597995775590450, 60: 1348597982093774869,
                70: 1348598235861880844, 80: 1348598239619711079, 90: 1348598231533355078, 100: 1348598227246645360}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="d!", intents=intents)
USER_EXP = {}
running_task = False

if os.path.exists(EXP_FILE):
    with open(EXP_FILE, "r") as f:
        USER_EXP = json.load(f)

@bot.event
async def on_ready():
    global running_task
    if running_task:
        await bot.close()
        return
    running_task = True
    server_on()
    update_exp.start()

@tasks.loop(minutes=1)
async def update_exp():
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and member.voice.channel:
                exp, level = USER_EXP.get(str(member.id), (0, 1))
                exp += EXP_RATE
                next_level_exp = (level ** 2) * 50
                if exp >= next_level_exp and level < 100:
                    level += 1
                    exp -= next_level_exp
                    await check_and_give_role(member, level)
                USER_EXP[str(member.id)] = (exp, level)
    save_exp_data()

async def check_and_give_role(member, level):
    guild = member.guild
    for lvl, role_id in EXP_ROLE_IDS.items():
        role = guild.get_role(role_id)
        if level >= lvl and role and role not in member.roles:
            await member.add_roles(role)

@bot.command()
@commands.is_owner()
async def pidbot(ctx):
    await ctx.send("🛑 ออฟละ ควย.")
    update_exp.cancel()
    save_exp_data()
    await asyncio.sleep(1)  # รอให้ข้อมูลถูกบันทึกลงไฟล์ก่อน
    os._exit(0)  # ปิดโปรแกรมทันทีแบบปลอดภัย


@bot.command()
async def exp(ctx):
    user_id = str(ctx.author.id)
    exp, level = USER_EXP.get(user_id, (0, 1))
    next_level_exp = (level ** 2) * 50
    progress = int((exp / next_level_exp) * 10)
    bar = "█" * progress + "-" * (10 - progress)
    percentage = (exp / next_level_exp) * 100
    await ctx.send(f"{ctx.author.mention} ➤ เลเวล: {level} | EXP: {int(exp)} / {next_level_exp}\n[{bar}] ({percentage:.1f}%)")

def save_exp_data():
    with open(EXP_FILE, "w") as f:
        json.dump(USER_EXP, f, indent=4)

bot.run(os.getenv('SYPHON'))
