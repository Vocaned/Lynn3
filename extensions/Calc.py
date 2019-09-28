import discord
from discord.ext import commands
import calclib

class Calculator(commands.Cog):
     """Calculator"""

     def __init__(self, bot):
          self.bot = bot

     @commands.command(name='calculator', aliases=["calc", "math"])
     async def calculator(self, ctx, *, expr):
          """Calculator""",
          expr = calclib.tokenize(expr)
          expr = calclib.implicit_multiplication(expr)
          expr = calclib.to_rpn(expr)
          expr = calclib.eval_rpn(expr)
          await ctx.send("> " + str(expr))

def setup(bot):
    bot.add_cog(Calculator(bot))