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

    @commands.command(aliases=["col", "color", "colour"])
    async def hex(self, ctx, *, col):
        hexcol = str(col).replace("#", "")
        if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', hexcol):
            raise commands.CommandError(message="Invalid hex color")

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
        embed = discord.Embed(title="Reminder", colour=0x8630bf)
        date = search_dates(string, settings={"TIMEZONE": "UTC"})
        if date and date[-1][1]:
            embed.timestamp = date[-1][1]
        embed.description = string.split("|")[0]
        embed.set_footer(text=str(ctx.message.author.name) + '#' +  str(ctx.message.author.discriminator), icon_url=ctx.message.author.avatar_url)
        await ctx.message.delete()
        await ctx.send(embed=embed, content='')

    @commands.command(aliases=["id"])
    async def snowflake(self, ctx, *, snowflake):
        snowflake =int(snowflake)
        embed = discord.Embed(title="Snowflake " + bin(snowflake)[2:], colour=0x7289DA)
        embed.description = "**Timestamp**: " + datetime.utcfromtimestamp(((snowflake >> 22) + 1420070400000) / 1000).strftime('%c') \
                          + "\n**Internal worker ID**: " + str((snowflake & 0x3E0000) >> 17) \
                          + "\n**Internal process ID**: " + str((snowflake & 0x1F000) >> 12) \
                          + "\n**Increment**: " + str(snowflake & 0xFFF)
        embed.set_footer(text="Timestamp: ")
        embed.timestamp = datetime.utcfromtimestamp(((snowflake >> 22) + 1420070400000) / 1000)
        await ctx.send(embed=embed, content='')

def setup(bot):
    bot.add_cog(Misc(bot))