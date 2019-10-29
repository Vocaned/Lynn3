import discord
from discord.ext import commands
from datetime import datetime
import random
from urllib import parse
from BotUtils import REST
import asyncio

"""Games and stuff"""


class Fun(commands.Cog):
	"""Fun"""

	def __init__(self, bot):
		self.bot = bot

	def generateMinesweeper(self, width, height, bombs):
		grid = []
		bomb = []
		for i in range(height):
			grid.append([0]*width)
		while bombs > 0:
			x = random.randint(0, width-1)
			y = random.randint(0, height-1)
			if grid[y][x] != 'x':
				grid[y][x] = 'x'
				bomb.append((x, y))
				bombs-=1

		for loc in bomb:
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
				if grid[loc[1]-1][loc[0]] != 'x':
					grid[loc[1]-1][loc[0]]+=1
			if canUp and canLeft:
				if grid[loc[1]-1][loc[0]-1] != 'x':
					grid[loc[1]-1][loc[0]-1]+=1
			if canUp and canRight:
				if grid[loc[1]-1][loc[0]+1] != 'x':
					grid[loc[1]-1][loc[0]+1]+=1
			if canDown:
				if grid[loc[1]+1][loc[0]] != 'x':
					grid[loc[1]+1][loc[0]]+=1
			if canDown and canLeft:
				if grid[loc[1]+1][loc[0]-1] != 'x':
					grid[loc[1]+1][loc[0]-1]+=1
			if canDown and canRight:
				if grid[loc[1]+1][loc[0]+1] != 'x':
					grid[loc[1]+1][loc[0]+1]+=1
			if canLeft:
				if grid[loc[1]][loc[0]-1] != 'x':
					grid[loc[1]][loc[0]-1]+=1
			if canRight:
				if grid[loc[1]][loc[0]+1] != 'x':
					grid[loc[1]][loc[0]+1]+=1

		return grid

	@commands.command(name='minesweeper')
	async def minesweeper(self, ctx, *, args=None):
		"""Generates a game of minesweeper.
		args = `width height bombs (nospoil)`"""
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
					output += '\N{BOMB}'
				if spoil: output += '||'
			output += '\n'
		embed = discord.Embed(title='Minesweeper', colour=0xFFA500)
		embed.description = output
		embed.timestamp = datetime.utcnow()
		await ctx.send(embed=embed, content="")

	multiNames = ["\U0001F1E6", "\U0001F1E7", "\U0001F1E8", "\U0001F1E9"]
	boolNames = ["\U00002714", "\U00002716"]

	@commands.command(name='trivia')
	async def trivia(self, ctx, *, difficulty="random", streak=0):
		"""Generates trivia questions.
		Difficulty can be Easy, Medium, Hard or Random
		(default: Random)
		Ignore the streak parameter, thanks :)"""

		if streak != 0 and ctx.message:
			raise commands.CommandError("%Too many arguments. Are you trying to cheat?")

		validdiffs = ("easy", "medium", "hard")
		if difficulty.lower() in validdiffs:
			dif = "&difficulty=" + difficulty.lower()
		elif difficulty.lower() == "random":
			dif = ""
		else:
			raise commands.CommandError("%Invalid difficulty")

		data = await REST("https://opentdb.com/api.php?amount=1&encode=url3986"+dif)
		if data["response_code"] != 0:
			raise commands.CommandError("%API error " + str(data["response_code"]))

		data = data["results"][0]

		if data["type"] == "multiple":
			answers = [data["correct_answer"]] + data["incorrect_answers"]
			random.shuffle(answers)
		else:
			answers = ["True", "False"]
		ansIndex = answers.index(data["correct_answer"])

		if data["difficulty"] == "easy":
			col = 0x00FF00
		elif data["difficulty"] == "medium":
			col = 0xFFFF00
		elif data["difficulty"] == "hard":
			col = 0xFF0000

		embed = discord.Embed(title='Trivia - ' + parse.unquote(data["category"]), color=col)
		embed.description = "```" + parse.unquote(data["question"]) + "```"
		embed.set_footer(text="Difficulty: " + data["difficulty"] + ". Data provided by Open Trivia DB (PixelTail Games)")

		if data["type"] == "multiple":
			for i in range(4):
				embed.add_field(name=self.multiNames[i], value=parse.unquote(answers[i]))
			nameList = self.multiNames
		elif data["type"] == "boolean":
			embed.add_field(name=self.boolNames[0], value="True")
			embed.add_field(name=self.boolNames[1], value="False")
			nameList = self.boolNames
		msg = await ctx.send(embed=embed)
		for name in nameList:
			await msg.add_reaction(name)

		def check(reaction, user):
			return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in nameList
		try:
			r,u = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
			guessIndex = nameList.index(str(r))
			if guessIndex == ansIndex:
				results = "Correct!\n" + nameList[ansIndex] + " - " + parse.unquote(data["correct_answer"])
				streak += 1
				correct = True
			else:
				results = "Wrong!\nYou picked " + nameList[guessIndex] + " - " + parse.unquote(answers[guessIndex]) + "\nThe answer was " + nameList[ansIndex] + " - " + parse.unquote(data["correct_answer"]) + "\n"
				correct = False
		except asyncio.TimeoutError:
			results = "Ran out of time!\nThe answer was " + nameList[ansIndex] + " - " + parse.unquote(data["correct_answer"])
			correct = False
		hadStreak = False
		if streak != 0:
			hadStreak = True
			endStreak = "\n\nYour streak ended with " + str(streak)+"x"
			curStreak = "\n\nYou currently have a " + str(streak) + "x streak"
			if correct:
				fullResults = results + curStreak
			else:
				fullResults = results + endStreak
				streak = 0
		else:
			fullResults = results

		resultsMsg = await ctx.send(fullResults+"\nClick \U0001F501 within 10 seconds to continue.")
		await resultsMsg.add_reaction("\U0001F501")

		def check2(reaction, user):
			return user == ctx.author and reaction.message.id == resultsMsg.id and str(reaction.emoji) == "\U0001F501"
		try:
			r,u = await self.bot.wait_for('reaction_add', timeout=10.0, check=check2)
			ctx.message = None
			await ctx.invoke(ctx.command, difficulty=difficulty, streak=streak)
		except asyncio.TimeoutError:
			if hadStreak:
				results += endStreak
			await resultsMsg.edit(content=results)
			await resultsMsg.remove_reaction("\U0001F501", self.bot.user)


def setup(bot):
	bot.add_cog(Fun(bot))