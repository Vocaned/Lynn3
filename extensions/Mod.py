import discord
from discord.ext import commands


class Mod(commands.Cog):
    """Mod"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge', aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int=None):
        """Purge an amount of messages in a channel"""
        if amount>500 or amount<0:
            return await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
        await ctx.message.delete()
        await ctx.message.channel.purge(limit=amount)
        await ctx.send(f'Sucesfully deleted **{int(amount)}** messages!', delete_after=5)

    @commands.command(name='echo', aliases=['say', 'repeat'])
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, message):
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Mod(bot))
