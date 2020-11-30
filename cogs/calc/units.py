import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import subprocess
import sys
from BotUtils import shellCommand

'''Units commands'''


class Units(commands.Cog):
    '''Units'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['convert', 'unit'])
    async def units(self, ctx, *, source, out):
        await shellCommand(ctx, ['units', '-1t', source, out], realtime=False)


def setup(bot):
    bot.add_cog(Units(bot))