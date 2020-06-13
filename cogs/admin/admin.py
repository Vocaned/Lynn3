from discord.ext import commands
import discord
from BotUtils import splitMessage

class Admin(commands.Cog):
    """Admin-only commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def debug(self, ctx):
        with open('error.dat', 'r') as errors:
            error = errors.read()
            if not error:
                await ctx.send('No errors logged.')
            else:
                for msg in splitMessage(error, highlight='py'):
                    await ctx.send(msg)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def activity(self, ctx, *, text=''""''):
        if text:
            text = text.lower()
            if text.startswith('listening to'):
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text[13:]))
            elif text.startswith('watching'):
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text[9:]))
            elif text == 'online':
                await self.bot.change_presence(status='online')
            elif text == 'idle':
                await self.bot.change_presence(status='idle')
            elif text == 'dnd':
                await self.bot.change_presence(status='dnd')
            else:
                await self.bot.change_presence(activity=discord.Game(name=text))
            await ctx.message.add_reaction('\N{OK HAND SIGN}')
        else:
            await self.bot.change_presence(activity=None, status='online')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.message.add_reaction('\N{WAVING HAND SIGN}')
        await ctx.send('Goodbye!')
        await self.bot.close()

def setup(bot):
    bot.add_cog(Admin(bot))