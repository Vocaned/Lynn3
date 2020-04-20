import discord
import  base64
import binascii
from discord.ext import commands

class Data(commands.Cog):
    '''Data'''

    def __init__(self, bot):
        self.bot = bot

    # BASE
    @commands.group(name='decode', aliases=['decoding'])
    async def decode(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()
    
    @commands.group(name='encode', aliases=['encoding'])
    async def encode(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    # BASE 64
    @decode.command(name='base64', aliases=['b64'])
    async def dbase64(self, ctx, *, val):
        try:
            await ctx.send(f'{ctx.author.mention}, `{base64.b64decode(val.encode()).decode("utf-8", "ignore")}`')
        except binascii.Error:
            await ctx.send('Could not parse base64')

    @encode.command(name='base64', aliases=['b64'])
    async def ebase64(self, ctx, *, val):
        await ctx.send(f'{ctx.author.mention}, `{base64.b64encode(val.encode()).decode()}`')


def setup(bot):
    bot.add_cog(Data(bot))
