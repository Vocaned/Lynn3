from discord.ext import commands
import discord
from datetime import datetime
from BotUtils import REST, escapeURL, getAPIKey

class osu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='osu')
    async def OsuAPI(self, ctx, *, user):
        """Gets information about osu! players."""
        data = await REST(f"https://osu.ppy.sh/api/get_user?u={escapeURL(user)}&k={getAPIKey('osu')}")
        data = data[0]
        embed = discord.Embed(title=f"osu! - {data['username']}", color=0xEA68A3)
        embed.set_thumbnail(url=f"https://a.ppy.sh/{data['user_id']}")
        embed.add_field(name='Level', value=str(round(float(data['level']), 2)))
        embed.add_field(name='Ranked Score', value=data['ranked_score'])
        embed.add_field(name='Hit Accuracy', value=str(round(float(data['accuracy']), 2)) + '%')
        embed.add_field(name='Play Count', value=data['playcount'])
        embed.add_field(name='Total Score', value=data['total_score'])
        embed.add_field(name='PP', value=str(round(float(data['pp_raw']), 2)))
        embed.add_field(name='Playtime', value=str(round(int(data['total_seconds_played'])/60/60, 2)) + 'h')
        embed.add_field(name='Ranks', value='Silver SS: ' + data['count_rank_ssh']
                                           + '\nGold SS: ' + data['count_rank_ss']
                                           + '\nSilver S: ' + data['count_rank_sh']
                                           + '\nGold S: ' + data['count_rank_s']
                                           + '\nA: ' + data['count_rank_a'])
        embed.add_field(name='Leaderboards', value='**#' + data['pp_rank'] + '** global'
                                                  + '\n**#' + data['pp_country_rank'] + '** in ' + data['country'])
        embed.set_footer(text='Account created', icon_url='https://osu.ppy.sh/favicon-32x32.png')
        embed.timestamp = datetime.strptime(data['join_date'], '%Y-%m-%d %H:%M:%S')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(osu(bot))