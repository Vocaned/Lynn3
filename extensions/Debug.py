import discord
from discord.ext import commands
from inspect import getframeinfo, stack
from datetime import datetime
import time

class Debug:
    """Debug"""

    def __init__(self, bot):
        self.bot = bot

    NORMAL = 0
    WARN = 1
    ERROR = 2

    debugOutput = []
    startTime = 0
    exitCode = NORMAL

    def printDebug(self, text):
        caller = getframeinfo(stack()[1][0])
        self.debugOutput.append("["+str(self.exitCode)+"] (" + str(time.time()-self.startTime) + ") " + str(caller.filename) + ":" + str(caller.lineno) + " - " + str(text))

    @commands.command()
    @commands.is_owner()
    async def debug(self, ctx, *, msg=""):
        self.debugOutput = []
        self.exitCode = self.NORMAL
        self.startTime = time.time()

        try:
            """Add stuff to debug here!"""
            self.printDebug("Hello, world!")
            self.printDebug(msg)



        except Exception as e:
            self.exitCode = self.ERROR
            self.printDebug(e)
        
        col = 0x00ff00
        if self.exitCode == self.WARN: col = 0xffff00
        if self.exitCode == self.ERROR: col = 0xff0000

        embed = discord.Embed(title='Debug', colour=col)
        embed.description = "```\n" + "\n".join(self.debugOutput) + "\n```"
        embed.timestamp = datetime.utcnow()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed, content='')

def setup(bot):
    bot.add_cog(Debug(bot))
 
