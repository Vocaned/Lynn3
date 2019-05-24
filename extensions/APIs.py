import discord
from discord.ext import commands
import requests
from datetime import datetime
import base64
import json
import math
import urllib.parse

class APIs(commands.Cog):
    """APIs"""

    def __init__(self, bot):
        self.bot = bot

    async def getAPI(self, url):
        r = requests.get(url=url)
        return(r.json())

    def url(self, url):
        return urllib.parse.quote(url)
    
    # ----
    # MINECRAFT
    # ----

    async def getMinecraftAgeCheck(self, name, num):
        r = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name + '?at=' + str(num))
        if r.status_code == 200:
            return True
        return False

    async def getMinecraftAge(self, name):
        a = 1263146630 # notch sign-up
        b = math.floor(datetime.utcnow().timestamp())
        lastfail = 0
        for i in range(30):
            if a == b:
                ok = await APIs.getMinecraftAgeCheck(self, name, a)
                if ok and lastfail == a-1:
                    return datetime.utcfromtimestamp(a).strftime('%c')
                else:
                    return  '???'
            else:
                mid = a + math.floor( ( b - a ) / 2)
                ok = await APIs.getMinecraftAgeCheck(self, name, mid)
                if ok:
                    #print('range: ' + str(a) + '\t<-| \t' + str(b))
                    b = mid
                else:
                    #print('range: ' + str(a) + '\t |->\t' + str(b))
                    a = mid+1
                    lastfail = mid

    async def getMinecraftSales(self):
        payload = '{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}'
        r = requests.post(url='https://api.mojang.com/orders/statistics', data=payload)
        return(r.json())
    
    async def getMinecraftUUID(self, name):
        r = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name)
        if r.status_code == 200:
            return(r.json())
        
        r2 = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name + "?at=0")
        if r2.status_code == 200:
            return(r2.json())
            
        return(None)
    
    async def getMinecraftSkinUrl(self, uuid):
        r = requests.get(url='https://sessionserver.mojang.com/session/minecraft/profile/' + uuid)
        data = r.json()
        val = data["properties"][0]["value"]
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    @commands.command(name='minecraft', aliases=['mc'])
    async def minecraftAPI(self, ctx, *, user=None):
        """Gets information about Minecraft, or searches players.
        Leave user as blank for general statistics"""
        try:
            if user:
                uuid = await APIs.getMinecraftUUID(self, user)
                if not uuid:
                    await ctx.send(content='User not found!')
                    await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
                    return
                await ctx.message.add_reaction('\N{HOURGLASS}')
                history = await APIs.getAPI(self, 'https://api.mojang.com/user/profiles/' + uuid["id"] + '/names')
                names = []
                for i in range(len(history)):
                    names.append(history[i]["name"])
                    names[i] = names[i].replace('*', '\*').replace('_', '\_').replace('~', '\~')
                names.reverse()
                names[0] += " **[CURRENT]**"

                created = await APIs.getMinecraftAge(self, user)

                skin = await APIs.getMinecraftSkinUrl(self, uuid["id"])
                embed = discord.Embed(title='Minecraft User', colour=0x82540f)
                embed.set_author(name=history[-1]["name"], 
                                icon_url='https://crafatar.com/avatars/' + uuid["id"])
                embed.set_image(url='https://crafatar.com/renders/body/' + uuid["id"] + '.png')
                embed.add_field(name='Name history', value='\n'.join(names))
                embed.add_field(name='UUID', value=uuid["id"])
                embed.add_field(name='Skin URL', value='[Click me]('+skin["textures"]["SKIN"]["url"]+')')
                embed.add_field(name='Account created', value=created)
                embed.set_footer(text='|', icon_url='https://minecraft.net/favicon-96x96.png')
                embed.timestamp = datetime.utcnow()
                await ctx.message.clear_reactions()
                await ctx.send(embed=embed, content="")
            else:
                sale = await APIs.getMinecraftSales(self)
                embed = discord.Embed(title='Minecraft', colour=0x82540f)
                embed.add_field(name='Sold total', value=sale["total"])
                embed.add_field(name='Sold in the last 24h', value=sale["last24h"])

                embed.set_footer(text='|', icon_url='https://minecraft.net/favicon-96x96.png')
                embed.timestamp = datetime.utcnow()
                await ctx.message.clear_reactions()
                await ctx.send(embed=embed, content="")
        except Exception:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction(content='\N{NO ENTRY SIGN}')

    # ----
    # Apex Legends
    # ----

    async def getApexAPI(self, url):
        r = requests.get(url=url, headers={"TRN-Api-Key":"4059b1bb-c040-4765-b945-0180e108fc36"})
        return(r.json())

    @commands.command(name='apex', aliases=['apexlegends', 'apesex'])
    async def apexAPI(self, ctx, user):
        """Gets information about Apex Legends players.
           Only PC information for now."""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        try:
            data = await APIs.getApexAPI(self, "https://public-api.tracker.gg/apex/v1/standard/profile/5/" + user)

            stats = []
            for stat in data["data"]["stats"]:
                val = str(stat["value"])
                stats.append(("Total " + stat["metadata"]["name"], val.rstrip('0').rstrip('.') if '.' in val else val))

            for legend in data["data"]["children"]:
                for stat in legend["stats"]:
                    val = str(stat["value"])
                    stats.append((legend["metadata"]["legend_name"] + " " + stat["metadata"]["name"], val.rstrip('0').rstrip('.') if '.' in val else val))

            embed = discord.Embed(title='Apex Legends', colour=0xff6666)
            embed.set_author(name=str(data["data"]["metadata"]["platformUserHandle"]) + " - Level " + str(data["data"]["metadata"]["level"]))
            for stat in stats:
                embed.add_field(name=stat[0], value=stat[1])

            embed.set_footer(text='Missing data because EA.', icon_url='https://cdn.discordapp.com/icons/541484311354933258/b8fc0f55e75911e45fb3348eb510fa6f.webp')
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed, content="")
        except Exception as e:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction(content='\N{NO ENTRY SIGN}')
            print(e)

    # ----
    # CSGO
    # ----

    users = {
        # Discord ID        :  Steam ID
        "177424155371634688": "76561198068918964",
        "257006753089060864": "76561198380462342",
        "350701370719862785": "76561198263243813",
        "287867554045624323": "76561198322549877",
        "303922742569336832": "76561198358351343",
        "415050364836904961": "76561198378745415",
        "380758020843634688": "76561198030030959",
        "413391798786850836": "76561198812709835",
        "344550203564621826": "76561198452824423"
    }

    @commands.command(name='csgo', aliases=['cs'])
    async def CSGOAPI(self, ctx, *, user=None):
        """Gets information about CSGO players."""
        if not user:
            if APIs.users[str(ctx.author.id)]:
                user = APIs.users[str(ctx.author.id)]
            else:
                await ctx.send("Please enter an steam id or custom url after the command.")
                return
        else:
            try:
                duser = await commands.UserConverter().convert(ctx, user)
                if APIs.users[str(duser.id)]:
                    user = APIs.users[str(duser.id)]
            except:
                pass
        await ctx.message.add_reaction('\N{HOURGLASS}')
        try:
            if not str(user).isdigit():
                data = await APIs.getAPI(self, "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=5F448887F3F06D8E18833E047BBCDB7E&vanityurl=" + APIs.url(self, user))
                user = data["response"]["steamid"]

            data = await APIs.getAPI(self, "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=5F448887F3F06D8E18833E047BBCDB7E&steamids=" + user)
            name = data["response"]["players"][0]["personaname"]

            data = await APIs.getAPI(self, "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=5F448887F3F06D8E18833E047BBCDB7E&steamid=" + user)
            data = data["playerstats"]

            embed = discord.Embed(title='Counter-Strike: Global Offensive', colour=0xadd8e6)
            embed.set_author(name=str(name))

            kills = deaths = timep = head = won = played = hit = shot = 0
            for i in data["stats"]:
                if i["name"] == "total_kills":
                    kills= i["value"]
                if i["name"] == "total_deaths":
                    deaths = i["value"]
                if i["name"] == "total_time_played":
                    timep = i["value"]
                if i["name"] == "total_kills_headshot":
                    head = i["value"]
                if i["name"] == "total_matches_won":
                    won = i["value"]
                if i["name"] == "total_matches_played":
                    played = i["value"]
                if i["name"] == "total_shots_hit":
                    hit = i["value"]
                if i["name"] == "total_shots_fired":
                    shot = i["value"]

            embed.add_field(name="Kills", value=str(kills))
            embed.add_field(name="K/D", value=str(round(kills/deaths, 2)))
            embed.add_field(name="Time Played", value=str(round(timep / 60 / 60, 1)) + "h")
            embed.add_field(name="Headshot %", value=str(round(head / kills * 100, 1)) + "%")
            embed.add_field(name="Win %", value=str(round(won / played * 100, 1)) + "%")
            embed.add_field(name="Accuracy", value=str(round(hit / shot * 100, 1)) + "%")

            embed.timestamp = datetime.utcnow()

            await ctx.message.clear_reactions()
            await ctx.send(embed=embed, content="")
        except Exception as e:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
            print(e)

    # ----
    # CLASSICUBE
    # ----
    
    @commands.command(name='classicube', aliases=['cc'])
    async def classiCubeAPI(self, ctx, *, user=None):
        """Gets information about ClassiCube, or searches players.
        user = ID or name
        Leave as blank for general statistics"""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        if user:
            data = await APIs.getAPI(self, 'https://www.classicube.net/api/player/'+user)
            if data["error"] != "":
                data = await APIs.getAPI(self, 'https://www.classicube.net/api/id/'+user)
                if data["error"] != "":
                    await ctx.message.clear_reactions()
                    await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
                    await ctx.send('User not found!')
                    return

            flags = []
            if 'b' in data["flags"]:
                flags.append('Banned from forums')
            if 'd' in data["flags"]:
                flags.append('Developer')
            if 'm' in data["flags"]:
                flags.append('Forum moderator')
            if 'a' in data["flags"]:
                flags.append('Forum admin')
            if 'e' in data["flags"]:
                flags.append('Blog editor')
            
            embed = discord.Embed(title='ClassiCube User', colour=0x977dab)
            embed.set_author(name=data["username"],
                icon_url='https://www.classicube.net/face/'+data["username"]+'.png')
            embed.add_field(name='ID', value=data["id"])
            embed.add_field(name='Registered on', value=datetime.utcfromtimestamp(data["registered"]).strftime('%c'))
            if flags:
                embed.add_field(name='Notes', value=', '.join(flags))
            
            embed.set_footer(text='|', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed, content='')
        else:
            data = await APIs.getAPI(self, 'https://www.classicube.net/api/players/')
            players = ''
            for p in data["lastfive"]:
                players += str(p) + '\n'
            embed = discord.Embed(title='ClassiCube', colour=0x977dab)
            embed.add_field(name='Total Players', value=data["playercount"])
            embed.add_field(name='Last five accounts', value=players)

            embed.set_footer(text='|', icon_url='https://www.classicube.net/static/img/cc-cube-small.png')
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed, content='')
    
    # ----
    # Wynncraft
    # ----
    
    @commands.command(name='wynncraft', aliases=['wc', 'wynn'])
    async def WynncraftAPI(self, ctx, *, user=None):
        """Gets information about Wynncraft, or searches players.
        Leave as blank for general statistics"""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        if user:
            data = await APIs.getAPI(self, 'https://api.wynncraft.com/v2/player/'+user+'/stats')
            data = data["data"][0]
            if "error" in data:
                await ctx.message.clear_reactions()
                await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
                await ctx.send(str(data["error"]))
                return

            rank = ""
            if data["rank"] != "Player":
                rank += "**" + data["rank"] + "**\n"

            if data["meta"]["veteran"]:
                rank += "Veteran\n"

            if data["meta"]["tag"]["value"]:
                rank += data["meta"]["tag"]["value"]

            if rank == "":
                rank = "Player"

            stats = []
            stats.append("**Items identified:** " + str(data["global"]["itemsIdentified"]))
            stats.append("**Mobs killed:** " + str(data["global"]["mobsKilled"]))
            stats.append("**PvP kills:** " + str(data["global"]["pvp"]["kills"]))
            stats.append("**PvP deaths:** " + str(data["global"]["pvp"]["deaths"]))
            stats.append("**Chests found:** " + str(data["global"]["chestsFound"]))
            stats.append("**Blocks walked:** " + str(data["global"]["blocksWalked"]))
            stats.append("**Logins:** " + str(data["global"]["logins"]))
            stats.append("**Deaths:** " + str(data["global"]["deaths"]))
            stats.append("**Combat Level:** " + str(data["global"]["totalLevel"]["combat"]))
            stats.append("**Total Level:** " + str(data["global"]["totalLevel"]["combined"]))
            stats.sort(key=lambda x:int(x.split(' ')[-1]))
            stats.reverse()

            classes = []
            for s in data["classes"]:
                classes.append("**" + ''.join([i for i in s["name"].title() if not i.isdigit()]) + ":** Level " + str(round(s["level"])))
            classes.sort(key=lambda x:float(x.split(' ')[-1]))
            classes.reverse()

            embed = discord.Embed(title='Wynncraft Player', colour=0x7bbf32)
            embed.set_author(name=data["username"],
                    icon_url='https://crafatar.com/avatars/'+data["uuid"])
            embed.add_field(name='Rank', value=rank)
            embed.add_field(name='Guild', value=str(data["guild"]["name"]))
            embed.add_field(name='Playtime', value=str(round(data["meta"]["playtime"]/12, 2))+"h")
            embed.add_field(name='First joined on', value=data["meta"]["firstJoin"].replace("T", ", ").split(".")[0])
            embed.add_field(name='Last joined on', value=data["meta"]["lastJoin"].replace("T", ", ").split(".")[0])
            if data["meta"]["location"]["online"]:
                embed.add_field(name='Currently in', value=data["meta"]["location"]["server"])
            
            embed.add_field(name='Global stats', value="\n".join(stats))
            embed.add_field(name='Classes', value="\n".join(classes))
            
            embed.set_footer(text='|', icon_url='https://cdn.wynncraft.com/img/ico/android-icon-192x192.png')
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed, content='')
            return                
        else:
            data = await APIs.getAPI(self, 'https://api.wynncraft.com/public_api.php?action=onlinePlayersSum')
            embed = discord.Embed(title='Wynncraft', colour=0x7bbf32)
            embed.add_field(name='Players Online', value=data["players_online"])

            embed.set_footer(text='|', icon_url='https://cdn.wynncraft.com/img/ico/android-icon-192x192.png')
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed, content='')

    @commands.command(name='imdb', aliases=["movie", "movies"])
    async def IMDbAPI(self, ctx, *, title):
        """Gets information about movies using the IMDb"""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        data = await APIs.getAPI(self, 'http://www.omdbapi.com/?apikey=df81343d&t=' + APIs.url(self, title))
        if data["Response"] == "False":
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
            await ctx.send(str(data["error"]))
            return

        embed = discord.Embed(title=data["Title"] + " (" + data["Year"] + ")", colour=0xf5c518, url="https://www.imdb.com/title/" + data["imdbID"])
        embed.add_field(name="Released", value=data["Released"])
        if "Production" in data:
            embed.add_field(name="Produced by", value=data["Production"])
        embed.add_field(name="Length", value=data["Runtime"])
        embed.add_field(name="Genres", value=data["Genre"])
        embed.add_field(name="Plot", value="||"+data["Plot"]+"||")
        if data["Poster"] != "N/A":
            embed.set_image(url=data["Poster"])

        if data["Ratings"]:
            ratings = ""
            for i in data["Ratings"]:
                ratings += "**" + i["Source"] + "** - `" + i["Value"] + "`\n"

            embed.add_field(name="Ratings", value=ratings)

        

        embed.timestamp = datetime.utcnow()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed, content='')

    @commands.command(name='urbandictionary', aliases=["urban", "define"])
    async def UrbanDictionaryAPI(self, ctx, *, term):
        """Gets information about movies using the IMDb"""
        await ctx.message.add_reaction('\N{HOURGLASS}')
        data = await APIs.getAPI(self, 'http://api.urbandictionary.com/v0/define?term=' + APIs.url(self, term))
        if not data["list"]:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
            return
        data = data["list"][0]
        embed = discord.Embed(title=data["word"], colour=0x1d2439, url=data["permalink"])
        embed.add_field(name="Definition", value="```"+data["definition"].replace("\r","")+"```")
        embed.add_field(name="Example", value="```"+data["example"].replace("\r","")+"```")
        
        embed.set_footer(text=str(data["thumbs_up"])+"👍, " + str(data["thumbs_down"]) + "👎 | Submitted")
        embed.timestamp = datetime.strptime(data["written_on"].split("T")[0], "%Y-%m-%d")
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed, content='')


def setup(bot):
    bot.add_cog(APIs(bot))
