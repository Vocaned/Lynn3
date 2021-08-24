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
        userfields = [
            'created_at', 'description', 'location',
            'name', 'profile_image_url', 'protected',
            'public_metrics', 'url', 'username',
            'verified', 'withheld'
        ]
        data = await twitter.request('GET', f'../2/users/by/username/{escapeURL(user)}', params={'expansions': 'author_id', 'user.fields': ",".join(userfields)})
        data = data[0]
        embed = discord.Embed(title=f"{data['name']} (@{data['username']})", url=data['url'], description=data['description'], color=0x1DA1F2)
        embed.set_thumbnail(url=data['profile_image_url'])
        embed.add_field(name='Tweets', value=str(data['public_metrics.tweet_count']))
        embed.add_field(name='Followers', value=str(data['public_metrics.followers_count']))
        embed.add_field(name='Following', value=str(data['public_metrics.following_count']))
        if data['location']:
            embed.add_field(name='Location', value=data['location'])
        if data['withheld'] and data['withheld.scope'] == 'user':
            embed.add_field(name='Banned in countries:', value=data['withheld.country_codes'])

        extra = []
        if data['verified']:
            extra.append('Verified')
        if data['protected']:
            extra.append('Private')

        if extra:
            embed.add_field(name='+', value='\n'.join(extra))
        embed.set_footer(icon_url='https://about.twitter.com/etc/designs/about-twitter/public/img/favicon-32x32.png', text='Twitter • Account created')
        embed.timestamp = datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S %z %Y')
        await ctx.message.reply(embed=embed)

def setup(bot):
    bot.add_cog(Twitter(bot))