import discord
import  base64
import binascii
from discord.ext import commands

class Data(commands.Cog):
    '''Data'''

    def __init__(self, bot):
        self.bot = bot

    async def send(self, ctx, string: bytes) -> str:
        await ctx.send(ctx.author.mention + '```' + string.decode('utf-8', 'ignore').replace('```', '`\U00002063``') + '```')

    # BASE
    @commands.group(name='decode')
    async def decode(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    
    @commands.group(name='encode')
    async def encode(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    # BASE 64
    @decode.command(name='base64', aliases=['b64'])
    async def dbase64(self, ctx, *, val):
        try:
            await self.send(ctx, base64.b64decode(val.encode()))
        except binascii.Error:
            await ctx.send('Could not parse base64')

    @encode.command(name='base64', aliases=['b64'])
    async def ebase64(self, ctx, *, val):
        await self.send(ctx, base64.b64encode(val.encode()))

    # HEX
    @decode.command(name='hex', aliases=['base8', 'hexadecimal'])
    async def dhex(self, ctx, *, val):
        try:
            await self.send(ctx, bytes.fromhex(val))
        except:
            await ctx.send('Could not parse hex')
        
    @encode.command(name='hex', aliases=['base8', 'hexadecimal'])
    async def ehex(self, ctx, *, val):
        await self.send(ctx, binascii.hexlify(val.encode()))

    # BINARY
    @decode.command(name='binary', aliases=['base2', 'bin'])
    async def dbin(self, ctx, *, val):
        try:
            n = int(val.replace(' ', ''), 2)
            await self.send(ctx, n.to_bytes((n.bit_length() + 7) // 8, 'big').decode())
        except (ValueError, binascii.Error):
            await ctx.send('Could not parse binary')

    @encode.command(name='binary', aliases=['base2', 'bin'])
    async def ebin(self, ctx, *, val):
        await self.send(ctx, bin(int.from_bytes(val.encode(), 'big')))


def setup(bot):
    bot.add_cog(Data(bot))
