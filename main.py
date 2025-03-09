import os 
import discord
from discord.ext import commands
from myserver import server_on

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ : {bot.user}')
    server_on()

@bot.command()
async def hello(ctx):
    await ctx.send(f'สวัสดี {ctx.author.mention}! 😊')

bot.run(os.getenv('SYPHON'))
