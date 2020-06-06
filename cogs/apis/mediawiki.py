from discord.ext import commands
from BotUtils import REST, escapeURL
import discord

class Mediawiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mediawiki(self, ctx, query, apiURL, wikiName, introOnly=True):
        # Assuming the user knows what they are looking for by using srwhat=nearmatch
        search = await REST(f"{apiURL}?action=query&list=search&format=json&srwhat=nearmatch&utf8&srsearch={escapeURL(query)}")
        if not search['query']['search']:
            # No matches found, guess what the user meant
            search = await REST(f"{apiURL}?action=query&list=search&format=json&utf8&srsearch={escapeURL(query)}")
            # Check if user is just stupid and can't spell properly
            if not search['query']['search']:
                if 'suggestionsnippet' in search['query']['searchinfo']:
                    await ctx.send('No results found. Did you mean: {}?'.format(search['query']['searchinfo']['suggestionsnippet'].replace('<em>', '__').replace('</em>', '__')))
                else:
                    await ctx.send('No results found.')
                return

        pageID = str(search['query']['search'][0]['pageid'])
        info = await REST(f'{apiURL}?action=query&prop=info|pageimages|extracts&inprop=url|displaytitle&piprop=original&pilicense=any&exchars=500&format=json&explaintext&utf8&redirects&pageids={pageID}')
        # Get "first" page with an unknown pageID
        info = list(info['query']['pages'].values())[0]

        title = info['title']
        url = info['fullurl']
        description = info['extract']
        try:
            imgUrl = info['original']['source']
        except:
            imgUrl = None

        embed = discord.Embed(title=f"{title} - {wikiName}", color=0x32cd32, url=url)
        embed.description = description
        if imgUrl:
            embed.set_image(url=imgUrl)
        await ctx.send(embed=embed)

    # The wiki has to have the TextExtracts extension in order for the API to work.
    # TODO: Don't rely on TextExtracts by stripping html manually (?)

    @commands.command(name='wiki', aliases=['wikipedia'])
    async def wiki(self, ctx, *, query):
        await self.mediawiki(ctx, query, 'https://en.wikipedia.org/w/api.php', 'Wikipedia')

    @commands.command(name='wiktionary', aliases=['dictionary', 'define'])
    async def wiktionary(self, ctx, *, query):
        await self.mediawiki(ctx, query, 'https://en.wiktionary.org/w/api.php', 'Wiktionary')

    @commands.command(name='wikilanguage', aliases=['wikil', 'wikilang'])
    async def wikilanguage(self, ctx, lang, *, query):
        await self.mediawiki(ctx, query, 'https://'+lang+'.wikipedia.org/w/api.php', 'Wikipedia ' + lang.upper())

    @commands.command(name='wiktionarylanguage', aliases=['wiktionarylang', 'dictionarylanguage', 'dictionarylang', 'definelang', 'definelanguage'])
    async def wiktionarylanguage(self, ctx, lang, *, query):
        await self.mediawiki(ctx, query, 'https://'+lang+'.wiktionary.org/w/api.php', 'Wiktionary ' + lang.upper())

    @commands.command(name='gamepedia')
    async def gamepedia(self, ctx, wiki, *, query):
        await self.mediawiki(ctx, query, 'https://'+wiki+'.gamepedia.com/api.php', wiki.title() + ' Wiki')

    @commands.command(name='mcwiki', aliases=['minecraftwiki'])
    async def mcwiki(self, ctx, *, query):
        await self.mediawiki(ctx, query, 'https://minecraft.gamepedia.com/api.php', 'Minecraft Wiki')
        
    # TODO: Bulbapedia doesn't return pageIDs in searches

def setup(bot):
    bot.add_cog(Mediawiki(bot))