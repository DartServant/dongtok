import os
import discord
from discord.ext import commands, tasks
from message_handler import on_message
from exp_system import load_exp_data, save_exp_data, update_user_exp, check_and_give_role, get_user_exp

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="d!", intents=intents)

# โหลดข้อมูล EXP ตอนเริ่มต้น
load_exp_data()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    update_exp.start()  # เริ่มต้นการทำงานของ update_exp

@tasks.loop(seconds=30)  # ⏳ เปลี่ยนจาก 1 นาที เป็น 30 วินาที
async def update_exp():
    # อัปเดต EXP และให้ role ตาม level ทุกๆ 30 วินาที
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and member.voice.channel:
                exp, level = get_user_exp(member.id)
                update_user_exp(member.id, exp, level)
                await check_and_give_role(member, level)
    save_exp_data()  # ✅ เซฟ EXP ทุก 30 วินาที

@bot.event
async def on_message(message):
    await on_message(message)

@bot.command()
async def exp(ctx):
    # แสดง EXP และ Level ของผู้ใช้
    user_id = str(ctx.author.id)
    exp, level = get_user_exp(user_id)
    next_level_exp = (level ** 2) * 50
    progress = int((exp / next_level_exp) * 10)
    bar = "█" * progress + "-" * (10 - progress)
    percentage = (exp / next_level_exp) * 100
    
    save_exp_data()  # ✅ บันทึก EXP ทุกครั้งที่เรียก d!exp
    
    await ctx.send(f"{ctx.author.mention} ➤ เลเวล: {level} | EXP: {int(exp)} / {next_level_exp}\n[{bar}] ({percentage:.1f}%)")

bot.run(os.getenv('SYPHON'))
