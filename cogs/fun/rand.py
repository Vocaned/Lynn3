import discord
import random
from discord.ext import commands
from BotUtils import REST
from config import perchanceInstance

class Random(commands.Cog):
    '''Random'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dice', aliases=['die', 'roll'])
    async def dice(self, ctx, *, args='1d6'):
        """Rolls n dice with set amount of faces. Default 1d6. For example:
        1d6 = 1 dice with 6 faces.
        2d10 = 2 dices with 10 faces each."""
        if not 'd' in args:
            n = int(args)
            f = 6
        else:
            n = int(args.split('d')[0])
            f = int(args.split('d')[1])

        if n == 0:
            await ctx.reply('You roll 0 dice. Nothing happens.')
            return
        if f == 0:
            await ctx.reply(f"You roll {n} {'dice' if n > 1 else 'die'} with 0 faces. The world implodes as your zero-dimensional {'dice' if n > 1 else 'die'} hit the table.")
            return
        
        if f < 0:
            await ctx.reply(f"You try to roll {n} {'dice' if n > 1 else 'die'} with negative faces, but you realize that you're all out of negative-dimensional dice.")
            return
        if n < 0:
            roll = random.randint(abs(n), abs(n)*f)
            await ctx.reply(f"You roll negative {n} dice. The dice jump from the table back into your hand. You rolled **{roll}**!")
            return

        roll = random.randint(n, n*f)
        await ctx.reply(f"You roll {n} {'dice' if n > 1 else 'die'} with {f} face{'s' if f > 1 else ''}. You rolled **{roll}**!")

    @commands.command(name='coinflip', aliases=['coin', 'flip'])
    async def coinflip(self, ctx):
        """Flips a coin"""
        flip = random.randint(1, 6001)
        if flip == 0:
            await ctx.reply('You flip a coin. It lands on its edge!')
        else:
            await ctx.reply(f"You flip a coin. It lands on **{'heads' if flip < 3000 else 'tails'}**.")

    @commands.command(name='choose', aliases=['pick', 'select'])
    async def choose(self, ctx, *, choises):
        """Enter a list of things (seperated with a comma) and the bot will pick one at random"""
        await ctx.reply(f"Picked **{random.choice(choises.split(',')).strip()}**.")

    @commands.command(name='perchance')
    async def perchance(self, ctx, *, generator):
        """Output from a generator on https://perchance.org/"""
        await ctx.reply(await REST(f'{perchanceInstance}/api?list=output&generator={generator}'))

def setup(bot):
    bot.add_cog(Random(bot))
