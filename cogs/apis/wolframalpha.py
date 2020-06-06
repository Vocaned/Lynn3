from discord.ext import commands
from BotUtils import REST, escapeURL, getAPIKey
import discord
import aiohttp

class WolframAlpha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wolframalpha', aliases=['wa', 'wolfram'])
    async def wolframalpha(self, ctx, *, query):
        # Discord can't download the file so we do it ourselves
        async with aiohttp.ClientSession() as s:
            async with s.get(f"http://api.wolframalpha.com/v1/simple?appid={getAPIKey('wolframalpha')}&layout=labelbar&background=2F3136&foreground=white&i={escapeURL(query)}") as r:
                data = await r.read()
                if len(data) < 1000: # HACK: Probably error msg if response is under 1000 bytes
                    await ctx.send(f'{ctx.author.mention} ' + data.decode('utf-8'))
                    return
                with open('wolfram.png', 'wb') as f:
                    f.write(await r.read())
        answer = discord.File('wolfram.png', filename='wolfram.png')
        await ctx.send(files=[answer])

def setup(bot):
    bot.add_cog(WolframAlpha(bot))