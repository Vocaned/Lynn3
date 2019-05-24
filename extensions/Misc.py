import discord
from discord.ext import commands
from datetime import datetime
import subprocess
import json
import math
import requests


"""Misc commands"""


class Misc(commands.Cog):
    """Misc"""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.message.guild.id != 485076757733572608

    @commands.command()
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
    async def match(self, ctx, matchid):
        m = matchid.split("%20")[1]
        requests.get("https://csgo-stats.com/match/" + m)
        await ctx.message.delete()
        embed = discord.Embed(title='CS:GO Match', colour=0xadd8e6)
        embed.description = "https://csgo-stats.com/match/" + m
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed, content="")
    
    @commands.command()
    async def lgbt(self, ctx):
        await ctx.message.delete()
        await ctx.send("<a:lgbt1:559809814943891457> <a:lgbt2:559809821377822720>")
        

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(Misc(bot))
