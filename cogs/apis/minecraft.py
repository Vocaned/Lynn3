from discord.ext import commands
import discord
from BotUtils import REST, headRenderer, skinRenderer2D, escapeURL
import math
from datetime import datetime
import json
import base64

class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Ported to python from
    # https://gist.github.com/jomo/be7dbb5228187edbb993
    async def getMinecraftAge(self, name):
        a = 1263146630 # notch sign-up
        b = math.floor(datetime.utcnow().timestamp())
        last = 0
        for _ in range(30):
            if a == b:
                if last == a-1 and await REST(f"https://api.mojang.com/users/profiles/minecraft/{name}?at={str(a)}", returns='status') == 200:
                    return datetime.utcfromtimestamp(a)
                else:
                    return False
            else:
                mid = a + math.floor((b - a) / 2)
                if await REST(f"https://api.mojang.com/users/profiles/minecraft/{name}?at={str(mid)}", returns='status')  == 200:
                    b = mid
                else:
                    a = mid+1
                    last = mid

    # thanks stackoverflow love ya
    # https://stackoverflow.com/a/13756038
    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ('year',        60*60*24*365),
            ('month',       60*60*24*30),
            ('day',         60*60*24),
            ('hour',        60*60),
            ('minute',      60)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = 's' if period_value > 1 else ''
                strings.append('%s %s%s' % (period_value, period_name, has_s))

        return ', '.join(strings)

    async def getMinecraftUUID(self, name):
        r = await REST(f"https://api.mojang.com/users/profiles/minecraft/{name}")
        if r:
            return r

        r = await REST(f"https://api.mojang.com/users/profiles/minecraft/{name}?at=0")
        if r:
            return r
        return None

    async def getMinecraftSkinUrl(self, uuid):
        data = await REST(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        try:
            val = data['properties'][0]['value']
        except:
            return None
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    @commands.command(name='minecraft', aliases=['mc'])
    @commands.cooldown(rate=1, per=10)
    async def minecraftAPI(self, ctx, *, user=None):
        """Gets information about Minecraft, or searches players.
        Leave user as blank for general statistics"""
        if user:
            uuid = await self.getMinecraftUUID(user)
            if not uuid:
                raise commands.BadArgument(message='User not found')
            history = await REST(f"https://api.mojang.com/user/profiles/{uuid['id']}/names")
            names = []
            for i in range(len(history)):
                names.append(history[i]['name'])
                # Escape special markdown characters
                names[i] = names[i].replace('*', '\\*').replace('_', '\\_').replace('~', '\\~')
            names.reverse()
            names[0] += ' **[CURRENT]**'
            created = await self.getMinecraftAge(user)
            skin = await self.getMinecraftSkinUrl(uuid['id'])
            if not skin:
                raise commands.CommandOnCooldown(commands.BucketType.default, 10)
            embed = discord.Embed(title='Minecraft User', colour=0x82540f)
            embed.set_author(name=history[-1]['name'], icon_url='attachment://head.png')
            embed.add_field(name='Name history', value='\n'.join(names))
            embed.add_field(name='UUID', value=uuid['id'])
            try:
                embed.add_field(name='Skin URL', value='[Click me]('+skin['textures']['SKIN']['url']+')')
                await skinRenderer2D(skin['textures']['SKIN']['url'])
                await headRenderer(skin['textures']['SKIN']['url'])
                skinFile = discord.File(f"skins/2d/{skin['textures']['SKIN']['url'].split('/')[-1]}.png", filename='skin.png')
                headFile = discord.File(f"skins/head/{skin['textures']['SKIN']['url'].split('/')[-1]}.png", filename='head.png')
            except:
                # TODO: Try to find a official steve skin in mojang's skin server
                await skinRenderer2D('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
                await headRenderer('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
                skinFile = discord.File('skins/2d/Steve_skin.png', filename='skin.png')
                headFile = discord.File('skins/head/Steve_skin.png', filename='head.png')

            if created:
                embed.add_field(name='Account created', value=f"On {created.strftime('%c')}\n{self.td_format(datetime.utcnow() - created)} ago")
            else:
                embed.add_field(name='Account created', value='???')
            embed.set_footer(text='\U00002063', icon_url='https://minecraft.net/favicon-96x96.png')
            embed.set_image(url='attachment://skin.png')
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[skinFile, headFile], embed=embed)
        else:
            sale = await REST('https://api.mojang.com/orders/statistics', method='POST', data='{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}', headers={"content-type": "application/json"})
            embed = discord.Embed(title='Minecraft', colour=0xa4d168)
            embed.add_field(name='Sold total', value=sale['total'])
            embed.add_field(name='Sold in the last 24h', value=sale['last24h'])
            embed.add_field(name='Sold per second', value=sale['saleVelocityPerSeconds'])
            embed.set_footer(text='\U00002063', icon_url='https://minecraft.net/favicon-96x96.png')
            embed.timestamp = datetime.utcnow()
            
            sale = await REST('https://api.mojang.com/orders/statistics', method='POST', data='{"metricKeys":["item_sold_dungeons"]}', headers={"content-type": "application/json"})
            embed2 = discord.Embed(title='Minecraft Dungeons', colour=0xe57834)
            embed2.add_field(name='Sold total', value=sale['total'])
            embed2.add_field(name='Sold in the last 24h', value=sale['last24h'])
            embed2.add_field(name='Sold per second', value=sale['saleVelocityPerSeconds'])
            # TODO: Minecraft dungeons favicon
            embed2.set_footer(text='\U00002063', icon_url='https://minecraft.net/favicon-96x96.png')
            embed2.timestamp = datetime.utcnow()

            await ctx.send(embed=embed)
            await ctx.send(embed=embed2)

    @commands.command(name='classicube', aliases=['cc'])
    async def classiCubeAPI(self, ctx, *, user=None):
        """Gets information about ClassiCube, or searches players.
        user = ID or name
        Leave blank for general statistics"""
        if user:
            data = await REST(f"https://www.classicube.net/api/player/{escapeURL(user)}")
            if not data or data['error'] != '':
                if user.isdigit():
                    data = await REST(f"https://www.classicube.net/api/id/{escapeURL(user)}")
                if not data or data['error'] != '':
                    raise commands.BadArgument(message='User not found')

            flagName = {
                'b': 'Banned from forums',
                'd': 'Developer',
                'm': 'Forum moderator',
                'a': 'Forum admin',
                'e': 'Blog editor',
                'p': 'Patron',
                'u': 'Unverified',
                'r': 'Recovering account'
            }
            flags = data['flags']

            embed = discord.Embed(title='ClassiCube User', colour=0x977dab)
            embed.set_author(name=data['username'],
                icon_url='attachment://head.png')
            embed.add_field(name='ID', value=data['id'])
            ago = self.td_format(datetime.utcnow() - datetime.utcfromtimestamp(data['registered']))
            if len(ago) == 0:
                ago = 'Under a minute'
            embed.add_field(name='Account created', value=f"On {datetime.utcfromtimestamp(data['registered']).strftime('%c')}\n{ago} ago")
            if flags:
                embed.add_field(name='Notes', value=', '.join([flagName[n] for n in flags]))
            if data['forum_title']:
                embed.add_field(name='Forum Title', value=discord.utils.escape_mentions(data['forum_title']))
            
            skinURL = f'https://classicube.s3.amazonaws.com/skin/{str(data["username"])}.png'
            if await REST(skinURL, returns='status') == 200:
                embed.add_field(name='Skin URL', value=f"[Click me]({skinURL})")
                await skinRenderer2D(skinURL, fromFile=False)
                await headRenderer(skinURL, fromFile=False)
                file = discord.File(f"skins/2d/{data['username']}.png", filename='skin.png')
                file2 = discord.File(f"skins/head/{data['username']}.png", filename='head.png')
            else:
                await skinRenderer2D('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
                await headRenderer('https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png')
                file = discord.File('skins/2d/Steve_skin.png', filename='skin.png')
                file2 = discord.File('skins/head/Steve_skin.png', filename='head.png')

            embed.set_footer(text='\U00002063', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
            embed.set_image(url='attachment://skin.png')
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[file, file2], embed=embed)
        else:
            data = await REST('https://www.classicube.net/api/players/')
            playercount = data['playercount']
            players = ''
            for p in data['lastfive']:
                players += str(p) + '\n'

            data = await REST('https://www.classicube.net/api/servers/')
            serverlist = []
            servers = ''
            for server in sorted(data['servers'], key=lambda k: k['players'], reverse=True):
                if server['players'] > 0:
                    temp = f"[{server['country_abbr']}] [{server['name']}](https://www.classicube.net/server/play/{server['hash']}) | {server['players']}/{server['maxplayers']}"
                    if len(servers) + len('\n---\n') + len(temp) > 1024:
                        serverlist.append(servers)
                        servers = ''
                    servers += temp+'\n---\n'
            serverlist.append(servers)

            embed = discord.Embed(title='ClassiCube', colour=0x977dab)
            embed.add_field(name='Total Accounts', value=playercount)
            embed.add_field(name='Last five accounts', value=players)
            for i in range(len(serverlist)):
                embed.add_field(name=(f"({str(i+1)}/{str(len(serverlist))})" if len(serverlist) != 1 else '') + 'Servers with players\nClick the server names to join!', value=serverlist[i])

            embed.set_footer(text='\U00002063', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Minecraft(bot))