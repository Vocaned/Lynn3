from discord.ext import commands
import discord
import io
import os
import textwrap
from contextlib import redirect_stdout
import traceback
import copy
from BotUtils import shellCommand

class Eval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def su(self, ctx, who: discord.User, *command):
        """Run a command as another user."""
        msg = copy.copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + " ".join(command)
        new_ctx = await self.bot.get_context(msg)
        await self.bot.invoke(new_ctx)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudo(self, ctx, *command):
        """Run a command as a superuser.
        Bypasses filters."""
        msg = copy.copy(ctx.message)
        msg.content = ctx.prefix + " ".join(command)
        new_ctx = await self.bot.get_context(msg)
        return await new_ctx.command.reinvoke(new_ctx)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def backdoor(self, ctx, *, cmd):
        """Does some shady stuff"""
        await shellCommand(ctx, cmd, timeout=30, verbose=True)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def magick(self, ctx, *, cmd):
        """imagemagick"""
        if not ctx.message.attachments:
            raise Exception("No image")
        b = await ctx.message.attachments[0].save("magick")
        if os.path.exists("magickoutput.png"):
            os.remove("magickoutput.png")
        if b == 0:
            raise Exception("Could not save image")
        await shellCommand(ctx, "convert magick "+cmd+" magickoutput.png", timeout=30, silent=True)
        if not os.path.exists("magickoutput.png"):
            raise Exception("no output")
        img = discord.File("magickoutput.png", filename="magick.png")
        await ctx.send(files=[img])

    @commands.command(hidden=True)
    @commands.is_owner()
    async def svg(self, ctx, width, height):
        """inkscape"""
        assert width.isnumeric()
        assert height.isnumeric()

        if not ctx.message.attachments:
            raise Exception("No image")
        b = await ctx.message.attachments[0].save("svg.svg")
        if os.path.exists("svgoutput.png"):
            os.remove("svgoutput.png")
        if b == 0:
            raise Exception("Could not save image")
        await shellCommand(ctx, f"inkscape -z -w {width} -h {height} svg.svg -e svgoutput.png", timeout=30, silent=True)
        if not os.path.exists("svgoutput.png"):
            raise Exception("no output")
        img = discord.File("svgoutput.png", filename="svg.png")
        await ctx.send(files=[img])

    @commands.command(hidden=True, aliases=["imageconvert"])
    @commands.is_owner()
    async def imgconvert(self, ctx, *, ff):
        """imagemagick convert"""
        if not ctx.message.attachments:
            raise Exception("No image")
        b = await ctx.message.attachments[0].save("magick")
        if os.path.exists("magickoutput."+ff):
            os.remove("magickoutput."+ff)
        if b == 0:
            raise Exception("Could not save image")
        await shellCommand(ctx, "convert magick magickoutput." + ff, timeout=30, silent=True)
        if not os.path.exists("magickoutput."+ff):
            raise Exception("no output")
        img = discord.File("magickoutput."+ff, filename="magick."+ff)
        await ctx.send(files=[img])

    @commands.command(hidden=True, aliases=["videoconvert"])
    @commands.is_owner()
    async def vidconvert(self, ctx, *, ff):
        """ffmpeg convert"""
        if not ctx.message.attachments:
            raise Exception("No video")
        b = await ctx.message.attachments[0].save("ffmpeg")
        if os.path.exists("ffmpeg."+ff):
            os.remove("ffmpeg."+ff)
        if b == 0:
            raise Exception("Could not save video")
        await shellCommand(ctx, "ffmpeg -i ffmpeg -o ffmpeg." + ff, timeout=30, silent=True)
        if not os.path.exists("ffmpeg."+ff):
            raise Exception("no output")
        img = discord.File("ffmpeg."+ff, filename="ffmpeg."+ff)
        await ctx.send(files=[img])

def setup(bot):
    bot.add_cog(Eval(bot))