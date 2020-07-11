import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from dateparser.search import search_dates

class Reminders(commands.Cog):
    '''Reminders'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['remind', 'remindme'])
    async def reminder(self, ctx, *message):
        '''Sets a reminder.
        Times are in UTC by default'''

        date = search_dates(message, settings={"TIMEZONE": "UTC"})
        date = date[0]
        await ctx.send("I'll remind you on " + date.strftime("%c") + "!\n*(please dont use this command for anything super important, reminders might just fail and never actually remind you because I don't have the motivation to make this bot good)*")
        await asyncio.sleep((date-datetime.utcnow()).total_seconds())
        
        embed = discord.Embed(title='Reminder', colour=0x8630bf)
        embed.description = ' '.join(message)
        await ctx.send(embed=embed, content=ctx.author.mention)

def setup(bot):
    bot.add_cog(Reminders(bot))