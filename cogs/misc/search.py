import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import re
import time
import subprocess
import sys
from BotUtils import REST, escapeURL, getAPIKey

'''Search commands'''


class Search(commands.Cog):
    '''Search'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ddg', 'duck'])
    async def duckduckgo(self, ctx, *, search):
        await ctx.message.reply('https://duckduckgo.com/?q=' + escapeURL(search))

    @commands.command()
    async def google(self, ctx, *, search):
        await ctx.message.reply('https://www.google.com/search?q=' + escapeURL(search))

    @commands.command(aliases=['yt'])
    async def youtube(self, ctx, *, search):
        data = await REST(f'https://www.googleapis.com/youtube/v3/search?q={escapeURL(search)}&type=video&part=id&regionCode=US&key={getAPIKey("google")}')
        data = data['items']
        if len(data) == 0:
            await ctx.message.reply('No videos found.')
        else:
            await ctx.message.reply('https://youtube.com/watch?v=' + data[0]['id']['videoId'])

def setup(bot):
    bot.add_cog(Search(bot))