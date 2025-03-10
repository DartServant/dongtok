import os
import discord
import json
import asyncio
import random
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
    if message.author.bot:
        return

    responses_dict = {
        "ควย": ["ควยไร", "อะไรอะ", "มึงบ้าหรอ", "เสร่อ", "เสือก"],
        "55": ["ขำไร", "เอ๋อ", "", "ตลกอ่อ", "ลิงจัด"],
        "เหี้ย": ["เหี้ยไร", "อะไรอะ", "มึงบ้าหรอ", "เสร่อจัด", "เสือก"],
        "ควาย": ["ควยไร", "อะไรมึง", "มึงอะหรอ", "เสร่อจัง", "ไปนอนมั้ย"],
        "ดแม่": ["แม่มึงอ่ะ", "ไอหน้าหี", "ไอหูตุ่น", "ไม่ต้องเสือก", "แม่มึงอะ"],
        "เสือก": ["พ่อมึงอ่ะ", "ไอหน้าหี", "ไอเหลือขอ", "ไม่ต้องเสือก", "ไอลิง"],
        "อมึงอ": ["แม่มึงอะ"],
        "ม่มึงอ": ["พ่อมึงอ่ะ"],
        "อมึงต": ["พ่อมึงดิ","พ่อมึงอะ"],
        "ม่มึงต": ["แม่มึงดิ","แม่มึงอะ"],
        "มึง": ["เต็มเปล่า", "แล้ว", "ยังไง", "อ่อ", "55555", "เต็มมั้ยกุถาม", "555"],
        "ดอกทอง": ["แม่มึงสิดอกทอง", "กูถามหรอ", "อย่ามึน", "ไอฮิปโป", "ไอลิง"],
        "เอ๋อ": ["เสร่อจัด", "กูถามหรอ", "อย่ามึน", "รั่วเลย", "พ่อมึงอ่ะ"],
        "หี": ["หีเปรี้ยวหีเค็ม?", "แล้วทำไม", "ทำไมอ่ะ", "หน้ามึงอ่ะ", "อย่างหลอน"],
        "สั": ["แล้ว", "แล้วทำไม", "โง่", "ซมดง", "หรอๆ"],
        "ปากดี": ["แล้วยังไง", "อ่อหรอ", "ไอจ๋อบ่นไร", "ชุ่วชุ่วโม่ะๆ", "ไอลิง"],
        "ขำ": ["เสือก", "ทำไมอ่ะ", "เสร่อจัด", "ขำหมา", "ให้หมาถาม", "โง่"],
        "ตลก": ["ขำขี้แตก", "หุบปาก", "ฮ่าฮ่า", "ก็ตลกไง", "ขำกลิ้ง"],
        "จอก": ["มึงควรนอน", "สภาพ", "ไม่ได้ถาม", "ไม่ต้องเสือก", "ไอหูตุ่น"],
        "ยุ่ง": ["กูถามหรอ", "สภาพ", "พ่อมึงอ่ะ", "โง่", "ไอหน้าหี"],
    }

    lower_message = message.content.lower()

    for key, responses in responses_dict.items():
        if key in lower_message:
            response = random.choice(responses)

            break  # ✅ ให้ตอบแค่ครั้งเดียวเพื่อป้องกันการส่งข้อความซ้ำซ้อน

    await bot.process_commands(message)  # ✅ ให้แน่ใจว่าบอทยังสามารถรันคำสั่งได้


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


def save_exp_data():
    with open(EXP_FILE, "w") as f:
        json.dump(USER_EXP, f, indent=4)

@bot.event
async def on_disconnect():
    save_exp_data()  # บันทึก EXP ก่อนปิดบอท

bot.run(os.getenv('SYPHON'))
