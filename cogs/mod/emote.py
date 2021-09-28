import discord
from discord.ext import commands
from PIL import Image
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
        
        try:
            ret = await ctx.guild.create_custom_emoji(name=name, image=emoji)
            await ctx.reply(f'Emote {ret} created successfully')
        except discord.HTTPException as e:
            if e.code == 30008:
                hint = '`\nHint: `Use %aemote to put static emotes into animated emote slots'
                e.text += hint 
                e.args = (e.args[0] + hint,)
            raise e

    @commands.command(name='aemote', aliases=['aemoji'])
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.guild_only()
    async def aemote(self, ctx, *, args=None):
        '''Adds an emote with a specified name, adding an static image into a 1 frame animated emote slot
        NOTE: This does not support animated files, for those use %emote
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

        # Turn image into a static gif
        image = Image.open(io.BytesIO(emoji)).quantize()
        output = io.BytesIO()
        image.save(output, 'GIF', append_images=(image,), save_all=True, duration=10, loop=1, optimize=False, disposal=2)

        ret = await ctx.guild.create_custom_emoji(name=name, image=output.getvalue())
        await ctx.reply(f'Emote {ret} created successfully')

def setup(bot):
    bot.add_cog(Emote(bot))