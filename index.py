import discord
from dotenv import load_dotenv
import datetime
import json
import os
import re

load_dotenv()
TOKEN = os.environ['BOT_TOKEN']
path = 'data.csv'
client = discord.Client()

@client.event
async def on_ready():
    print('logged in')

datetime = datetime.datetime.utcnow() - datetime.timedelta(days=1)
@client.event
async def on_message(msg):
    if msg.content == '!emoji-analyzer analyze':
        data = {}
        guild = msg.guild
        for emoji in guild.emojis:
            data[str(emoji.id)] = 0
        for channel in guild.text_channels:
            perm = channel.permissions_for(guild.me)
            if not(perm.read_message_history):
                continue
            for message in await channel.history(limit=10000, after=datetime).flatten():
                for reaction in message.reactions:
                    try:
                        if reaction.custom_emoji:
                            data[str(reaction.emoji.id)] += reaction.count
                    except Exception as e:
                        print(e)
                emojistrs = re.findall(r'\<\:.+\:\d{18}\>', message.content)
                if emojistrs != []:
                    for emojistr in emojistrs:
                        id = re.search(r'\d{18}', emojistr).group()
                        try:
                            if client.get_emoji(int(id)) != None:
                                data[id] += 1
                        except Exception as e:
                            print(e)
        print(data)

        with open(path, mode='w') as f:
            for key, value in sorted(data.items()):
                f.write(f'{key}, {value}\n')


client.run(TOKEN)