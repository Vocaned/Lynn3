import discord
from discord.ext import commands
from datetime import datetime
import subprocess
import json
import math
import requests
import re
from dateparser.search import search_dates
import time
import asyncio

"""Misc commands"""


class Misc(commands.Cog):
    """Misc"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.cooldown(60, 60)
    @commands.is_owner()
    async def speedtest(self, ctx):
        """Speedtest"""
        message = await ctx.send('\N{HOURGLASS}')
        output = json.loads(subprocess.check_output(['speedtest', '--json']))
        down = '{0:.2f}'.format(int(output["download"]) / 1000000)
        up = '{0:.2f}'.format(int(output["upload"]) / 1000000)
        ping = '{0:.2f}'.format(output["ping"])
        embed = discord.Embed(title='Speedtest', colour=0x551a8b)
        embed.description = 'Fam0r is paying for a 100Mb/100Mb connection, but is getting ' + str(down) + 'Mb/' + str(up) + 'Mb! (ping ' + str(ping) + 'ms)'
        embed.timestamp = datetime.utcnow()
        await message.edit(embed=embed, content="")

    @commands.command()
    async def lgbt(self, ctx):
        await ctx.message.delete()
        await ctx.send("<a:lgbt1:559809814943891457> <a:lgbt2:559809821377822720>")
        
    @commands.command(aliases=["col", "color", "colour"])
    async def hex(self, ctx, *, col):
        hexcol = str(col).replace("#", "")
        if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', hexcol):
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
            return

        embed = discord.Embed(title="#"+hexcol, colour=int(hexcol, 16))
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
        embed = discord.Embed(title="Pong!", colour=0xfffdd0)
        embed.description = str(round(self.bot.latency*1000, 2)) + "ms"
        await ctx.send(embed=embed, content='')

    @commands.command(aliases=["remind", "remindme"])
    async def reminder(self, ctx, *, string):
        """Reminder"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        embed = discord.Embed(title="Reminder", colour=0x8630bf)
        date = search_dates(string, settings={"TIMEZONE": "UTC"})
        if date and date[-1][1]:
            embed.timestamp = date[-1][1]
        embed.description = string.split("|")[0]
        embed.set_footer(text=str(ctx.message.author.name) + '#' +  str(ctx.message.author.discriminator), icon_url=ctx.message.author.avatar_url)
        await ctx.message.delete()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed, content='')

    @commands.command(aliases=["id"])
    async def snowflake(self, ctx, *, snowflake):
        try:
            snowflake =int(snowflake)
            embed = discord.Embed(title="Snowflake " + bin(snowflake)[2:], colour=0x7289DA)
            embed.description = "**Timestamp**: " + datetime.utcfromtimestamp(((snowflake >> 22) + 1420070400000) / 1000).strftime('%c') \
                              + "\n**Internal worker ID**: " + str((snowflake & 0x3E0000) >> 17) \
                              + "\n**Internal process ID**: " + str((snowflake & 0x1F000) >> 12) \
                              + "\n**Increment**: " + str(snowflake & 0xFFF)
            await ctx.send(embed=embed, content='')
        except:
            await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
        
# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Misc(bot))
