import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio

# ตั้งค่า intents
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
}  # ใส่ ID ของ Roles ตามระดับเลเวล

USER_EXP = {}  # เก็บ EXP ของแต่ละคน {user_id: (exp, level)}
EXP_RATE = 2.5  # 1 นาที = 2.5 EXP

@bot.event
async def on_ready():
    
    update_exp.start()

@bot.event
async def on_voice_state_update(member, before, after):
    """ให้ Role เมื่อเข้าห้องเสียง และลบ Role เมื่อออก"""
    if member.bot:
        return
    guild = member.guild
    # ID ของ Role ที่ต้องการให้เมื่อเข้าห้องเสียง
    VC_ROLE_ID = 1348584551261147197  # ใส่ ID ของ Role ที่ต้องการให้

    # ถ้าเข้าห้องเสียง
    if after.channel:
        if member.id not in USER_EXP:
            USER_EXP[member.id] = (0, 1)  # เริ่มต้น EXP และ Level
        role = guild.get_role(VC_ROLE_ID)
        if role and role not in member.roles:
            await member.add_roles(role)

    # ถ้าออกห้องเสียง
    elif before.channel and not after.channel:
        role = guild.get_role(VC_ROLE_ID)
        if role and role in member.roles:
            await member.remove_roles(role)

@tasks.loop(minutes=1)
async def update_exp():
    """เพิ่ม EXP ทุกนาทีเมื่ออยู่ในห้องเสียง"""
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and member.voice.channel:  # ตรวจสอบว่าอยู่ในห้องเสียง
                exp, level = USER_EXP.get(member.id, (0, 1))
                exp += EXP_RATE  # เพิ่ม EXP ทุกๆ 1 นาที
                next_level_exp = (level ** 2) * 50  # คำนวณ EXP ที่ต้องการในการเลื่อนเลเวล
                if exp >= next_level_exp and level < 100:  # ถ้า EXP มากพอที่จะอัพเลเวล
                    level += 1
                    exp -= next_level_exp
                    await check_and_give_role(member, level)  # ให้ Role ตามเลเวล
                USER_EXP[member.id] = (exp, level)  # อัพเดต EXP และ Level

async def check_and_give_role(member, level):
    """มอบ Role ใหม่ทุก 10 เลเวล"""
    guild = member.guild
    for lvl, role_id in EXP_ROLE_IDS.items():
        role = guild.get_role(role_id)
        if level >= lvl and role and role not in member.roles:  # เช็คว่าเลเวลถึงแล้วหรือยัง
            await member.add_roles(role)  # มอบ Role

@bot.command()
async def exp(ctx):
    """แสดง EXP ปัจจุบันและเลเวลของผู้ใช้"""
    user_id = ctx.author.id
    exp, level = USER_EXP.get(user_id, (0, 1))
    next_level_exp = (level ** 2) * 50  # คำนวณ EXP ที่ต้องใช้ในการอัพเลเวลถัดไป
    progress = int((exp / next_level_exp) * 10)  # คำนวณเปอร์เซ็นต์เป็นแท่ง
    bar = "█" * progress + "-" * (10 - progress)  # แสดง Progress Bar
    percentage = (exp / next_level_exp) * 100  # คำนวณเปอร์เซ็นต์ที่เป็นตัวเลข
    
    await ctx.send(f"{ctx.author.mention} ➤ เลเวล: {level} | EXP: {int(exp)} / {next_level_exp}\n[{bar}] ({percentage:.1f}%)")

bot.run(os.getenv('SYPHON'))
