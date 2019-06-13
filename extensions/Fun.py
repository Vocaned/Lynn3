import discord
from discord.ext import commands
from datetime import datetime
import random
import logging

"""Games and stuff"""


class Fun(commands.Cog):
	"""Fun"""

	def __init__(self, bot):
		self.bot = bot

	#async def __local_check(self, ctx):
		#return ctx.message.guild.id != 485076757733572608

	def generateMinesweeper(self, width, height, bombs):
		grid = []
		bomb = []
		for i in range(height):
			grid.append([0]*width)
		while bombs > 0:
			x = random.randint(0, width-1)
			y = random.randint(0, height-1)
			logging.debug('Adding bomb to: ' + str(x) + ' ' + str(y))
			if grid[y][x] != 'x':
				grid[y][x] = 'x'
				bomb.append((x, y))
				bombs-=1
			else:
				logging.debug('Bomb was already there, trying again...')

		for loc in bomb:
			logging.debug('Doing ' + str(loc))
			canUp = False
			canLeft = False
			canRight = False
			canDown = False
			if loc[1] > 0:
				canUp = True
			if loc[1] < height-1:
				canDown = True
			if loc[0] > 0:
				canLeft = True
			if loc[0] < width-1:
				canRight = True
				
			if canUp:
				# up
				if grid[loc[1]-1][loc[0]] != 'x':
					grid[loc[1]-1][loc[0]]+=1
			if canUp and canLeft:
				# up-left
				if grid[loc[1]-1][loc[0]-1] != 'x':
					grid[loc[1]-1][loc[0]-1]+=1
			if canUp and canRight:
				# up-right
				if grid[loc[1]-1][loc[0]+1] != 'x':
					grid[loc[1]-1][loc[0]+1]+=1
			if canDown:
				# down
				if grid[loc[1]+1][loc[0]] != 'x':
					grid[loc[1]+1][loc[0]]+=1
			if canDown and canLeft:
				# down-left
				if grid[loc[1]+1][loc[0]-1] != 'x':
					grid[loc[1]+1][loc[0]-1]+=1
			if canDown and canRight:
				# down-right
				if grid[loc[1]+1][loc[0]+1] != 'x':
					grid[loc[1]+1][loc[0]+1]+=1
			if canLeft:
				# left
				if grid[loc[1]][loc[0]-1] != 'x':
					grid[loc[1]][loc[0]-1]+=1
			if canRight:
				# right
				if grid[loc[1]][loc[0]+1] != 'x':
					grid[loc[1]][loc[0]+1]+=1
			
		return grid

	@commands.command(name='minesweeper', aliases=['miinaharava'])
	async def minesweeper(self, ctx, *, args=None):
		"""Generates a game of minesweeper.
		args = `width height bombs (nospoil)`"""
		await ctx.message.add_reaction('\N{HOURGLASS}')
		
		spoil = True
		if args != None and len(str(args).split(' ')) > 2:
			width = int(str(args).split(' ')[0])
			height = int(str(args).split(' ')[1])
			bombs = int(str(args).split(' ')[2])
			if 'nospoil' in args:
				spoil = False
		else:
			width = 10
			height = 10
			bombs = 15
		output = ''
		field = Fun.generateMinesweeper(self, width, height, bombs)
		for row in field:
			for c in row:
				if spoil: output += '||'
				if c == 0:
					output += '\N{WHITE LARGE SQUARE}'
				elif c == 1:
					output += '\U00000031\U000020E3'
				elif c == 2:
					output += '\U00000032\U000020E3'
				elif c == 3:
					output += '\U00000033\U000020E3'
				elif c == 4:
					output += '\U00000034\U000020E3'
				elif c == 5:
					output += '\U00000035\U000020E3'
				elif c == 6:
					output += '\U00000036\U000020E3'
				elif c == 7:
					output += '\U00000037\U000020E3'
				elif c == 8:
					output += '\U00000038\U000020E3'
				elif str(c) == 'x':
					output += '\N{bomb}'
				if spoil: output += '||'
			output += '\n'
		embed = discord.Embed(title='Minesweeper', colour=0xFFA500)
		embed.description = output
		embed.timestamp = datetime.utcnow()
		await ctx.message.clear_reactions()
		await ctx.message.add_reaction("\N{OK HAND SIGN}")
		await ctx.send(embed=embed, content="")

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
	bot.add_cog(Fun(bot)) 
