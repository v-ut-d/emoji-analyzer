import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import csv
import os
import re

load_dotenv()
TOKEN = os.environ['BOT_TOKEN']
path = 'dict.csv'
bot = commands.Bot(command_prefix = '!')

@bot.event
async def on_ready():
    print('bot logged in')

@bot.command()
async def analyze(ctx, arg1=(date.today() - timedelta(days=7)).isoformat(), arg2=date.today().isoformat(), arg3='10'):
    if ctx.author.bot:
        return
    async with ctx.channel.typing():
        dict = {}
        guild = ctx.guild
        bound1 = datetime.fromisoformat(arg1)
        bound2 = datetime.fromisoformat(arg2)
        if bound1 >= bound2:
            await ctx.channel.send('引数が不正です。')
            return
        for emoji in guild.emojis:
            if emoji.is_usable() and not(emoji.animated):
                dict[str(emoji)] = 0
        for channel in guild.text_channels:
            perm = channel.permissions_for(guild.me)
            if not(perm.read_message_history):
                continue
            for message in await channel.history(limit=None, after=bound1, before=bound2).flatten():
                if message.author == bot.user:
                    continue
                for reaction in message.reactions:
                    try:
                        if reaction.custom_emoji:
                            dict[str(reaction.emoji)] += reaction.count
                    except KeyError as e:
                        for key in dict.keys():
                            if str(emoji.id) in key:
                                dict[key] += 1
                    except Exception as e:
                        print(e)
                emojistrs = re.findall(r'\<\:.+?\:\d{18}\>', message.content)
                for emojistr in emojistrs:
                    id = re.search(r'\d{18}', emojistr).group()
                    try:
                        if bot.get_emoji(int(id)) != None:
                            dict[emojistr] += 1
                    except Exception as e:
                        for key in dict.keys():
                            if id in key:
                                dict[key] += 1
                    except Exception as e:
                        print(e)
        data = []
        for key, count in sorted(dict.items()):
            data += [[key, count]]
        
        std = sorted(data, key=lambda x:x[1])
        with open('data.csv', 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(std)

        n = min([int(arg3),len(std)])
        for i in range(n):
            if i%20 == 0:
                content = ''
            content += '\n' + std[i][0] + ' : ' + str(std[i][1])
            if i%20 == 19 or i == n-1:
                await ctx.channel.send(content)

def setup(bot):
    bot.add_command(analyze)

bot.run(TOKEN)