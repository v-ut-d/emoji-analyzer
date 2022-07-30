import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import csv
import os
import re

load_dotenv()
TOKEN = os.environ['EMOJI_ANALYZER_BOT_TOKEN']
bot = commands.Bot(command_prefix = 'emoji-analyzer ')

@bot.event
async def on_ready():
    print('bot logged in')

@bot.command()
async def analyze(ctx, arg1='csv', arg2='today-7', arg3='today'):
    if ctx.author.bot:
        return
    async with ctx.channel.typing():
        dict = {}
        guild = ctx.guild
        if re.fullmatch(r'([ad]\d+)|(csv)', arg1) == None:
            await ctx.channel.send('第1引数は`csv`とするか`a10` `d20`のように入力してください。')
            return
        try:
            if arg2[0:5] == 'today':
                if len(arg2) > 5 and arg2[5] == '-':
                    bound1 = datetime.today() - timedelta(days = int(arg2[6:]))
                elif arg2 == 'today':
                    bound1 = datetime.today()
            else:
                bound1 = datetime.fromisoformat(arg2)
            if arg3[0:5] == 'today':
                if len(arg3) > 5 and arg3[5] == '-':
                    bound2 = datetime.today() - timedelta(days = int(arg3[6:]))
                elif arg3 == 'today':
                    bound2 = datetime.today()
            else:
                bound2 = datetime.fromisoformat(arg3)
        except ValueError:
            await ctx.channel.send('第2・第3引数はISOフォーマットで`2000-01-01`のように、または`today`ないし`today-7`(数字の単位は日)のように入力してください。')
            return
        if bound1 >= bound2:
            await ctx.channel.send('第2引数の日付が第1引数の日付よりも後になるように入力してください。')
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
                emojistrs = re.findall(r'\<\:.+?\:\d{16,19}\>', message.content)
                for emojistr in emojistrs:
                    id = re.search(r'\d{16,19}', emojistr).group()
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
        
        std = sorted(data, key=lambda x:x[1], reverse=(arg1[0] == 'd'))

        if arg1 == 'csv':
            path = 'csv/' + datetime.now().replace(microsecond=0).isoformat() + '.csv'
            with open(path, 'w') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerows(std)
            await ctx.send(file=discord.File(path))
            os.remove(path)
            return
        else:
            n = min([int(arg1[1:]),len(std)])
            for i in range(n):
                if i%20 == 0:
                    content = ''
                content += '\n' + std[i][0] + ' : ' + str(std[i][1])
                if i%20 == 19 or i == n-1:
                    await ctx.send(content)

def setup(bot):
    bot.add_command(analyze)

bot.run(TOKEN)
