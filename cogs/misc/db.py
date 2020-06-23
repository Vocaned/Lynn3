from discord.ext import commands
import discord
from BotUtils import splitMessage
import database

class db(commands.Cog):
    """Database commands."""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def location(self, ctx, *, location=None):
        """Get or set current location.
        Used for weather command
        Add (hidden) after location to prevent your location from being visible to others"""
        if not location:
            loc = await database.getValue('users', ctx.author.id, 'location')
            if not loc:
                await ctx.send('No location set.')
            else:
                await ctx.send(f'your current location is "{loc}"')
        else:
            loc = await database.setUser(ctx.author.id, 'location', location)
            await ctx.send('Location set.')

def setup(bot):
    bot.add_cog(db(bot))
    