import discord
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ['BOT_TOKEN']

client = discord.Client()

@client.event
async def on_ready():
    print('logged in')

client.run(TOKEN)