from discord.ext import commands
from aioauth_client import TwitterClient
from BotUtils import getAPIKey, escapeURL
from datetime import datetime
import discord

class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='twitter')
    async def TwitterAPI(self, ctx, *, user):
        """Gets information about twitter users."""
        twitter = TwitterClient(consumer_key=getAPIKey('twitterConsKey'),
                                consumer_secret=getAPIKey('twitterConsSecret'),
                                oauth_token=getAPIKey('twitterAccToken'),
                                oauth_token_secret=getAPIKey('twitterAccSecret'))
        data = await twitter.request('GET', 'users/search.json', params={'count': 1, 'q': escapeURL(user)})
        data = data[0]
        embed = discord.Embed(title=f"{data['name']} (@{data['screen_name']})", url=f"https://twitter.com/{data['screen_name']}", description=data['description'], color=0x1DA1F2)
        embed.set_thumbnail(url=data['profile_image_url_https'])
        embed.add_field(name='Tweets', value=str(data['statuses_count']))
        embed.add_field(name='Followers', value=str(data['followers_count']))
        embed.add_field(name='Following', value=str(data['friends_count']))
        embed.add_field(name='Liked posts', value=str(data['favourites_count']))
        if data['location']:
            embed.add_field(name='Location', value=data['location'])
        extra = []
        if data['verified']:
            extra.append('Verified')
        if data['protected']:
            extra.append('Private')
        if extra:
            embed.add_field(name='+', value='\n'.join(extra))
        embed.set_footer(icon_url='https://about.twitter.com/etc/designs/about-twitter/public/img/favicon-32x32.png', text='Twitter • Account created')
        embed.timestamp = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Twitter(bot))