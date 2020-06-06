from discord.ext import commands
from BotUtils import REST, escapeURL
from datetime import datetime
import discord

class UrbanDictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_nsfw()
    @commands.command(name='urbandictionary', aliases=['urban'])
    async def UrbanDictionaryAPI(self, ctx, *, term):
        """Gets information about the urban dictionary"""
        data = await REST(f"http://api.urbandictionary.com/v0/define?term={escapeURL(term)}")
        data = data['list'][0]
        embed = discord.Embed(title=data['word'], colour=0x1d2439, url=data['permalink'])
        embed.add_field(name='Definition', value='```'+data['definition'].replace('\r','')+'```')
        embed.add_field(name='Example', value='```'+data['example'].replace('\r','')+'```')
        embed.set_footer(text=str(data['thumbs_up'])+'\N{THUMBS UP SIGN}, ' + str(data['thumbs_down']) + '\N{THUMBS DOWN SIGN} | Submitted')
        embed.timestamp = datetime.strptime(data['written_on'].split('T')[0], '%Y-%m-%d')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UrbanDictionary(bot))