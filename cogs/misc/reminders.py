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

        date = search_dates(' '.join(message), settings={"TIMEZONE": "UTC"})
        if not date:
            await ctx.message.reply('No date or time found in your message')
            return
        elif len(date) > 1:
            await ctx.send(f'Multiple dates found in your message. Using the first one ("{date[0][0]}")')
        date = date[0]
        await ctx.send("I'll remind you on " + date[1].strftime("%c") + "!\n*(please dont use this command for anything super important, reminders might just fail and never actually remind you because I don't have the motivation to make this bot good)*")
        await asyncio.sleep((date[1]-datetime.utcnow()).total_seconds())
        
        embed = discord.Embed(title='Reminder', colour=0x8630bf)
        embed.description = ' '.join(message)
        await ctx.message.reply(embed=embed, content=ctx.author.mention)

def setup(bot):
    bot.add_cog(Reminders(bot))