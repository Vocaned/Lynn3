from discord.ext import commands
from BotUtils import REST, getAPIKey, escapeURL
import discord

class IMDb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='imdb', aliases=['movie', 'movies'])
    async def IMDbAPI(self, ctx, *, title):
        """Gets information about movies using the IMDb"""
        data = await REST(f"http://www.omdbapi.com/?apikey={getAPIKey('omdb')}&t={escapeURL(title)}")

        embed = discord.Embed(title=f"{data['Title']} ({data['Year']})", colour=0xf5c518, url=f"https://www.imdb.com/title/{data['imdbID']}")
        embed.add_field(name='Released', value=data['Released'])
        if 'Production' in data:
            embed.add_field(name='Produced by', value=data['Production'])
        if data['Runtime'] != 'N/A':
            embed.add_field(name='Length', value=data['Runtime'])
        embed.add_field(name='Genre', value=data['Genre'])
        if 'totalSeasons' in data and data['totalSeasons'] != 'N/A':
            embed.add_field(name='Seasons', value=data['totalSeasons'])
        embed.add_field(name='Plot', value='||'+data['Plot']+'||')
        if 'Website' in data and data['Website'] != 'N/A':
            embed.add_field(name='Website', value=data['Website'])
        if 'Awards' in data and data['Awards'] != 'N/A':
            embed.add_field(name='Awards', value=data['Awards'].replace('. ', '.\n'))
        if data['Poster'] != 'N/A':
            embed.set_image(url=data['Poster'])

        if data['Ratings']:
            ratings = ''
            for i in data['Ratings']:
                ratings += f"**{i['Source']}** - `{i['Value']}`\n"
            embed.add_field(name='Ratings', value=ratings)
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(IMDb(bot))