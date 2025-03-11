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

ADMIN_ROLE_ID = 1114614641709023272  # แก้เป็น ID ของยศแอดมิน
ANNOUNCE_CHANNEL_ID = 1348165898736767038  # แก้เป็น ID ของห้องแจ้งเตือน

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

@tasks.loop(seconds=30)
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

                    # ประกาศในช่องสำหรับ Level Up
                    guild = member.guild
                    channel = guild.get_channel(ANNOUNCE_CHANNEL_ID)

                    if channel:
                        embed = discord.Embed(
                            title="🎉 **𝗟𝗲𝘃𝗲𝗹 𝗨𝗽!** 🎉", 
                            description=f"{member.mention} **𝗟𝗲𝘃𝗲𝗹 𝘂𝗽 𝘁𝗼 {level}** !", 
                            color=discord.Color.gold()
                        )
                        embed.set_thumbnail(url=member.avatar.url)  
                        embed.add_field(name="🔸 𝗡𝗲𝘄 𝗟𝗲𝘃𝗲𝗹", value=f"**{level}**", inline=True)
                        embed.set_footer(text="𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀 𝗼𝗻 𝗹𝗲𝘃𝗲𝗹𝗶𝗻𝗴 𝘂𝗽!") 

                        await channel.send(embed=embed)

                # อัปเดตข้อมูล EXP และเลเวลใหม่
                USER_EXP[str(member.id)] = (exp, level)
                save_exp_data()

async def check_and_give_role(member, level):
    guild = member.guild
    current_roles = {r.id for r in member.roles}
    
    for lvl, role_id in EXP_ROLE_IDS.items():
        role = guild.get_role(role_id)
        if role:
            if level >= lvl and role_id not in current_roles:
                await member.add_roles(role)
            elif level < lvl and role_id in current_roles:
                await member.remove_roles(role)

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
        "เสร่อ": ["แม่มึงอะ", "ไอหน้าหี", "ไอเหลือขอ", "ไม่ต้องเสือก", "ไอหมา"],
        "อมึงอ": ["แม่มึงอะ"],
        "ม่มึงอ": ["พ่อมึงอ่ะ"],
        "อมึงต": ["พ่อมึงดิ","พ่อมึงอะ"],
        "ม่มึงต": ["แม่มึงดิ","แม่มึงอะ"],
        "มึง": ["เต็มเปล่า", "แล้ว", "ยังไง", "อ่อ", "55555", "เต็มมั้ยกุถาม", "555"],
        "มืง": ["เต็มเปล่า", "แล้ว", "ยังไง", "อ่อ", "55555", "เต็มมั้ยกุถาม", "555"],
        "กุ": ["เต็มมั้ย", "แล้วไง", "หรอ", "อ่อ", "5443225", "5225", "ไอหมา"],
        "กู": ["เต็มมั้ย", "แล้วไง", "หรอ", "อ่อ", "5443225", "5225", "ไอหมา"],
        "ดอกทอง": ["แม่มึงสิดอกทอง", "กูถามหรอ", "อย่ามึน", "ไอฮิปโป", "ไอลิง"],
        "เอ๋อ": ["เสร่อจัด", "กูถามหรอ", "อย่ามึน", "รั่วเลย", "พ่อมึงอ่ะ"],
        "ไอ": ["โง่", "กูถามหรอ", "ถุ้ย", "ไอสัส", "ควย"],
        "หี": ["หีเปรี้ยวหีเค็ม?", "แล้วทำไม", "ทำไมอ่ะ", "หน้ามึงอ่ะ", "อย่างหลอน"],
        "สั": ["แล้ว", "แล้วทำไม", "โง่", "ซมดง", "หรอๆ"],
        "ปากดี": ["แล้วยังไง", "อ่อหรอ", "ไอจ๋อบ่นไร", "ชุ่วชุ่วโม่ะๆ", "ไอลิง"],
        "ขำ": ["เสือก", "ทำไมอ่ะ", "เสร่อจัด", "ขำหมา", "ให้หมาถาม", "โง่"],
        "ตลก": ["ขำขี้แตก", "หุบปาก", "ฮ่าฮ่า", "ก็ตลกไง", "ขำกลิ้ง"],
        "จอก": ["มึงควรนอน", "สภาพ", "ไม่ได้ถาม", "ไม่ต้องเสือก", "ไอหูตุ่น"],
        "กาก": ["มึงควรนอนอะ", "สภาพจัด", "ไม่ได้ถามนะ", "ไม่ต้องเสือกจั๊ฟ", "ไอปีจอ"],
        "ยุ่ง": ["กูถามหรอ", "สภาพ", "พ่อมึงอ่ะ", "โง่", "ไอหน้าหี"],
        "พ่อ": ["ควยไร", "อะไรอะ", "หลอน", "เสร่อ", "เสือก", "มึงบ้า"],
        "แม่": ["ควยไร", "อะไรอะ", "มึงบ้า", "เสร่อ", "เสือก", "หลอน"],
        "โง่": ["ควยไร", "อะไรอะ", "หลอน", "เสร่อ", "เสือก", "มึงบ้าป้ะ", "ไปนอนนะ"],
        "หลอน": ["เต็มเปล่า", "ไปนอนนะ", "ไร", "เสร่อ", "เสือก", "มึงบ้าอ่อ"],
        "ไร": ["มุนซึง", "ไอควาย", "แล้วควยไร", "ไม่ต้องเสือกเนาะ", "ไอปากแหว่ง"],
        "ไม": ["มินจง", "ไอควาย", "แล้วควยไล", "ไม่ต้องเสือกก", "ไอฟันเหยิน"],
        "ด่า": ["หรอไอเหี้ย", "ไอหมูเป๋", "ไอพิการ", "รั่วจัด", "ไอตาโบ๋","จะสื่อไร","อย่างโง่"],
        "เงียบ": ["มึงเหงาหรอไอเหี้ย", "ควยไร", "หุบปาก", "แล้ว", "ยุ่ง","เสือก","นอนเถอะ"],
    }

    lower_message = message.content.lower()
    response = None

    for key, responses in responses_dict.items():
        if key in lower_message:
            response = random.choice(responses)
            break

    if response:
        await message.channel.send(response)
    await bot.process_commands(message)

