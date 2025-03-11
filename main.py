import os
import discord
import json
import asyncio
import random
from myserver import server_on
from discord.ext import commands, tasks
from message_handler import on_message

EXP_RATE = 2.5
EXP_FILE = os.path.join(os.getcwd(), "exp_data.json")
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
    try:
        with open(EXP_FILE, "r") as f:
            USER_EXP = json.load(f)
            if not isinstance(USER_EXP, dict) or not USER_EXP:  
                USER_EXP = {}  
    except (json.JSONDecodeError, ValueError):
        USER_EXP = {}  

@bot.event
async def on_ready():
    global running_task
    if running_task:
        await bot.close()
        return
    running_task = True
    server_on()
    update_exp.start()

@tasks.loop(seconds=30)  # ⏳ เปลี่ยนจาก 1 นาที เป็น 30 วินาที
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
    
    save_exp_data()  # ✅ เซฟ EXP ทุก 30 วินาที


async def check_and_give_role(member, level):
    guild = member.guild
    for lvl, role_id in EXP_ROLE_IDS.items():
        role = guild.get_role(role_id)
        if level >= lvl and role and role not in member.roles:
            await member.add_roles(role)

@bot.event
async def on_message(message):
    await on_message(message)
  

@bot.command()
async def exp(ctx):
    user_id = str(ctx.author.id)
    exp, level = USER_EXP.get(user_id, (0, 1))
    next_level_exp = (level ** 2) * 50
    progress = int((exp / next_level_exp) * 10)
    bar = "█" * progress + "-" * (10 - progress)
    percentage = (exp / next_level_exp) * 100
    
    save_exp_data()  # ✅ บันทึก EXP ทุกครั้งที่เรียก d!exp
    
    await ctx.send(f"{ctx.author.mention} ➤ เลเวล: {level} | EXP: {int(exp)} / {next_level_exp}\n[{bar}] ({percentage:.1f}%)")


last_exp_data = None  # ใช้เก็บข้อมูล EXP ล่าสุด
def save_exp_data():
    global last_exp_data
    if USER_EXP != last_exp_data:  # ตรวจสอบว่า USER_EXP มีการเปลี่ยนแปลง
        with open(EXP_FILE, "w") as f:
            json.dump(USER_EXP, f, indent=4)
        last_exp_data = USER_EXP.copy()  # อัปเดตข้อมูล EXP ล่าสุด

@bot.event
async def on_disconnect():
    save_exp_data()  # บันทึก EXP ก่อนปิดบอท

bot.run(os.getenv('SYPHON'))
