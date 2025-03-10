import os
import discord
from discord.ext import commands
from myserver import server_on

# ตั้งค่า intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

EXP_ROLE_ID = 1348584551261147197  # 👈 ใส่ ID ของ Role ที่ใช้

@bot.event
async def on_ready():
    print(f'✅ : {bot.user} พร้อมทำงาน!')
    server_on()  # ✅ เปิดเซิร์ฟเวอร์ Flask ไปด้วย

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    role = guild.get_role(EXP_ROLE_ID)

    if not role:
        print(f"⚠️ ไม่พบ Role ID: {EXP_ROLE_ID} ในเซิร์ฟเวอร์!")
        return

    if after.channel and role not in member.roles:
        await member.add_roles(role)
        print(f"✅ เพิ่ม Role ให้ {member.display_name}")
    elif not after.channel and role in member.roles:
        await member.remove_roles(role)
        print(f"❌ ลบ Role ออกจาก {member.display_name}")

bot.run(os.getenv('SYPHON'))
