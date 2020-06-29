from discord.ext import commands
from BotUtils import REST, escapeURL
import discord
import re

class Mediawiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mediawiki(self, ctx, query, apiURL, wikiName, introOnly=True, safe=False):
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

        pageID = search['query']['search'][0]['pageid']
        info = await REST(f'{apiURL}?action=query&prop=info|pageimages|extracts&inprop=url|displaytitle&piprop=original&pilicense=any&exlimit=1&format=json&explaintext&utf8&redirects&pageids={pageID}')
        # Get "first" page with an unknown pageID
        info = list(info['query']['pages'].values())[0]

        title = info['title']
        url = info['fullurl']
        try:
            imgUrl = info['original']['source']
        except:
            imgUrl = None

        totalchars = 0
        title = f"{title} - {wikiName}"
        totalchars += len(title)
        embed = discord.Embed(title=title, color=0x32cd32, url=url)
        if imgUrl and (safe or (not ctx.guild or ctx.channel.is_nsfw())):
            embed.set_image(url=imgUrl)

        extract = info['extract'].replace('\\t', '')
        r = re.compile('([^=])(==\\s)(.+?)(\\s==)')
        m = [m for m in r.finditer(extract)]

        embed.description = extract[:min(m[0].start(), 2048)]
        totalchars += len(embed.description)

        for i in range(len(m)):
            next = None if i+1 == len(m) else m[i+1].start()
            val = extract[m[i].end():next]
            if val.strip() and len(val)+len(m[i].group(3))+totalchars < 6000:
                embed.add_field(name=m[i].group(3), value=val.strip()[:1024], inline=False)
                totalchars += len(val)+len(m[i].group(3))
        
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
        await self.mediawiki(ctx, query, f"https://{lang}.wikipedia.org/w/api.php", 'Wikipedia ' + lang.upper())

    @commands.command(name='wiktionarylanguage', aliases=['wiktionarylang', 'dictionarylanguage', 'dictionarylang', 'definelang', 'definelanguage'])
    async def wiktionarylanguage(self, ctx, lang, *, query):
        await self.mediawiki(ctx, query, f"https://{lang}.wiktionary.org/w/api.php", 'Wiktionary ' + lang.upper())

    @commands.command(name='wikibooks', aliases=['wikibook', 'book', 'books'])
    async def wikibooks(self, ctx, *, query):
        await self.mediawiki(ctx, query, 'https://en.wikibooks.org/w/api.php', 'Wikibooks')

    @commands.command(name='wikibookslanguage', aliases=['wikibookslang', 'wikibooklanguage', 'wikibooklang', 'bookslanguage', 'booklang', 'booklanguage', 'booklang'])
    async def wikibookslanguage(self, ctx, lang, *, query):
        await self.mediawiki(ctx, query, f"https://{lang}.wikibooks.org/w/api.php", 'Wikibooks ' + lang.upper())

    @commands.command(name='gamepedia')
    async def gamepedia(self, ctx, wiki, *, query):
        await self.mediawiki(ctx, query, f"https://{wiki}.gamepedia.com/api.php", wiki.title() + ' Wiki', safe=True)

    @commands.command(name='mcwiki', aliases=['minecraftwiki'])
    async def mcwiki(self, ctx, *, query):
        await self.mediawiki(ctx, query, 'https://minecraft.gamepedia.com/api.php', 'Minecraft Wiki', safe=True)
        
    # TODO: Bulbapedia doesn't return pageIDs in searches

def setup(bot):
    bot.add_cog(Mediawiki(bot))