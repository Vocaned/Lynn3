from discord.ext import commands
import discord
import sys
import traceback
import math
import logging

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        logging.error('Ignoring exception in {}'.format(ctx.command))
        try:
            with open('error.dat', 'w') as f:
                f.write('\n'.join(traceback.format_exception(type(error), error, error.__traceback__)))
        except:
            logging.error('ERROR: Could not write error into error.dat')

        try:
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
        except:
            pass
  
        errmsg = ''

        try:
            if hasattr(error, 'args'):
                errmsg = f"Error: `{type(error).__name__}: {error}`\n"
        except:
            pass

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            errmsg += _message
            return

        if isinstance(error, commands.NSFWChannelRequired):
            errmsg += 'This command can only be used in NSFW channels.'
            return

        if isinstance(error, commands.DisabledCommand):
            errmsg += 'This command has been disabled in this server.'
            return

        if isinstance(error, commands.CommandOnCooldown):
            errmsg += 'This command is on cooldown, please retry in {}s.'.format(math.ceil(error.retry_after))
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            errmsg += 'You need the **{}** permission(s) to use this command.'.format(fmt)
            return

        if isinstance(error, commands.UserInputError):
            await ctx.message.reply('Invalid input. Usage:')
            await ctx.send_help(ctx.command)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.Forbidden:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            errmsg += 'You do not have permission to use this command.'
            return

        if isinstance(error, commands.ExtensionAlreadyLoaded):
            errmsg += 'Extension already loaded.'
            return
        
        if isinstance(error, commands.ExtensionNotFound):
            errmsg += 'Extension not found.'
            return

        if isinstance(error, commands.ExtensionNotLoaded):
            errmsg += 'Extension not loaded.'
            return
        
        if isinstance(error, commands.ExtensionFailed):
            errmsg += 'Failed to load extension.'
            return
        
        if errmsg:
            await ctx.message.reply(errmsg)

def setup(bot):
    bot.add_cog(Error(bot))