import discord
from discord.ext import commands
import config
from datetime import datetime
import base64
import json
import math
import urllib
from BotUtils import REST, headRenderer, skinRenderer2D
from aioauth_client import TwitterClient
import aiohttp

class APIs(commands.Cog):
    '''APIs'''

    def __init__(self, bot):
        self.bot = bot

    # ---
    # FUNCTIONS
    # ---

    def escape(self, url):
        return urllib.parse.quote(url)

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
                strings.append("%s %s%s" % (period_value, period_name, has_s))

        return ', '.join(strings)

    # Ported to python from
    # https://gist.github.com/jomo/be7dbb5228187edbb993
    async def getMinecraftAge(self, name):
        a = 1263146630 # notch sign-up
        b = math.floor(datetime.utcnow().timestamp())
        last = 0
        for _ in range(30):
            if a == b:
                if last == a-1 and await REST(f'https://api.mojang.com/users/profiles/minecraft/{name}?at={str(a)}', returns='r.status == 200'):
                    return datetime.utcfromtimestamp(a)
                else:
                    return False
            else:
                mid = a + math.floor((b - a) / 2)
                if await REST(f'https://api.mojang.com/users/profiles/minecraft/{name}?at={str(mid)}', returns='r.status == 200'):
                    b = mid
                else:
                    a = mid+1
                    last = mid

    async def getMinecraftUUID(self, name):
        r = await REST(f'https://api.mojang.com/users/profiles/minecraft/{name}')
        if r:
            return r

        r = await REST(f'https://api.mojang.com/users/profiles/minecraft/{name}?at=0')
        if r:
            return r
        return None

    async def getMinecraftSkinUrl(self, uuid):
        data = await REST(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}')
        try:
            val = data['properties'][0]['value']
        except:
            return None
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    def getCSStat(self, data, stat):
        return [i for i in data['stats'] if i['name'] == stat][0]['value']

    async def mediawiki(self, ctx, query, apiURL, wikiName, introOnly=True):
        # Assuming the user knows what they are looking for by using srwhat=nearmatch
        search = await REST(f'{apiURL}?action=query&list=search&format=json&srwhat=nearmatch&utf8&srsearch={self.escape(query)}')
        if not search['query']['search']:
            # No matches found, guess what the user meant
            search = await REST(f'{apiURL}?action=query&list=search&format=json&utf8&srsearch={self.escape(query)}')
            # Check if user is just stupid and can't spell properly
            if not search['query']['search']:
                if 'suggestionsnippet' in search['query']['searchinfo']:
                    await ctx.send('No results found. Did you mean: {}?'.format(search['query']['searchinfo']['suggestionsnippet'].replace('<em>', '__').replace('</em>', '__')))
                else:
                    await ctx.send('No results found.')
                return

        pageID = str(search['query']['search'][0]['pageid'])
        info = await REST(f'{apiURL}?action=query&prop=info|pageimages|extracts&inprop=url|displaytitle&piprop=original&pilicense=any&exchars=500&format=json&explaintext&utf8&redirects&pageids={pageID}')
        # Get "first" page with an unknown pageID
        info = list(info['query']['pages'].values())[0]

        title = info['title']
        url = info['fullurl']
        description = info['extract']
        try:
            imgUrl = info['original']['source']
        except:
            imgUrl = None

        embed = discord.Embed(title=f'{title} - {wikiName}', color=0x32cd32, url=url)
        embed.description = description
        #if imgUrl and ctx.channel.is_nsfw():
            #embed.set_image(url=imgUrl)
        await ctx.send(embed=embed)

    # ---
    # GAMES
    # ---

    @commands.command(name="minecraft", aliases=["mc"])
    @commands.cooldown(rate=1, per=10)
    async def minecraftAPI(self, ctx, *, user=None):
        """Gets information about Minecraft, or searches players.
        Leave user as blank for general statistics"""
        if user:
            uuid = await self.getMinecraftUUID(user)
            if not uuid:
                raise commands.CommandError(message="%User not found!")
            history = await REST("https://api.mojang.com/user/profiles/" + uuid["id"] + "/names")
            names = []
            for i in range(len(history)):
                names.append(history[i]["name"])
                # Escape special markdown characters
                names[i] = names[i].replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
            names.reverse()
            names[0] += " **[CURRENT]**"
            created = await self.getMinecraftAge(user)
            skin = await self.getMinecraftSkinUrl(uuid["id"])
            if not skin:
                raise commands.CommandOnCooldown(commands.BucketType.default, 10)
            embed = discord.Embed(title="Minecraft User", colour=0x82540f)
            embed.set_author(name=history[-1]["name"], icon_url="attachment://head.png")
            embed.add_field(name="Name history", value="\n".join(names))
            embed.add_field(name="UUID", value=uuid["id"])
            try:
                embed.add_field(name="Skin URL", value="[Click me]("+skin["textures"]["SKIN"]["url"]+")")
                await skinRenderer2D(skin["textures"]["SKIN"]["url"])
                await headRenderer(skin["textures"]["SKIN"]["url"])
                skinFile = discord.File("skins/2d/" + skin["textures"]["SKIN"]["url"].split("/")[-1] + ".png", filename="skin.png")
                headFile = discord.File("skins/head/" + skin["textures"]["SKIN"]["url"].split("/")[-1] + ".png", filename="head.png")
            except:
                # TODO: Try to find a official steve skin in mojang's skin server
                await skinRenderer2D("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                await headRenderer("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                skinFile = discord.File("skins/2d/Steve_skin.png", filename="skin.png")
                headFile = discord.File("skins/head/Steve_skin.png", filename="head.png")

            if created:
                embed.add_field(name="Account created", value="On " + created.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - created) + " ago")
            else:
                embed.add_field(name="Account created", value="???")
            embed.set_footer(text="\U00002063", icon_url="https://minecraft.net/favicon-96x96.png")
            embed.set_image(url="attachment://skin.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[skinFile, headFile], embed=embed)
        else:
            sale = await REST("https://api.mojang.com/orders/statistics", method="s.post", data='{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}', headers='{"content-type": "application/json"}')
            embed = discord.Embed(title="Minecraft", colour=0x82540f)
            embed.add_field(name="Sold total", value=sale["total"])
            embed.add_field(name="Sold in the last 24h", value=sale["last24h"])
            embed.set_footer(text="\U00002063", icon_url="https://minecraft.net/favicon-96x96.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

    @commands.command(name="csgo", aliases=["cs"])
    async def CSGOAPI(self, ctx, *, user):
        """Gets information about CSGO players."""
        if not user.isdigit():
            data = await REST("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + config.apiKeys["steam"] + "&vanityurl=" + self.escape(user))
            user = data["response"]["steamid"]
        data = await REST("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + config.apiKeys["steam"] + "&steamids=" + user)
        name = data["response"]["players"][0]["personaname"]
        data = await REST("http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=" + config.apiKeys["steam"] + "&steamid=" + user)
        data = data["playerstats"]
        embed = discord.Embed(title="Counter-Strike: Global Offensive", colour=0xadd8e6)
        embed.set_author(name=str(name))
        embed.add_field(name="Kills", value=str(self.getCSStat(data, "total_kills")))
        embed.add_field(name="K/D", value=str(round(self.getCSStat(data, "total_kills")/self.getCSStat(data, "total_deaths"), 2)))
        embed.add_field(name="Time Played", value=str(round(self.getCSStat(data, "total_time_played") / 60 / 60, 1)) + "h")
        embed.add_field(name="Headshot %", value=str(round(self.getCSStat(data, "total_kills_headshot") / self.getCSStat(data, "total_kills") * 100, 1)) + "%")
        embed.add_field(name="Win %", value=str(round(self.getCSStat(data, "total_matches_won") / self.getCSStat(data, "total_matches_played") * 100, 1)) + "%")
        embed.add_field(name="Accuracy", value=str(round(self.getCSStat(data, "total_shots_hit") / self.getCSStat(data, "total_shots_fired") * 100, 1)) + "%")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


    @commands.command(name="osu")
    async def OsuAPI(self, ctx, *, user):
        """Gets information about osu! players."""
        data = await REST("https://osu.ppy.sh/api/get_user?u=" + self.escape(user) + "&k=" + config.apiKeys["osu"])
        data = data[0]
        embed = discord.Embed(title="osu! - " + data["username"], color=0xEA68A3)
        embed.set_thumbnail(url="https://a.ppy.sh/" + data["user_id"])
        embed.add_field(name="Level", value=str(round(float(data["level"]), 2)))
        embed.add_field(name="Ranked Score", value=data["ranked_score"])
        embed.add_field(name="Hit Accuracy", value=str(round(float(data["accuracy"]), 2)) + "%")
        embed.add_field(name="Play Count", value=data["playcount"])
        embed.add_field(name="Total Score", value=data["total_score"])
        embed.add_field(name="PP", value=str(round(float(data["pp_raw"]), 2)))
        embed.add_field(name="Playtime", value=str(round(int(data["total_seconds_played"])/60/60, 2)) + "h")
        embed.add_field(name="Ranks", value="Silver SS: " + data["count_rank_ssh"]
                                           + "\nGold SS: " + data["count_rank_ss"]
                                           + "\nSilver S: " + data["count_rank_sh"]
                                           + "\nGold S: " + data["count_rank_s"]
                                           + "\nA: " + data["count_rank_a"])
        embed.add_field(name="Leaderboards", value="**#" + data["pp_rank"] + "** global"
                                                  + "\n**#" + data["pp_country_rank"] + "** in " + data["country"])
        embed.set_footer(text="Account created", icon_url="https://osu.ppy.sh/favicon-32x32.png")
        embed.timestamp = datetime.strptime(data["join_date"], "%Y-%m-%d %H:%M:%S")
        await ctx.send(embed=embed)


    @commands.command(name="classicube", aliases=["cc"])
    async def classiCubeAPI(self, ctx, *, user=None):
        """Gets information about ClassiCube, or searches players.
        user = ID or name
        Leave blank for general statistics"""
        if user:
            data = await REST("https://www.classicube.net/api/player/"+self.escape(user))
            if not data or data["error"] != "":
                if user.isdigit():
                    data = await REST("https://www.classicube.net/api/id/"+self.escape(user))
                if not data or data["error"] != "":
                    raise commands.CommandError(message="%User not found!")

            flagName = {
                "b": "Banned from forums",
                "d": "Developer",
                "m": "Forum moderator",
                "a": "Forum admin",
                "e": "Blog editor",
                "p": "Patron",
                "u": "Unverified",
                "r": "Recovering account"
            }
            flags = data["flags"]

            embed = discord.Embed(title="ClassiCube User", colour=0x977dab)
            embed.set_author(name=data["username"],
                icon_url="attachment://head.png")
            embed.add_field(name="ID", value=data["id"])
            ago = self.td_format(datetime.utcnow() - datetime.utcfromtimestamp(data["registered"]))
            if len(ago) == 0:
                ago = "Under a minute"
            embed.add_field(name="Account created", value="On " + datetime.utcfromtimestamp(data["registered"]).strftime("%c") + "\n" + ago + " ago")
            if flags:
                embed.add_field(name="Notes", value=", ".join([flagName[n] for n in flags]))
            if data["forum_title"]:
                embed.add_field(name="Forum Title", value=discord.utils.escape_mentions(data["forum_title"]))
            if await REST("https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png", returns="r.status == 200"):
                embed.add_field(name="Skin URL", value="[Click me](https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png)")
                await skinRenderer2D("https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png", fromFile=False)
                await headRenderer("https://classicube.s3.amazonaws.com/skin/" + str(data["username"]) + ".png", fromFile=False)
                file = discord.File("skins/2d/" + str(data["username"]) + ".png", filename="skin.png")
                file2 = discord.File("skins/head/" + str(data["username"]) + ".png", filename="head.png")
            else:
                await skinRenderer2D("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                await headRenderer("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                file = discord.File("skins/2d/Steve_skin.png", filename="skin.png")
                file2 = discord.File("skins/head/Steve_skin.png", filename="head.png")

            embed.set_footer(text="\U00002063", icon_url="https://www.classicube.net/static/img/cc-cube-small.png")
            embed.set_image(url="attachment://skin.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[file, file2], embed=embed)
        else:
            data = await REST("https://www.classicube.net/api/players/")
            playercount = data["playercount"]
            players = ""
            for p in data["lastfive"]:
                players += str(p) + "\n"

            data = await REST("https://www.classicube.net/api/servers/")
            serverlist = []
            servers = ""
            for server in sorted(data["servers"], key=lambda k: k["players"], reverse=True):
                if server["players"] > 0:
                    temp = "[" + str(server["country_abbr"]) + "] [" + str(server["name"]) + "](https://www.classicube.net/server/play/" + str(server["hash"]) + ") | " + str(server["players"]) + "/" + str(server["maxplayers"])
                    if len(servers) + len("\n---\n") + len(temp) > 1024:
                        serverlist.append(servers)
                        servers = ""
                    servers += temp+"\n---\n"
            serverlist.append(servers)

            embed = discord.Embed(title="ClassiCube", colour=0x977dab)
            embed.add_field(name="Total Accounts", value=playercount)
            embed.add_field(name="Last five accounts", value=players)
            for i in range(len(serverlist)):
                embed.add_field(name=("("+str(i+1)+"/" + str(len(serverlist))+")" if len(serverlist) != 1 else "") + "Servers with players\nClick the server names to join!", value=serverlist[i])

            embed.set_footer(text="\U00002063", icon_url="https://www.classicube.net/static/img/cc-cube-small.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)


    @commands.command(name="wynncraft", aliases=["wc", "wynn"])
    async def WynncraftAPI(self, ctx, *, user=None):
        """Gets information about Wynncraft, or searches players.
        Leave blank for general statistics"""
        if user:
            data = await REST("https://api.wynncraft.com/v2/player/"+self.escape(user)+"/stats")
            data = data["data"][0]
            if "error" in data:
                raise commands.CommandError(message="%"+str(data["error"]))

            rankDict = {
                "**" + data["rank"] + "**": data["rank"] != "Player",
                "Veteran": data["meta"]["veteran"],
                data["meta"]["tag"]["value"]: data["meta"]["tag"]["value"]
            }

            ranks = [k for k,v in rankDict.items() if v]
            rank = "\n".join(ranks if ranks else ["Player"])

            statDict = {
                "Items identified": data["global"]["itemsIdentified"],
                "Mobs killed": data["global"]["mobsKilled"],
                "PvP kills": data["global"]["pvp"]["kills"],
                "PvP deaths": data["global"]["pvp"]["deaths"],
                "Chests found": data["global"]["chestsFound"],
                "Blocks walked": data["global"]["blocksWalked"],
                "Logins": data["global"]["logins"],
                "Deaths": data["global"]["deaths"],
                "Combal Level": data["global"]["totalLevel"]["combat"],
                "Total Level": data["global"]["totalLevel"]["combined"]
            }

            stats = [("**"+k+"**", str(v)) for k,v in statDict.items()]
            stats.sort(key=lambda x:int(x[-1]), reverse=True)

            classes = []
            for s in data["classes"]:
                classes.append("**" + "".join([i for i in s["name"].title()]) + ":** Level " + str(s["level"]))
            # Why is this a float? Did the api return floats before? Too scared to change
            classes.sort(key=lambda x:float(x.split(" ")[-1]))
            classes.reverse()

            skin = await self.getMinecraftSkinUrl(data["uuid"].replace("-", ""))
            if not skin:
                await ctx.send("Ratelimited! Custom player skin will not be shown.")
            try:
                skin["textures"]["SKIN"]["url"]
            except:
                await headRenderer("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png")
                headFile = discord.File("skins/head/Steve_skin.png", filename="head.png")
            else:
                await headRenderer(skin["textures"]["SKIN"]["url"])
                headFile = discord.File("skins/head/" + skin["textures"]["SKIN"]["url"].split("/")[-1] + ".png", filename="head.png")

            embed = discord.Embed(title="Wynncraft Player", colour=0x7bbf32)
            embed.set_author(name=data["username"],
                    icon_url="attachment://head.png")
            embed.add_field(name="Rank", value=rank)
            embed.add_field(name="Guild", value=str(data["guild"]["name"]))
            embed.add_field(name="Playtime", value=str(round(data["meta"]["playtime"]/12, 2))+"h")
            created = datetime.strptime(data["meta"]["firstJoin"], "%Y-%m-%dT%H:%M:%S.%fZ")
            last = datetime.strptime(data["meta"]["lastJoin"], "%Y-%m-%dT%H:%M:%S.%fZ")
            embed.add_field(name="First joined on", value="On " + created.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - created) + " ago")
            embed.add_field(name="Last joined on", value="On " + last.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - last) + " ago")
            if data["meta"]["location"]["online"]:
                embed.add_field(name="Currently online in", value=data["meta"]["location"]["server"])

            embed.add_field(name="Global stats", value="\n".join([x+": "+y for x,y in stats]))
            embed.add_field(name="Classes", value="\n".join(classes))

            embed.set_footer(text="\U00002063", icon_url="https://cdn.wynncraft.com/img/ico/android-icon-192x192.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(files=[headFile], embed=embed)
        else:
            data = await REST("https://api.wynncraft.com/public_api.php?action=onlinePlayersSum")
            embed = discord.Embed(title="Wynncraft", colour=0x7bbf32)
            embed.add_field(name="Players Online", value=data["players_online"])

            embed.set_footer(text="\U00002063", icon_url="https://cdn.wynncraft.com/img/ico/android-icon-192x192.png")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

    # ---
    # WEBSITES
    # ---

    @commands.command(name="mixer")
    async def MixerAPI(self, ctx, *, user):
        """Gets information about mixer users"""
        data = await REST("https://mixer.com/api/v1/channels/" + self.escape(user))

        name = data["token"]
        if data["user"]["username"].lower() != data["token"].lower():
            name = data["token"] + " (" + data["user"]["username"] + ")"

        s = " (Currently Streaming)" if data["online"] else ""
        embed = discord.Embed(title="Mixer user - " + name + s, color=0x002050, url="https://mixer.com/" + data["token"])

        if data["user"]["avatarUrl"]:
            embed.set_thumbnail(url=data["user"]["avatarUrl"])

        typeNames = {
            "Verified": data["user"]["verified"],
            "Suspended": data["suspended"],
            "Featured": data["featured"],
            "Partnered": data["partnered"],
            "Interactive Stream": data["interactive"],
            "VODs": data["vodsEnabled"]
        }
        types = [c for c in typeNames if typeNames[c]]
        groups = []

        try:
            for group in data["user"]["groups"]:
                groups.append(group["name"])
        except:
            pass

        if types:
            embed.add_field(name="Account type", value="\n".join(types))
        if groups:
            embed.add_field(name="Account groups", value="\n".join(groups))

        if data["user"]["bio"]:
            embed.add_field(name="Bio", value=str(data["user"]["bio"]))

        embed.add_field(name="Followers", value=str(data["numFollowers"]))
        embed.add_field(name="Sparks", value=str(data["user"]["sparks"]))

        try:
            if data["thumbnail"]["url"]:
                embed.set_image(url=data["thumbnail"]["url"])
        except:
            pass

        if data["online"]:
            embed.add_field(name="Current viewers", value=str(data["viewersCurrent"]))

        embed.set_footer(icon_url="https://mixer.com/_latest/assets/favicons/favicon-32x32.png", text="LVL " + str(data["user"]["level"]) + " • Account created ")
        embed.timestamp = datetime.strptime(data["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        await ctx.send(embed=embed)

    @commands.command(name="twitch")
    async def TwitchAPI(self, ctx, *, user):
        """Gets information about twitch users"""
        # TODO: Cache tokens
        token = await REST("https://id.twitch.tv/oauth2/token?client_id="+config.apiKeys["twitchID"]+"&client_secret="+config.apiKeys["twitchSecret"]+"&grant_type=client_credentials", method="s.post")
        token = token["access_token"]
        data = await REST("https://api.twitch.tv/helix/users?login=" + self.escape(user), headers={"Authorization": "Bearer " + token})
        data = data["data"][0]

        name = data["display_name"]
        if data["login"].lower() != data["display_name"].lower():
            name = data["display_name"] + " (" + data["login"] + ")"

        embed = discord.Embed(title="Twitch user - " + name, color=0x6441A4, url="https://twitch.tv/" + data["login"])

        embed.set_thumbnail(url=data["profile_image_url"])

        if data["offline_image_url"]:
            embed.set_image(url=data["offline_image_url"])

        if data["broadcaster_type"]:
            utype = data["broadcaster_type"].title()
            if data["type"]:
                utype += "\n" + data["type"].title()
            embed.add_field(name="User Type", value=utype)

        if data["description"]:
            embed.add_field(name="Description", value=data["description"])
        embed.add_field(name="Views", value=str(data["view_count"]))

        embed.set_footer(icon_url="https://static.twitchcdn.net/assets/favicon-32-d6025c14e900565d6177.png", text="User id " + data["id"])
        await ctx.send(embed=embed)


    @commands.command(name="imdb", aliases=["movie", "movies"])
    async def IMDbAPI(self, ctx, *, title):
        """Gets information about movies using the IMDb"""
        data = await REST("http://www.omdbapi.com/?apikey=" + config.apiKeys["omdb"] + "&t=" + self.escape(title))

        embed = discord.Embed(title=data["Title"] + " (" + data["Year"] + ")", colour=0xf5c518, url="https://www.imdb.com/title/" + data["imdbID"])
        embed.add_field(name="Released", value=data["Released"])
        if "Production" in data:
            embed.add_field(name="Produced by", value=data["Production"])
        if data["Runtime"] != "N/A":
            embed.add_field(name="Length", value=data["Runtime"])
        embed.add_field(name="Genre", value=data["Genre"])
        if "totalSeasons" in data and data["totalSeasons"] != "N/A":
            embed.add_field(name="Seasons", value=data["totalSeasons"])
        embed.add_field(name="Plot", value="||"+data["Plot"]+"||")
        if "Website" in data and data["Website"] != "N/A":
            embed.add_field(name="Website", value=data["Website"])
        if "Awards" in data and data["Awards"] != "N/A":
            embed.add_field(name="Awards", value=data["Awards"].replace(". ", ".\n"))
        if data["Poster"] != "N/A":
            embed.set_image(url=data["Poster"])

        if data["Ratings"]:
            ratings = ""
            for i in data["Ratings"]:
                ratings += "**" + i["Source"] + "** - `" + i["Value"] + "`\n"
            embed.add_field(name="Ratings", value=ratings)

        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


    @commands.is_nsfw()
    @commands.command(name="urbandictionary", aliases=["urban"])
    async def UrbanDictionaryAPI(self, ctx, *, term):
        """Gets information about the urban dictionary"""
        data = await REST("http://api.urbandictionary.com/v0/define?term=" + self.escape(term))
        data = data["list"][0]
        embed = discord.Embed(title=data["word"], colour=0x1d2439, url=data["permalink"])
        embed.add_field(name="Definition", value="```"+data["definition"].replace("\r","")+"```")
        embed.add_field(name="Example", value="```"+data["example"].replace("\r","")+"```")
        embed.set_footer(text=str(data["thumbs_up"])+"\N{THUMBS UP SIGN}, " + str(data["thumbs_down"]) + "\N{THUMBS DOWN SIGN} | Submitted")
        embed.timestamp = datetime.strptime(data["written_on"].split("T")[0], "%Y-%m-%d")
        await ctx.send(embed=embed)


    @commands.command(name="invite", aliases=["discord"])
    async def DiscordAPI(self, ctx, *, invite):
        """Gets information about discord invites"""
        invite = str(invite.split("/")[-1])
        data = await REST("https://discordapp.com/api/v6/invite/" +  self.escape(invite) + "?with_counts=true")
        try:
            data["guild"]
        except:
            raise commands.CommandError(message="%"+data["message"])

        embed = discord.Embed(title="Click here to join the server!", colour=0x7289DA, url="https://discord.gg/" + data["code"])
        embed.add_field(name="Guild Name", value=str(data["guild"]["name"]))
        if data["guild"]["description"]:
            embed.add_field(name="Description", value=str(data["guild"]["description"]))
        embed.add_field(name="Members", value=str(data["approximate_member_count"]))
        embed.add_field(name="Online", value=str(data["approximate_presence_count"]))


        flagName = {
            "VERIFIED": "Verified",
            "LURKABLE": "Lurking enabled",
            "INVITE_SPLASH": "Invite splash screen",
            "VIP_REGIONS": "VIP Server",
            "FEATURABLE": "Featured server",
            "DISCOVERABLE": "Discoverable",
            "NEWS": "News channel",
            "BANNER": "Custom banner",
            "VANITY_URL": "Vanity URL",
            "ANIMATED_ICON": "Animated icon",
            "COMMERCE": "Store",
            "MORE_EMOJI": "More emojis",
            "PUBLIC": "Public server",
            "PARTNERED": "Partnered",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen",
            "RELAY_ENABLED": "Sharded server",
            "ENABLED_DISCOVERABLE_BEFORE": "Discoverable (?)"
        }

        flags = data["guild"]["features"]

        if flags:
            embed.add_field(name="Special features", value="\n".join([flagName.get(n, n) for n in flags]))

        try:
            embed.add_field(name="Invite created by", value=str(data["inviter"]["username"]) + "#" + str(data["inviter"]["discriminator"]) + " (<@" + str(data["inviter"]["id"]) + ">)")
        except KeyError:
            pass

        if "BANNER" in flags and data["guild"]["banner"]:
            embed.set_image(url="https://cdn.discordapp.com/banners/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["banner"]) + ".webp?size=4096")
        elif "INVITE_SPLASH" in flags and data["guild"]["splash"]:
            embed.set_image(url="https://cdn.discordapp.com/splashes/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["splash"]) + ".webp?size=4096")

        if "ANIMATED_ICON" in flags and \
            data["guild"]["icon"] and \
            data["guild"]["icon"].startswith("a_"):
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["icon"] + ".gif?size=4096"))
        elif data["guild"]["icon"]:
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["icon"] + ".webp?size=4096"))

        embed.set_footer(text="Server ID " + str(data["guild"]["id"]))
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


    @commands.command(name="weather")
    async def WeatherAPI(self, ctx, *, city):
        """Gets information about the weather"""
        geocoding = await REST("https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=en&q=" + self.escape(city))
        data = await REST("https://api.darksky.net/forecast/" +  config.apiKeys["darksky"] + "/" + geocoding[0]["lat"] + "," + geocoding[0]["lon"] + "?exclude=minutely,hourly,daily,flags&units=si")

        try:
            if data["alerts"]:
                col = 0xff0000
            else:
                col = 0xffb347
        except:
            col = 0xffb347

        embed = discord.Embed(title=geocoding[0]["display_name"], color=col)
        embed.set_thumbnail(url="https://darksky.net/images/weather-icons/" + data["currently"]["icon"] + ".png")
        try:
            alerts = []
            for alert in data["alerts"]:
                if len(alerts) > 3:
                    continue
                if alert["title"] not in alerts:
                    embed.add_field(name=alert["title"], value=alert["description"][:1024])
                    alerts.append(alert["title"])
        except:
            pass
        embed.add_field(name="Weather", value=str(round(data["currently"]["temperature"], 2)) + "°C (" + str(round(data["currently"]["temperature"] * (9/5) + 32, 2)) + "°F)\n" \
            + data["currently"]["summary"] + "\n" \
            + "Feels Like: " + str(round(data["currently"]["apparentTemperature"], 2)) + "°C (" + str(round(data["currently"]["apparentTemperature"] * (9/5) + 32, 2)) + "°F)\n" \
            + "Humidity: " + str(round(data["currently"]["humidity"] * 100, 2)) + "%\n" \
            + "Clouds: " + str(round(data["currently"]["cloudCover"] * 100, 2)) + "%\n" \
            + "Wind: " + str(data["currently"]["windSpeed"]) + " m/s (" + str(round(int(data["currently"]["windSpeed"]) * 2.2369362920544, 2)) + " mph)")
        embed.set_footer(text="Powered by Dark Sky and OpenStreetMap")
        embed.timestamp = datetime.utcfromtimestamp(data["currently"]["time"])
        await ctx.send(embed=embed)


    @commands.command(name="twitter")
    async def TwitterAPI(self, ctx, *, user):
        """Gets information about twitter users."""
        twitter = TwitterClient(consumer_key=config.apiKeys["twitterConsKey"],
                                consumer_secret=config.apiKeys["twitterConsSecret"],
                                oauth_token=config.apiKeys["twitterAccToken"],
                                oauth_token_secret=config.apiKeys["twitterAccSecret"])
        data = await twitter.request("GET", "users/search.json", params={"count": 1, "q": self.escape(user)})
        data = data[0]
        embed = discord.Embed(title=f'{data["name"]} (@{data["screen_name"]})', url="https://twitter.com/"+data["screen_name"], description=data["description"], color=0x1DA1F2)
        embed.set_thumbnail(url=data["profile_image_url_https"])
        embed.add_field(name="Tweets", value=str(data["statuses_count"]))
        embed.add_field(name="Followers", value=str(data["followers_count"]))
        embed.add_field(name="Following", value=str(data["friends_count"]))
        embed.add_field(name="Liked posts", value=str(data["favourites_count"]))
        if data["location"]:
            embed.add_field(name="Location", value=data["location"])
        extra = []
        if data["verified"]:
            extra.append("Verified")
        if data["protected"]:
            extra.append("Private")
        if extra:
            embed.add_field(name="+", value="\n".join(extra))
        embed.set_footer(icon_url="https://about.twitter.com/etc/designs/about-twitter/public/img/favicon-32x32.png", text="Twitter • Account created")
        embed.timestamp = datetime.strptime(data["created_at"], "%a %b %d %H:%M:%S %z %Y")
        await ctx.send(embed=embed)

    @commands.command(name="status", aliases=["statuspage"])
    async def StatusAPI(self, ctx, *, name="None"):
        """Gets information about status pages."""
        for page in config.statusPages:
            if name.lower() == page[0]:
                col = 0x00
                j = await REST(page[1] + "/index.json")
                if j["status"]["indicator"] == "none":
                    col = 0x00ff00
                elif j["status"]["indicator"] == "minor":
                    col = 0xffa500
                elif j["status"]["indicator"] == "major":
                    col = 0xff0000

                embed = discord.Embed(title="**" + page[0].title() + " Status** - " + j["status"]["description"], colour=col, url=page[1])
                for comp in j["components"]:
                    embed.add_field(name=comp["name"], value=comp["status"].replace("_", " ").title())
                if page[2]:
                    # Seperate component and metric statuses by using an invisible field
                    embed.add_field(inline=False, name="\U00002063", value="\U00002063")
                    for metric in page[2]:
                        m = await REST(page[1] + "/metrics-display/" + metric + "/day.json")
                        last = m["summary"]["last"]
                        last = str(round(last, 2)) if last else "0"
                        embed.add_field(name=m["metrics"][0]["metric"]["name"], value=last)
                embed.timestamp = datetime.utcnow()

                await ctx.send(embed=embed)

                for incident in j["incidents"]:
                    if incident["status"] == "resolved" or incident["status"] == "completed":
                        continue
                    firstUpdate = incident["incident_updates"][-1]
                    lastUpdate = incident["incident_updates"][0]
                    if incident["status"] == "scheduled":
                        col = 0xffa500
                    else:
                        col = 0xff0000

                    embed = discord.Embed(title="**" + incident["status"].title() + "** - " + incident["name"], color=col)
                    if firstUpdate["affected_components"]:
                        embed.add_field(name="Affected components", value="\n".join(c["name"] for c in firstUpdate["affected_components"]))
                    if firstUpdate != lastUpdate and len(firstUpdate) + len(lastUpdate) + 5 < 1900:
                        embed.description = "**" + datetime.fromisoformat(lastUpdate["created_at"].rstrip("Z")).strftime("%b %d %H:%M:%S %Y UTC%z") \
                                          + "**: " + lastUpdate["body"] + "\n\n\n**" \
                                          + datetime.fromisoformat(firstUpdate["created_at"].rstrip("Z")).strftime("%b %d %H:%M:%S %Y UTC%z") \
                                          + "**: " + firstUpdate["body"]
                    else:
                        embed.description = firstUpdate["body"]

                    if incident["scheduled_for"]:
                        embed.timestamp = datetime.fromisoformat(incident["scheduled_for"].rstrip("Z"))
                        embed.set_footer(text=incident["impact"].title() + " • Starts")
                    else:
                        embed.timestamp = datetime.fromisoformat(incident["created_at"].rstrip("Z"))
                        embed.set_footer(text=incident["impact"].title() + " • Started")

                    await ctx.send(embed=embed)
                return

        raise commands.CommandError(message="%Invalid page! Currently supported pages: ```\n" + "\n".join([n.title() for n,u,c in config.statusPages]) + "```")

    @commands.command(name="screenshot")
    async def screenshot(self, ctx, *, url, size="1920x1080"):
        if not url.startswith("http"):
            url = "http://" + url
        # Download file to website.png
        async with aiohttp.ClientSession() as s:
            async with s.get("http://api.screenshotlayer.com/api/capture?viewport=" + size + "&access_key=" + config.apiKeys["screenshotlayer"] + "&url=" + url) as r:
                with open("website.png", "wb") as f:
                    f.write(await r.read())
        shot = discord.File("website.png", filename="website.png")
        await ctx.send(files=[shot])

    @commands.command(name="wolframalpha", aliases=["wa", "wolfram"])
    async def wolframalpha(self, ctx, *, query):
        # Discord can't download the file so we do it ourselves
        async with aiohttp.ClientSession() as s:
            async with s.get(f"http://api.wolframalpha.com/v1/simple?appid={config.apiKeys['wolframalpha']}&layout=labelbar&background=2F3136&foreground=white&i={self.escape(query)}") as r:
                data = await r.read()
                if len(data) < 1000: # HACK: Probably error msg if response is under 1000 bytes
                    await ctx.send(f"{ctx.author.mention} " + data.decode("utf-8"))
                    return
                with open("wolfram.png", "wb") as f:
                    f.write(await r.read())
        answer = discord.File("wolfram.png", filename="wolfram.png")
        await ctx.send(files=[answer])

    # The wiki has to have the TextExtracts extension in order for the API to work.
    # TODO: Don't rely on TextExtracts by stripping html manually (?)

    @commands.command(name="wiki", aliases=["wikipedia"])
    async def wiki(self, ctx, *, query):
        await self.mediawiki(ctx, query, "https://en.wikipedia.org/w/api.php", "Wikipedia")

    @commands.command(name="wiktionary", aliases=["dictionary", "define"])
    async def wiktionary(self, ctx, *, query):
        await self.mediawiki(ctx, query, "https://en.wiktionary.org/w/api.php", "Wiktionary")

    @commands.command(name="wikilanguage", aliases=["wikil", "wikilang"])
    async def wikilanguage(self, ctx, lang, *, query):
        await self.mediawiki(ctx, query, "https://"+lang+".wikipedia.org/w/api.php", "Wikipedia " + lang.upper())

    @commands.command(name="wiktionarylanguage", aliases=["wiktionarylang", "dictionarylanguage", "dictionarylang", "definelang", "definelanguage"])
    async def wiktionarylanguage(self, ctx, lang, *, query):
        await self.mediawiki(ctx, query, "https://"+lang+".wiktionary.org/w/api.php", "Wiktionary " + lang.upper())

    @commands.command(name="gamepedia")
    async def gamepedia(self, ctx, wiki, *, query):
        await self.mediawiki(ctx, query, "https://"+wiki+".gamepedia.com/api.php", wiki.title() + " Wiki")

    @commands.command(name="mcwiki", aliases=["minecraftwiki"])
    async def mcwiki(self, ctx, *, query):
        await self.mediawiki(ctx, query, "https://minecraft.gamepedia.com/api.php", "Minecraf Wiki")

    # TODO: Bulbapedia doesn't return pageIDs in searches
    """@commands.command(name="pokémon", aliases=["pokemon", "bulbapedia"])
    async def bulbapedia(self, ctx, *, query):
        await self.mediawiki(ctx, query, "https://bulbapedia.bulbagarden.net/w/api.php", "Bulbapedia")"""

    # Enable this if fandom ever decides to update their MediaWiki installation. Fandom's version (1.19.24) was last updated March 31st, 2015.
    # Fandom also disabled searching API so :shrug:
    """@commands.command(name="fandom")
    async def fandom(self, ctx, wiki, *, query):
        await self.mediawiki(ctx, query, "https://"+wiki+".fandom.com/api.php", wiki.title() + " Wiki")"""

def setup(bot):
    bot.add_cog(APIs(bot))
