import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from inspect import getframeinfo, stack
from datetime import datetime
import time
import re
import requests

class Debug(commands.Cog):
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
    async def debug(self, ctx):
        self.debugOutput = []
        self.exitCode = self.NORMAL
        self.startTime = time.time()

        try:
            """Add stuff to debug here!"""
            replaced = []
            match = re.findall("(?!<):.+?:(?!\\d+?>)", ctx.message.content)
            if match:
                shouldSend = False
                newmsg = ctx.message.content
                for emote in match:
                    if not emote in replaced:
                        em = emote.replace(":", "")
                        self.printDebug("Matched possible emote " + emote)
                        for e in ctx.guild.emojis:
                            if e.name.lower() == em.lower():
                                self.printDebug("Found the emote " + emote)
                                if not e.animated:
                                    self.exitCode = self.WARN
                                    self.printDebug(emote + " wasn't animated!")
                                    continue
                                fullemote = "<a:" + str(em) + ":" + str(e.id) + ">"
                                self.printDebug("Reconstructing message with " + fullemote)
                                newmsg = newmsg.replace(emote, fullemote)
                                replaced.append(emote)
                                shouldSend = True
                if shouldSend:
                    self.printDebug("Getting webhooks")
                    hook = None
                    for h in await ctx.channel.webhooks():
                        if h.name == "EmoteFix":
                            hook = h
                            self.printDebug("Webhook found! ID " + str(hook.id))
                    if hook == None:
                        self.printDebug("Couldn't find the webhook, creating one..")
                        hook = await ctx.channel.create_webhook(name="EmoteFix")
                        self.printDebug("Webhook created! ID " + str(hook.id))
                    await hook.send(content=newmsg, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)
                    self.printDebug("Sent fixed message")
                    #await ctx.message.delete()
            else:
                self.exitCode = self.WARN
                self.printDebug("Didn't find an emote")



        except Exception as e:
            self.exitCode = self.ERROR
            self.printDebug(e)
        
        col = 0x00ff00
        if self.exitCode == self.WARN: col = 0xffff00
        if self.exitCode == self.ERROR: col = 0xff0000

        embed = discord.Embed(title='Debug', colour=col)
        embed.description = "```\n" + "\n-----\n".join(self.debugOutput) + "\n```"
        embed.timestamp = datetime.utcnow()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed, content='')

def setup(bot):
    bot.add_cog(Debug(bot))
 
