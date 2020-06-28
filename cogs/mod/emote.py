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
    async def emote(self, ctx, *, args=None):
        '''Adds an emote with a specified name
        args = [url] [name] when uploading from URL, [name] when image is an attachment
        name can be empty if file name is used
        '''
        if ctx.message.attachments:
            emoji = await ctx.message.attachments[0].read()
            if not args:
                name = '_'.join(ctx.message.attachments[0].filename.split('.')[:-1])
            else:
                name = '_'.join(args.split(' ')[0:])

        else:
            emoji = await REST(args.split(' ')[0], returns='raw')
            if len(args) > 1:
                name = '_'.join(args.split(' ')[1:])
            else:
                name = '_'.join(args.split(' ')[0].split('.')[:-1])
        
        ret = await ctx.guild.create_custom_emoji(name=name, image=emoji)
        await ctx.send(f'Emote {ret} created successfully')

def setup(bot):
    bot.add_cog(Emote(bot))