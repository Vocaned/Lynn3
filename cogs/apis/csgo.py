from discord.ext import commands
import discord
from BotUtils import REST, escapeURL, getAPIKey
from datetime import datetime

class CSGO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def getCSStat(self, data, stat):
        return [i for i in data['stats'] if i['name'] == stat][0]['value']

    @commands.command(name='csgo', aliases=['cs'])
    async def CSGOAPI(self, ctx, *, user):
        """Gets information about CSGO players."""
        if not user.isdigit():
            data = await REST(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={getAPIKey('steam')}&vanityurl={escapeURL(user)}")
            user = data['response']['steamid']
        data = await REST(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={getAPIKey('steam')}&steamids={user}")
        name = data['response']['players'][0]['personaname']
        data = await REST(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={getAPIKey('steam')}&steamid={user}")
        data = data['playerstats']
        embed = discord.Embed(title='Counter-Strike: Global Offensive', colour=0xadd8e6)
        embed.set_author(name=str(name))
        embed.add_field(name='Kills', value=str(self.getCSStat(data, 'total_kills')))
        embed.add_field(name='K/D', value=str(round(self.getCSStat(data, 'total_kills')/self.getCSStat(data, 'total_deaths'), 2)))
        embed.add_field(name='Time Played', value=str(round(self.getCSStat(data, 'total_time_played') / 60 / 60, 1)) + 'h')
        embed.add_field(name='Headshot %', value=str(round(self.getCSStat(data, 'total_kills_headshot') / self.getCSStat(data, 'total_kills') * 100, 1)) + '%')
        embed.add_field(name='Win %', value=str(round(self.getCSStat(data, 'total_matches_won') / self.getCSStat(data, 'total_matches_played') * 100, 1)) + '%')
        embed.add_field(name='Accuracy', value=str(round(self.getCSStat(data, 'total_shots_hit') / self.getCSStat(data, 'total_shots_fired') * 100, 1)) + '%')
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CSGO(bot))