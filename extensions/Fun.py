import discord
from discord.ext import commands
from datetime import datetime
import random
from urllib import parse
from BotUtils import REST
import asyncio

'''Games and stuff'''


class Fun(commands.Cog):
	'''Fun'''

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
		'''Generates a game of minesweeper.
		args = `width height bombs (nospoil)`'''
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
		await ctx.send(embed=embed, content='')

	@commands.command(name='trivia')
	async def trivia(self, ctx, *, difficulty='random', streak=0):
		'''Generates trivia questions.
		Difficulty can be Easy, Medium, Hard or Random
		(default: Random)
		Ignore the streak parameter, thanks :)'''

		multiNames = ['\U0001F1E6', '\U0001F1E7', '\U0001F1E8', '\U0001F1E9']
		boolNames = ['\U00002611', '\U0001F1FD']
		continueName = '\U0001F501'

		if streak != 0 and ctx.message:
			raise commands.CommandError('%Too many arguments. Are you trying to cheat?')

		if difficulty.lower() in ('easy', 'medium', 'hard'):
			dif = '&difficulty='+difficulty.lower()
		elif difficulty.lower() == 'random':
			dif = ''
		else:
			raise commands.CommandError('%Invalid difficulty')

		data = await REST('https://opentdb.com/api.php?amount=1&encode=url3986'+dif)
		if data['response_code'] != 0:
			raise commands.CommandError(f'%API error '+str(data['response_code']))

		data = data['results'][0]

		if data['type'] == 'multiple':
			answers = [data['correct_answer']] + data['incorrect_answers']
			random.shuffle(answers)
		else:
			answers = ['True', 'False']
		ansIndex = answers.index(data['correct_answer'])

		if data['difficulty'] == 'easy':
			col = 0x00FF00
		elif data['difficulty'] == 'medium':
			col = 0xFFFF00
		elif data['difficulty'] == 'hard':
			col = 0xFF0000

		embed = discord.Embed(title=f'Trivia - {parse.unquote(data["category"])}', color=col)
		embed.description = f'```{parse.unquote(data["question"])}```'
		embed.set_footer(text=f'Difficulty: {data["difficulty"]}. Data provided by Open Trivia DB (PixelTail Games)')

		if data['type'] == 'multiple':
			for i in range(4):
				embed.add_field(name=multiNames[i], value=parse.unquote(answers[i]))
			nameList = multiNames
		elif data['type'] == 'boolean':
			embed.add_field(name=boolNames[0], value='True')
			embed.add_field(name=boolNames[1], value='False')
			nameList = boolNames
		msg = await ctx.send(ctx.author.mention, embed=embed)
		for name in nameList:
			await msg.add_reaction(name)

		def check(reaction, user):
			return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in nameList
		try:
			r,u = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
			guessIndex = nameList.index(str(r))
			if guessIndex == ansIndex:
				results = f'{ctx.author.mention}, Correct!\n{nameList[ansIndex]} - {parse.unquote(data["correct_answer"])}'
				streak += 1
				correct = True
			else:
				results = f'{ctx.author.mention}, Wrong!\nYou picked {nameList[guessIndex]} - {parse.unquote(answers[guessIndex])}\nThe answer was {nameList[ansIndex]} - {parse.unquote(data["correct_answer"])}\n'
				correct = False
		except asyncio.TimeoutError:
			results = f'{ctx.author.mention}, Ran out of time!\nThe answer was {nameList[ansIndex]} - {parse.unquote(data["correct_answer"])}'
			correct = False
		hadStreak = False
		if streak != 0:
			hadStreak = True
			endStreak = f'\n\nYour streak ended with {str(streak)}x streak'
			curStreak = f'\n\nYou currently have a {str(streak)}x streak'
			if correct:
				fullResults = results + curStreak
			else:
				fullResults = results + endStreak
				streak = 0
		else:
			fullResults = results

		resultsMsg = await ctx.send(f'{fullResults}\nClick {continueName} within 10 seconds to continue.')
		await resultsMsg.add_reaction(continueName)

		def check2(reaction, user):
			return user == ctx.author and reaction.message.id == resultsMsg.id and str(reaction.emoji) == continueName
		try:
			r,u = await self.bot.wait_for('reaction_add', timeout=10.0, check=check2)
			ctx.message = None
			await ctx.invoke(ctx.command, difficulty=difficulty, streak=streak)
		except asyncio.TimeoutError:
			if hadStreak:
				results += endStreak
			await resultsMsg.edit(content=results)
			await resultsMsg.remove_reaction(continueName, self.bot.user)

	games = {}
	hangmanMaxTries = 8

	def hangmanMsg(self, ctx, game: dict) -> str:
		# TODO: Embed messages
		chars = [c for c in game["word"]]
		for i in range(len(chars)):
			if chars[i] in game['right']:
				chars[i] = f'__{chars[i]}__'
			else:
				chars[i] = '\\_'

		message = f"""
{ctx.author.mention}
{' '.join(chars)}
You have {game['left']} guesses left.

Wrong guesses: {', '.join([c for c in game['wrong']])}

Type `{ctx.prefix}hangman [guess]` to guess a letter or a word, or `{ctx.prefix}hangman -` to stop the current game.
"""

		return message

	
	@commands.command(name='hangman')
	# https://github.com/first20hours/google-10000-english/blob/master/google-10000-english.txt
	# all words under 5 characters removed
	async def hangman(self, ctx, *, guess=''):
		if str(ctx.author.id) in self.games:
			game = self.games[str(ctx.author.id)]
		else:
			game = None

		if not guess:
			if not game:
				with open('hangman.txt', 'r') as f:
					word = random.choice(f.readlines()).replace('\n', '')
				self.games[str(ctx.author.id)] = {
					'word': word,
					'wrong': '',
					'right': '',
					'tries': 0,
					'left': self.hangmanMaxTries
				}
				await ctx.send(self.hangmanMsg(ctx, self.games[str(ctx.author.id)]))
			else:
				await ctx.send(self.hangmanMsg(ctx, game))
		elif not game:
			await ctx.send(f'A game is not running. Type `{ctx.prefix}hangman` to start a game of hangman.')
		else:
			if guess == '-':
				await ctx.send(f'Stopped the game. The word was {game["word"]}')
				del self.games[str(ctx.author.id)]
			elif len(guess) != 1:
				game['tries'] += 1
				if game["word"] == guess:
					await ctx.send(f'Correct! You got the word `{game["word"]}` in {game["tries"]} guesses!')
					del self.games[str(ctx.author.id)]
				else:
					game['left'] += 1
					await ctx.send(f'Incorrect!\n{self.hangmanMsg(ctx, game)}')
			else:
				if guess in game['right'] or guess in game['wrong']:
					await ctx.send(f'You have already guessed this letter!\n{self.hangmanMsg(ctx, game)}')
				else:
					game['tries'] += 1
					if guess in game['word']:
						game['right'] += guess
						await ctx.send(f'Correct!\n{self.hangmanMsg(ctx, game)}')
						won = True
						for char in game['word']:
							if char not in game['right']:
								won = False
						if won:
							await ctx.send(f'You got the word `{game["word"]}` in {game["tries"]} guesses!')
							del self.games[str(ctx.author.id)]
					else:
						game['wrong'] += guess
						game['left'] -= 1
						await ctx.send(f'Incorrect!\n{self.hangmanMsg(ctx, game)}')
		
		if game and game['left'] <= 1:
			await ctx.send(f'You lost! The word was {game["word"]}')
			del self.games[str(ctx.author.id)]


def setup(bot):
	bot.add_cog(Fun(bot))