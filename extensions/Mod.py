import discord
from discord.ext import commands


class Mod:
    """Mod"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='purge', aliases=['prune'])
    @commands.has_permissions(manage_guild=True)
    async def purge(self, ctx, amount: int=None):
        """Purge an amount of messages in a channel"""
        if amount>500 or amount<0:
            return await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
        await ctx.message.delete()
        await ctx.message.channel.purge(limit=amount)
        await ctx.send(f'Sucesfully deleted **{int(amount)}** messages!', delete_after=5)

def setup(bot):
    bot.add_cog(Mod(bot))
