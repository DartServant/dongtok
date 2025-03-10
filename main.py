import os
import discord
from discord.ext import commands

# ตั้งค่า intents ให้สามารถตรวจจับ Voice State ได้
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ตั้งค่า ID ของ Role ที่ใช้สำหรับเก็บ EXP
EXP_ROLE_ID = 1348584551261147197  # 👈 เปลี่ยนเป็น ID จริงของ Role

@bot.event
async def on_ready():
    print(f'✅ : {bot.user} พร้อมทำงาน!')

@bot.event
async def on_voice_state_update(member, before, after):
    """ให้ Role เมื่อเข้าห้องเสียง และลบ Role เมื่อออก"""
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
