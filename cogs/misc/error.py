from discord.ext import commands
import discord
import sys
from Lynn import errors
import traceback
import math

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        if isinstance(error, commands.NSFWChannelRequired):
            await ctx.send('This command can only be used in NSFW channels.')
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send('This command has been disabled in this server.')
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('This command is on cooldown, please retry in {}s.'.format(math.ceil(error.retry_after)))
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
            await ctx.send('Invalid input. Usage:')
            await ctx.send_help(ctx.command)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to use this command.')
            return

        try:
            if hasattr(error, 'args') and len(error.args) != 0:
                await ctx.send(error.args[0][1:])
        except:
            pass

        print('Ignoring exception in {}'.format(ctx.command), file=sys.stderr)
        errors = '\n'.join(traceback.format_exception(type(error), error, error.__traceback__))

def setup(bot):
    bot.add_cog(Error(bot))