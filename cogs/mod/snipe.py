import discord
import logging
from discord.ext import commands
from BotUtils import splitMessage, REST, escapeURL, shellCommand
import asyncio
import aiohttp
from io import BytesIO
from subprocess import Popen, TimeoutExpired, PIPE
import emoji
import os
import datetime
import difflib
import re


class Snipe(commands.Cog):
    '''snipe'''

    def __init__(self, bot):
        self.bot = bot
        # type=edited/deleted
        # {
        #  guildID: [(type, Message, datetime), (type, Message, datetime),]
        # }
        self.lastmsgs = {}

    def logMsg(self, type, message):
        if message.guild.id not in self.lastmsgs:
            self.lastmsgs[message.guild.id] = []

        self.lastmsgs[message.guild.id].append((type, message, datetime.datetime.now()))

    @commands.command(name='snipe')
    async def snipe(self, ctx):
        embed = discord.Embed(title="Edits or deletes in the last 30 second")
        embed.set_footer(text=f'Sniped by {ctx.author.name}#{ctx.author.discriminator}')
        valid = {}
        for guild in self.lastmsgs:
            if not self.lastmsgs[guild]:
                continue
            valid[guild] = []
            for msg in self.lastmsgs[guild]:
                # check if edit is expired
                if datetime.datetime.now() - msg[2] > datetime.timedelta(seconds=30):
                    continue

                # Some messages might not have content
                if msg[1].content is None or len(msg[1].content) == 0:
                    if len(msg[1].embeds) > 0:
                        msg[1].content = '[embed]'
                    elif len(msg[1].attachments) > 0:
                        msg[1].content = '[attachment]'
                    else:
                        continue
                
                # Make sure message fits in field
                if len(msg[1].content) > 1024:
                    msg[1].content = msg[1].content[:1020] + '...'

                valid[guild].append(msg)

                # check perms
                if not msg[1].channel.permissions_for(ctx.author).read_messages:
                    continue

                embed.add_field(name=f'{msg[1].author.name}#{msg[1].author.discriminator} {msg[0]} in #{msg[1].channel.name}', value=msg[1].content, inline=False)
        self.lastmsgs = valid

        if len(embed.fields) == 0:
            await ctx.reply('No messages to snipe')
        else:
            await ctx.reply(embed=embed)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message_edit(self, before, after):
        if before.author.bot \
           or before.content == after.content \
           or after.edited_at-after.created_at > datetime.timedelta(seconds=60):
            return
        
        self.logMsg("edited", before)


    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        self.logMsg("deleted", message)


def setup(bot):
    bot.add_cog(Snipe(bot))
