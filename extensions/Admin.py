from discord.ext import commands
import traceback
import discord
import textwrap
from contextlib import redirect_stdout
import io
import copy
import os
import time
import subprocess
import config
import sys
import math
from Lynn import errors

class Admin(commands.Cog):
    """Admin-only commands."""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        global errors
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        try:
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
        except:
            pass

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send('This command has been disabled.')
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.UserInputError):
            await ctx.send("Invalid input. Usage:")
            await ctx.send_help(ctx.command)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
            return

        try:
            if hasattr(error, "args") and len(error.args) != 0 and error.args[0][0] == "%":
                await ctx.send(error.args[0][1:])
        except:
            pass

        print("Ignoring exception in " + str(ctx.command), file=sys.stderr)
        errors = "\n".join(traceback.format_exception(type(error), error, error.__traceback__))

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command(hidden=True)
    @commands.is_owner()
    async def modules(self, ctx):
        """Lists all loaded modules"""
        await ctx.send("Loaded modules: ```" + "\n".join(self.bot.extensions) + "```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        self.bot.load_extension(config.cogDir+"."+module)
        await ctx.message.add_reaction('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        self.bot.unload_extension(config.cogDir+"."+module)
        await ctx.message.add_reaction('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module.
        Module can be \"all\""""
        start = time.time()
        if module == "all":
            n = 0
            for file in os.listdir(config.cogDir+'/'):
                if str(file).endswith(".py"):
                    file = file[:-3]
                    self.bot.reload_extension(config.cogDir+"."+file)
                    n+=1
            end = time.time()
            await ctx.send('Reloaded `'+str(n)+'` modules in `' + str(round((end-start)*1000, 2)) + 'ms`.')
        else:
            self.bot.reload_extension(config.cogDir+"."+module)
            end = time.time()
            await ctx.send('Reloaded `'+str(module)+'` in `'+str(round((end-start)*1000, 2))+'ms`.')

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
    async def git(self, ctx, *, action):
        if action == "pull":
            p = subprocess.check_output(["git", "pull", config.gitURI], stderr=subprocess.STDOUT, timeout=30).decode("utf-8")
            w = p.split()
            try:
                commits = w[w.index("Updating") + 1]

                p2 = subprocess.check_output(["git", "log", "--format=%h %an | %B%n%N", commits], stderr=subprocess.STDOUT, timeout=30)
                p2 = "\n".join([line for line in p2.decode("utf-8").split('\n') if line.strip() != '']) + "\n\nRemember to reload modules!"
            except:
                p2 = ""
            await ctx.message.clear_reactions()
            # 1993 = 2000 - len("```\n```")
            if len(p) + len(p2) >= 1993:
                if len(p) >= 1994:
                    await ctx.send("Git output too long. Changes were still applied. Remember to reload modules!")
                else:
                    await ctx.send("```" + p + "```")
            else:
                await ctx.send("```" + p + "\n" + p2 + "```")
        else:
            raise commands.UserInputError()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debug(self, ctx):
        global errors
        if not errors:
            await ctx.send("No errors logged.")
        else:
            for msg in [errors[i:i+1990] for i in range(0, len(errors), 1990)]:
                await ctx.send("```py\n" + msg.replace("```", "`\U00002063``") + "```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def activity(self, ctx, *, text=""):
        if text:
            text = text.lower()
            if text.startswith('listening to'):
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text[13:]))
            elif text.startswith('watching'):
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text[9:]))
            elif text == "online":
                await self.bot.change_presence(status="online")
            elif text == "idle":
                await self.bot.change_presence(status="idle")
            elif text == "dnd":
                await self.bot.change_presence(status="dnd")
            else:
                await self.bot.change_presence(activity=discord.Game(name=text))
            await ctx.message.add_reaction('\N{OK HAND SIGN}')
        else:
            await self.bot.change_presence(activity=None, status="online")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Goodbye!")
        await ctx.message.add_reaction("\N{WAVING HAND SIGN}")
        await self.bot.close()

def setup(bot):
    bot.add_cog(Admin(bot))