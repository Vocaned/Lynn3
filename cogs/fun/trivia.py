from discord.ext import commands
import discord
import random
from BotUtils import REST
import asyncio
from urllib import parse

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    bot.add_cog(Trivia(bot))