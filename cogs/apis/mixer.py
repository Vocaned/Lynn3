from discord.ext import commands
from BotUtils import REST, escapeURL
from datetime import datetime
import discord

class Mixer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='mixer')
    async def MixerAPI(self, ctx, *, user):
        """Gets information about mixer users"""
        data = await REST(f"https://mixer.com/api/v1/channels/{escapeURL(user)}")

        name = data['token']
        if data['user']['username'].lower() != data['token'].lower():
            name = f"{data['token']} ({data['user']['username']})"

        s = ' (Currently Streaming)' if data['online'] else ''
        embed = discord.Embed(title=f"Mixer user - {name}{s}", color=0x002050, url=f'https://mixer.com/{data["token"]}')

        if data['user']['avatarUrl']:
            embed.set_thumbnail(url=data['user']['avatarUrl'])

        typeNames = {
            'Verified': data['user']['verified'],
            'Suspended': data['suspended'],
            'Featured': data['featured'],
            'Partnered': data['partnered'],
            'Interactive Stream': data['interactive'],
            'VODs': data['vodsEnabled']
        }
        types = [c for c in typeNames if typeNames[c]]
        groups = []

        try:
            for group in data['user']['groups']:
                groups.append(group['name'])
        except:
            pass

        if types:
            embed.add_field(name='Account type', value='\n'.join(types))
        if groups:
            embed.add_field(name='Account groups', value='\n'.join(groups))

        if data['user']['bio']:
            embed.add_field(name='Bio', value=str(data['user']['bio']))

        embed.add_field(name='Followers', value=str(data['numFollowers']))
        embed.add_field(name='Sparks', value=str(data['user']['sparks']))

        try:
            if data['thumbnail']['url']:
                embed.set_image(url=data['thumbnail']['url'])
        except:
            pass

        if data['online']:
            embed.add_field(name='Current viewers', value=str(data['viewersCurrent']))

        embed.set_footer(icon_url='https://mixer.com/_latest/assets/favicons/favicon-32x32.png', text=f"LVL {data['user']['level']} • Account created ")
        embed.timestamp = datetime.strptime(data['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Mixer(bot))