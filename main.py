import os
import discord
import asyncio
import random
from myserver import server_on
from discord.ext import commands, tasks

EXP_RATE = 2.5
EXP_ROLE_IDS = {10: 1345467425499385886, 20: 1345467017003536384, 30: 1345802923493298286,
                40: 1348597989760958544, 50: 1348597995775590450, 60: 1348597982093774869,
                70: 1348598235861880844, 80: 1348598239619711079, 90: 1348598231533355078, 100: 1348598227246645360}

ADMIN_ROLE_ID = 1114614641709023272
ANNOUNCE_CHANNEL_ID = 1348165898736767038

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="d!", intents=intents)

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
google_creds = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
scope = ["https://docs.google.com/spreadsheets/d/1Ea_nIYkxs4HOyEfkqXTVz-QaKu5SPBVOUd1Nnp6QMPo/edit?usp=sharing", "https://www.googleapis.com/robot/v1/metadata/x509/romandiscord%40romandiscord.iam.gserviceaccount.com"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

def load_exp_data():
    data = sheet.get_all_values()
    exp_data = {row[0]: (int(row[1]), int(row[2])) for row in data[1:] if len(row) >= 3}
    return exp_data

def save_exp_data(user_id, exp, level):
    data = sheet.get_all_values()
    user_ids = [row[0] for row in data]
    
    if str(user_id) in user_ids:
        index = user_ids.index(str(user_id)) + 1
        sheet.update(f"B{index}:C{index}", [[exp, level]])
    else:
        sheet.append_row([str(user_id), exp, level])

USER_EXP = load_exp_data()

@bot.event
async def on_ready():
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

                    channel = guild.get_channel(ANNOUNCE_CHANNEL_ID)
                    if channel:
                        await channel.send(f"**Level Up!** 🎉⋆.˚⤷ {member.mention} level up to **{level}** 🎀\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                USER_EXP[str(member.id)] = (exp, level)
                save_exp_data(str(member.id), exp, level)

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
####################################################
'''เช็คเวล'''
@bot.command()
async def exp(ctx):
    user_id = str(ctx.author.id)
    exp, level = USER_EXP.get(user_id, (0, 1))
    next_level_exp = (level ** 2) * 50
    progress = int((exp / next_level_exp) * 10)
    bar = "█" * progress + "-" * (10 - progress)  
    percentage = (exp / next_level_exp) * 100

    message = (
        f"{ctx.author.mention} ➤ Level: {level} | EXP: {int(exp)} / {next_level_exp}\n"
        f"[{bar}] ({percentage:.1f}%)"
    )

    await ctx.send(message)
####################################################
'''บอร์ดอันดับ'''
@bot.command()
async def rank(ctx):
    sorted_users = sorted(USER_EXP.items(), key=lambda x: (x[1][1], x[1][0]), reverse=True)[:10]
    embed = discord.Embed(title="🏆 **Online Rank VC**", color=discord.Color(0x000000))
    medals = ["🥇", "🥈", "🥉"]
    rank_list = []
    
    for i, (user_id, (exp, level)) in enumerate(sorted_users, start=1):
        member = ctx.guild.get_member(int(user_id))
        display_name = f"**{member.display_name}**" if member else "**Unknown**"
        medal = medals[i-1] if i <= 3 else "・"
        rank_list.append(f"| {medal} ที่ {i} | {display_name} |\n| ・ Level {level} (EXP: {exp}) |\n━━━━━━━━━━━━━━")

    embed.description = "\n".join(rank_list)
    await ctx.send(embed=embed)

####################################################
'''ปรับเวล/exp'''
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def lev(ctx, member: discord.Member, level: int, exp: int = 0):
    if level < 1 or level > 100:
        await ctx.send("🛑 ระดับต้องอยู่ระหว่าง 1-100")
        return
    
    if exp < 0:
        await ctx.send("🛑 ค่า EXP ต้องเป็นจำนวนเต็มบวก")
        return

    USER_EXP[str(member.id)] = (exp, level)
    await check_and_give_role(member, level)
    save_exp_data(str(member.id), exp, level)
    await ctx.send(f"☑ › {member.mention} → ระดับถูกปรับเป็น **{level}** และ EXP เป็น **{exp}** !")

####################################################
"""กดยศออโต้"""
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def add_role(ctx, role_check: discord.Role, role_add: discord.Role):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("อะไรมึงอ่ะ จะทำไร")
        return

    count = 0
    for member in ctx.guild.members:
        if role_check in member.roles and role_add not in member.roles:
            await member.add_roles(role_add)
            count += 1

    await ctx.send(f"✅ เพิ่มบทบาท {role_add.mention} ให้กับ {count} คนที่มีบทบาท {role_check.mention} แล้ว!")


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def del_role(ctx, role_check: discord.Role, role_remove: discord.Role):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("อะไรอะ")
        return

    count = 0
    for member in ctx.guild.members:
        if role_check in member.roles and role_remove in member.roles:
            await member.remove_roles(role_remove)
            count += 1

    await ctx.send(f"✅ ลบบทบาท {role_remove.mention} ออกจาก {count} คนที่มีบทบาท {role_check.mention} แล้ว!")


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def in_role(ctx, role_add: discord.Role):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("เป็นใคร มาสั่งกู")
        return

    count = 0
    for member in ctx.guild.members:
        if len(member.roles) == 1:  # มีแค่ @everyone (Index 0)
            await member.add_roles(role_add)
            count += 1

    await ctx.send(f"✅ เพิ่มบทบาท {role_add.mention} ให้กับ {count} คนที่ไม่มีบทบาทในเซิร์ฟเวอร์แล้ว!")

####################################################
"""บอทด่า"""
from responses import responses_dict

ALLOWED_CHANNELS = [1349573896923250739]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id in ALLOWED_CHANNELS:
        lower_message = message.content.lower()
        response = None

        for key, responses in responses_dict.items():
            if key in lower_message:
                response = random.choice(responses)
                break

        if response:
            await message.channel.send(response)

    await bot.process_commands(message)

####################################################
'''ข้อความ'''
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def chat(ctx, *, args: str):
    
    await ctx.message.delete()

    parts = args.rsplit(" ", 1)
    
    message = parts[0]
    channel = ctx.channel

    if len(parts) > 1 and parts[1].startswith("<#") and parts[1].endswith(">"):
       
        channel_id = int(parts[1][2:-1])
        new_channel = bot.get_channel(channel_id)
        
        if new_channel:
            channel = new_channel
    
    await channel.send(message)   

####################################################

bot.run(os.getenv('SYPHON'))
