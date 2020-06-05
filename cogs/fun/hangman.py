from discord.ext import commands
import random

class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    games = {}
    hangmanMaxTries = 9

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
You have {game['left']-1} guesses left.

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
    bot.add_cog(Hangman(bot))