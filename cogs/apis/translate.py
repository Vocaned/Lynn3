from discord.ext import commands
from BotUtils import REST, escapeURL
from datetime import datetime
import discord

class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='translate', aliases=['trans'])
    async def TranslateAPI(self, ctx, *, query):
        """Translate stuff using Google Translate.
        Defaults to Auto-Detect -> English
        use 2 letter country codes i guess lol too lazy to make this bot any good"""

        inlang = 'auto'
        outlang = 'en'

        newquery = []
        for word in query:
            if word.startswith('from:') and word != 'from:': # check that there's no space after from:
                inlang = word.split(':')[1]
            elif word.startswith('to:') and word != 'to:':
                outlang = word.split(':')[1]
            else:
                newquery.append(word)
        query = ' '.join(newquery)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        data = await REST(f'https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&ie=UTF-8&oe=UTF-8&sl={inlang}&tl={outlang}&q={query}', headers=headers)

        fromlang = data[2]

        confidence = ''
        if data[6] and data[6] != 1:
            confidence = f'(confidence: {round(data[6]*100)}%)'

        await ctx.send(f'{fromlang} -> {outlang}: {data[0][0][0]} {confidence}')


def setup(bot):
    bot.add_cog(Translate(bot))