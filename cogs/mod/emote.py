import discord
from discord.ext import commands
from BotUtils import REST
import aiohttp
import io
class Emote(commands.Cog):
    '''Emote'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='emote', aliases=['emoji'])
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.guild_only()
    async def emote(self, ctx, *, args):
        '''Adds an emote with a specified name
        args = [name] when image is an attachment, [url] [name] when uploading from URL
        '''
        if ctx.message.attachments:
            emoji = await ctx.message.attachments[0].read()
        else:
            emoji = await REST(args.split(' ')[0], returns='raw')

        ret = await ctx.guild.create_custom_emoji(name=' '.join(args.split(' ')[1:]), image=emoji)
        await ctx.send(f'Emote {ret} created successfully')

def setup(bot):
    bot.add_cog(Emote(bot))