@bot.command()
async def exp(ctx):
    user_id = str(ctx.author.id)
    exp, level = USER_EXP.get(user_id, (0, 1))
    next_level_exp = (level ** 2) * 50
    progress = int((exp / next_level_exp) * 10)
    bar = "🟩" * progress + "⬜" * (10 - progress)  # ใช้สีเขียวแทนความคืบหน้า
    percentage = (exp / next_level_exp) * 100

    save_exp_data()

    embed = discord.Embed(
        title=f"🔸 𝗘𝗫𝗣 | {ctx.author.display_name}",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)  # ใส่รูปโปรไฟล์
    embed.add_field(name="🔹 𝗟𝗲𝘃𝗲𝗹", value=f"**{level}**", inline=True)
    embed.add_field(name="⚡ 𝗘𝘅𝗽", value=f"**{int(exp)} / {next_level_exp}**", inline=True)
    embed.add_field(name="📊 𝗦𝘁𝗮𝘁𝘂𝘀", value=f"{bar} **({percentage:.1f}%)**", inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def rank(ctx):
    sorted_users = sorted(USER_EXP.items(), key=lambda x: x[1][1], reverse=True)[:10]
    embed = discord.Embed(title="🏆 𝐎𝐧𝐥𝐢𝐧𝐞 𝐑𝐚𝐧𝐤 𝐕𝐂", color=discord.Color.green())

    medals = ["🥇", "🥈", "🥉"]  # เหรียญสำหรับ 3 อันดับแรก
    rank_list = []
    
    for i, (user_id, (exp, level)) in enumerate(sorted_users, start=1):
        member = ctx.guild.get_member(int(user_id))
        display_name = f"**{member.display_name}**" if member else "**Unknown**"
        medal = medals[i-1] if i <= 3 else "🏅"  # Top 3 ใช้เหรียญพิเศษ อื่นๆ ใช้ 🏅
        
        rank_list.append(f"| {medal} ที่ {i} | {display_name} |\n| 🔹 𝗟𝗲𝘃𝗲𝗹 {level} |\n━━━━━━━━━━━━━━")

    embed.description = "\n".join(rank_list)  # ใช้เส้นคั่นให้ดูเป็นระเบียบ
    await ctx.send(embed=embed)


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def lev(ctx, member: discord.Member, level: int):
    if level < 1 or level > 100:
        await ctx.send("🛑 **𝗧𝗵𝗲 𝗻𝘂𝗺𝗯𝗲𝗿 𝗼𝗳 𝗹𝗲𝘃𝗲𝗹𝘀 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗯𝗲𝘁𝘄𝗲𝗲𝗻 𝟭 𝗮𝗻𝗱 𝟭𝟬𝟬.**.")
        return
    
    # ปรับเลเวลของผู้ใช้
    USER_EXP[str(member.id)] = (0, level)
    await check_and_give_role(member, level)
    save_exp_data()
    
    embed = discord.Embed(
        title="✅ 𝗟𝗲𝘃𝗲𝗹 𝗔𝗱𝗷𝘂𝘀𝘁𝗺𝗲𝗻𝘁 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱!",
        description=f"{member.mention} **has been leveled to {level}** successfully!",
        color=discord.Color(0x000000)
    )
    embed.set_thumbnail(url=member.avatar.url)  # เพิ่มรูปโปรไฟล์ของสมาชิก
    embed.add_field(name="🔹 𝗨𝘀𝗲𝗿", value=f"**{member.display_name}**", inline=False)
    embed.add_field(name="🔸 𝗡𝗲𝘄 𝗟𝗲𝘃𝗲𝗹", value=f"**{level}**", inline=False)
    embed.set_footer(text="𝗟𝗲𝘃𝗲𝗹 𝗮𝗱𝗷𝘂𝘀𝘁𝗺𝗲𝗻𝘁 𝗮𝗰𝘁𝗶𝗼𝗻 𝗯𝘆 𝗔𝗱𝗺𝗶𝗻")  # ใส่ฟุตเตอร์ที่บอกว่าเป็นการปรับเลเวลจาก Admin

    await ctx.send(embed=embed)

last_exp_data = None

def save_exp_data():
    global last_exp_data
    if USER_EXP != last_exp_data:
        with open(EXP_FILE, "w") as f:
            json.dump(USER_EXP, f, indent=4)
        last_exp_data = USER_EXP.copy()

@bot.event
async def on_disconnect():
    save_exp_data()

bot.run(os.getenv('SYPHON'))
