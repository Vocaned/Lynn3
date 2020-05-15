import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import re
import time
import subprocess
import sys
from BotUtils import splitMessage

'''Misc commands'''


class Misc(commands.Cog):
    '''Misc'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['col', 'color', 'colour'])
    async def hex(self, ctx, *, col):
        hexcol = str(col).replace('#', '')
        if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', hexcol):
            raise commands.CommandError(message='Invalid hex color')

        embed = discord.Embed(title='#'+hexcol, colour=int(hexcol, 16))
        r = int(hexcol[:2], 16)
        rp = round(int(hexcol[:2], 16) / 2.55, 2)
        g = int(hexcol[2:4], 16)
        gp = round(int(hexcol[2:4], 16) / 2.55, 2)
        b = int(hexcol[4:6], 16)
        bp = round(int(hexcol[4:6], 16) / 2.55, 2)
        embed.description = f'**Red** = **{str(r)}** (**{str(rp)}%**)\n**Green** = **{str(g)}** (**{str(gp)}%**)\n**Blue** = **{str(b)}** (**{str(bp)}%**)'
        await ctx.send(embed=embed, content='')

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(title='Pong!', colour=0xfffdd0)
        embed.description = f'{str(round(self.bot.latency*1000, 2))}ms'
        await ctx.send(embed=embed, content='')

    @commands.command(aliases=['remind', 'remindme'])
    async def reminder(self, ctx, *message):
        '''Sets a reminder.
        Time must be in ISO 8601 format. Times are in UTC. Examples:
        %reminder 2017-01-10T07:30:59 Example message    =January 10th 2017, 12:30:59 UTC
        %reminder 2026-05-09T20:00:00 Example message    =May 9th 2026, 8 pm UTC
        '''

        date = datetime.fromisoformat(message[0])
        await ctx.send("I'll remind you on " + date.strftime("%c") + "!\n*(please dont use this command for anything super important, reminders might just fail and never actually remind you because I don't have the motivation to make this bot good)*")
        await asyncio.sleep((date-datetime.utcnow()).total_seconds())
        
        embed = discord.Embed(title='Reminder', colour=0x8630bf)
        embed.description = ' '.join(message[1:])
        await ctx.send(embed=embed, content=ctx.author.mention)

    @commands.command()
    async def whois(self, ctx, *, domain):
        '''Whois'''
        if not sys.platform.startswith('linux'):
            await ctx.send('This command is only usable when the bot is hosted on linux. Sorry!')
            return
        output = subprocess.check_output(['whois', domain], stderr=subprocess.PIPE).decode('utf-8')

        for msg in splitMessage(output):
            await ctx.send(msg)

    @commands.command(aliases=['id'])
    async def snowflake(self, ctx, *, snowflake):
        # HACK: Parse mentions by just removing everything that's not a digit
        snowflake = ''.join(c for c in snowflake if c.isdigit())
        snowflake = int(snowflake)
        embed = discord.Embed(title=f'Snowflake {snowflake}', colour=0x7289DA)
        embed.description = f'''**Timestamp**: {datetime.utcfromtimestamp(((snowflake >> 22) + 1420070400000) / 1000).strftime('%c')}
                                **Internal worker ID**: {str((snowflake & 0x3E0000) >> 17)}
                                **Internal process ID**: {str((snowflake & 0x1F000) >> 12)}
                                **Increment**: {str(snowflake & 0xFFF)}'''
        await ctx.send(embed=embed, content='')

def setup(bot):
    bot.add_cog(Misc(bot))