from discord.ext import commands
from BotUtils import REST, getAPIKey, isURL
from datetime import datetime
import discord

class OCR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    langs = {
        'arabic': 'ara',
        'bulgarian':'bul',
        'chinese': 'chs',
        'chinese(traditional)': 'cht',
        'croatian': 'hrv',
        'czech': 'cze',
        'danish': 'dan',
        'dutch': 'dut',
        'english': 'eng',
        'finnish': 'fin',
        'french': 'fre',
        'german': 'ger',
        'greek': 'gre',
        'hungarian': 'hun',
        'korean': 'kor',
        'italian': 'ita',
        'japanese': 'jpn',
        'polish': 'pol',
        'portuguese': 'por',
        'russian': 'rus',
        'slovenian': 'slv',
        'spanish': 'spa',
        'swedish': 'swe',
        'turkish': 'tur'
    }

    def getLang(self, lang: str) -> str:
        if lang in self.langs.values():
            return lang

        if lang in self.langs:
            return self.langs[lang]
        
        raise commands.ArgumentParsingError('Invalid language.')
        
    @commands.command(name='ocrlangs', aliases=['ocrlanguages'])
    async def ocrlangs(self, ctx):
        """Shows supported ocr languages"""
        await ctx.reply('```'+'\n'.join(self.langs.keys())+'```')

    @commands.command(name='ocr')
    async def OCRSPACE(self, ctx, *, args=None):
        """ocr.space engine V1. Results not what you expected? Try ocr2 command.

        args = [link] [language]
        or args = [language] if image as attachment
        or args = [link] if language is english
        args can also be empty if language is english (default) and image in attachment
        
        Use ocrlangs command to see supported languages.
        """
        if args:
            args = args.split(' ')
        else:
            args = []
        
        if '-v2' in args:
            engine = 2
            del args[-1]

            lang = 'eng'

            if not args and len(ctx.message.attachments) == 0:
                raise commands.MissingRequiredArgument(args)
            elif not args:
                link = ctx.message.attachments[0].url
            elif isURL(args[0]):
                link = args[0]
            else:
                raise commands.ArgumentParsingError()
        else:
            engine = 1

            if not args and len(ctx.message.attachments) == 0:
                raise commands.MissingRequiredArgument(args)
            elif not args:
                link = ctx.message.attachments[0].url
                lang = 'eng'
            elif isURL(args[0]) and len(args) == 1:
                link = args[0]
                lang = 'eng'
            elif len(args) == 1 and len(ctx.message.attachments) != 0:
                link = ctx.message.attachments[0].url
                lang = self.getLang(args[0])
            elif len(args) == 2 and isURL(args[0]):
                link = args[0]
                lang = self.getLang(args[1])
            elif len(args) == 2 and isURL(args[1]):
                lang = self.getLang(args[0])
                link = args[1]
            else:
                raise commands.ArgumentParsingError()

        data = await REST('https://api.ocr.space/parse/image', method='POST', headers={'apikey': getAPIKey('ocrspace')}, data={'url': link, 'language': lang, 'OCREngine': engine})

        if data['OCRExitCode'] != 1:
            await ctx.reply(f"`{data['ErrorMessage']}`")
        else:
            await ctx.reply(f"```{data['ParsedResults'][0]['ParsedText']} ```")

    @commands.command(name='ocr2')
    async def OCRSPACE2(self, ctx, *, args=None):
        f"""ocr.space engine V2. Results not what you expected? Try ocr command.
        V2 engine only supports latin characters, but is better at detecting numbers, special characters and rotated text.

        args = [link]
        args can also be empty if image in attachment
        """
        if args:
            args += ' -v2'
        else:
            args = '-v2'
        await ctx.invoke(self.OCRSPACE, args=args)


def setup(bot):
    bot.add_cog(OCR(bot))