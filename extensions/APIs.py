import discord
from discord.ext import commands
import config
import requests
from datetime import datetime
import base64
import json
import math
import urllib.parse
import BotUtils
from requests_oauthlib import OAuth1
import dateutil

class APIs(commands.Cog):
    """APIs"""

    def __init__(self, bot):
        self.bot = bot

    # ---
    # FUNCTIONS
    # ---

    def REST(self, url, method=requests.get, headers={}, data={}, auth=None, returns="r.json()"):
        r = method(url=url, headers=headers, data=data, auth=auth)
        try:
            return eval(returns)
        except:
            return None     

    def escape(self, url):
        return urllib.parse.quote(url)

    # thanks stackoverflow love ya
    def td_format(self, td_object):
        seconds = int(td_object.total_seconds())
        periods = [
            ("year",        60*60*24*365),
            ("month",       60*60*24*30),
            ("day",         60*60*24),
            ("hour",        60*60),
            ("minute",      60)
        ]

        strings=[]
        for period_name, period_seconds in periods:
            if seconds > period_seconds:
                period_value , seconds = divmod(seconds, period_seconds)
                has_s = "s" if period_value > 1 else ""
                strings.append("%s %s%s" % (period_value, period_name, has_s))

        return ", ".join(strings)

    
    async def getMinecraftAge(self, name):
        a = 1263146630 # notch sign-up
        b = math.floor(datetime.utcnow().timestamp())
        lastfail = 0
        for i in range(30):
            if a == b:
                ok = self.REST("https://api.mojang.com/users/profiles/minecraft/" + name + "?at=" + str(a), returns="r.status_code == 200")
                if ok and lastfail == a-1:
                    return datetime.utcfromtimestamp(a)
                else:
                    return False
            else:
                mid = a + math.floor((b - a) / 2)
                ok = self.REST("https://api.mojang.com/users/profiles/minecraft/" + name + "?at=" + str(mid), returns="r.status_code == 200")
                if ok:
                    b = mid
                else:
                    a = mid+1
                    lastfail = mid

    
    async def getMinecraftUUID(self, name):
        r = self.REST("https://api.mojang.com/users/profiles/minecraft/" + name)
        if r:
            return r
        
        r = self.REST("https://api.mojang.com/users/profiles/minecraft/" + name + "?at=0")
        if r:
            return r
        return None
    
    async def getMinecraftSkinUrl(self, uuid):
        data = self.REST("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid)
        try:
            val = data["properties"][0]["value"]
        except:
            return None
        decoded = base64.b64decode(val)
        return(json.loads(decoded))

    def getCSStat(self, data, stat):
        return [i for i in data["stats"] if i["name"] == "stat"]

    
    # ---
    # GAMES
    # ---

    @commands.command(name="minecraft", aliases=["mc"])
    async def minecraftAPI(self, ctx, *, user=None):
        """Gets information about Minecraft, or searches players.
        Leave user as blank for general statistics"""
        if user:
            uuid = await self.getMinecraftUUID(user)
            if not uuid:
                await ctx.send("User not found!")
                await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
                return
            await ctx.message.add_reaction("\N{HOURGLASS}")
            history = self.REST("https://api.mojang.com/user/profiles/" + uuid["id"] + "/names")
            names = []
            for i in range(len(history)):
                names.append(history[i]["name"])
                names[i] = names[i].replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
            names.reverse()
            names[0] += " **[CURRENT]**"
            created = await self.getMinecraftAge(user)
            skin = await self.getMinecraftSkinUrl(uuid["id"])
            if not skin:
                await ctx.send("Ratelimited! Try again in 10 seconds")
            embed = discord.Embed(title="Minecraft User", colour=0x82540f)
            embed.set_author(name=history[-1]["name"], icon_url="attachment://head.png")
            embed.add_field(name="Name history", value="\n".join(names))
            embed.add_field(name="UUID", value=uuid["id"])
            try:
                skin["textures"]["SKIN"]["url"]
            except:
                # TODO: Try to find a official steve skin in mojang's skin server
                await BotUtils.skinRenderer2D("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png", "default")
                await BotUtils.headRenderer("https://gamepedia.cursecdn.com/minecraft_gamepedia/3/37/Steve_skin.png", "default")
                skin = discord.File("skins/2d/default.png", filename="skin.png")
                head = discord.File("skins/head/default.png", filename="head.png")
            else:
                embed.add_field(name="Skin URL", value="[Click me]("+skin["textures"]["SKIN"]["url"]+")")
                await BotUtils.skinRenderer2D(skin["textures"]["SKIN"]["url"], str(uuid["id"]))
                await BotUtils.headRenderer(skin["textures"]["SKIN"]["url"], str(uuid["id"]))
                skin = discord.File("skins/2d/" + str(uuid["id"]) + ".png", filename="skin.png")
                head = discord.File("skins/head/" + str(uuid["id"]) + ".png", filename="head.png")

            if created:
                embed.add_field(name="Account created", value="On " + created.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - created) + " ago")
            else:
                embed.add_field(name="Account created", value="???")
            embed.set_footer(text="|", icon_url="https://minecraft.net/favicon-96x96.png")
            embed.set_image(url="attachment://skin.png")
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(files=[skin, head], embed=embed)
        else:
            sale = self.REST("https://api.mojang.com/orders/statistics", method=requests.post, data='{"metricKeys":["item_sold_minecraft","prepaid_card_redeemed_minecraft"]}')
            embed = discord.Embed(title="Minecraft", colour=0x82540f)
            embed.add_field(name="Sold total", value=sale["total"])
            embed.add_field(name="Sold in the last 24h", value=sale["last24h"])
            embed.set_footer(text="|", icon_url="https://minecraft.net/favicon-96x96.png")
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed)

    # TODO: FIX for APIv2
    @commands.command(name="apex", aliases=["apexlegends", "apesex"])
    async def apexAPI(self, ctx, user, platform="origin"):
        """Gets information about Apex Legends players.
           Only PC information for now."""
        if platform != "origin" and platform != "xbl" and platform != "psn":
            await ctx.send("Possible platform: origin, xbl, psn")
            return
        await ctx.message.add_reaction("\N{HOURGLASS}")
        data = self.REST("https://public-api.tracker.gg/v2/apex/standard/profile/" + platform + "/" + user, headers={"TRN-Api-Key":config.api_keys["tracker"]})
        stats = []
        for stat in data["data"]["segments"]:
            print(stat)
            # TODO
            for value in stat["stats"]["metadata"]["name"] :
                print(value)
                val = str(value["value"])
                print(val)
                stats.append((stat["metadata"]["name"] +" - " + value["displayName"], val.rstrip("0").rstrip(".") if "." in val else val))
        embed = discord.Embed(title="Apex Legends", colour=0xff6666)
        embed.set_author(name=str(data["data"]["platformInfo"]["platformUserHandle"]) + " - Level " + str(data["data"]["segments"][0]["stats"]["level"]["value"]))
        for stat in stats:
            embed.add_field(name=stat[0], value=stat[1])
        embed.set_footer(text="Missing data because EA.", icon_url="https://logodownload.org/wp-content/uploads/2019/02/apex-legends-logo-1.png")
        embed.timestamp = datetime.utcnow()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)


    @commands.command(name="csgo", aliases=["cs"])
    async def CSGOAPI(self, ctx, *, user=None):
        """Gets information about CSGO players."""
        if not user:
            await ctx.send("Please enter an steam id or custom url after the command.")
            return
        await ctx.message.add_reaction("\N{HOURGLASS}")
        if not str(user).isdigit():
            data = self.REST("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + config.api_keys["steam"] + "&vanityurl=" + self.escape(user))
            user = data["response"]["steamid"]
        data = self.REST("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + config.api_keys["steam"] + "&steamids=" + user)
        name = data["response"]["players"][0]["personaname"]
        data = self.REST("http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=" + config.api_keys["steam"] + "&steamid=" + user)
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
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)


    @commands.command(name="osu")
    async def OsuAPI(self, ctx, *, user):
        """Gets information about osu! players."""
        data = self.REST("https://osu.ppy.sh/api/get_user?u=" + self.escape(user) + "&k=" + config.api_keys["osu"])[0]
        embed = discord.Embed(title="osu! - " + data["username"], color=0xEA68A3)
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
        embed.set_footer(text="Account created", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Osu%21Logo_%282015%29.svg/480px-Osu%21Logo_%282015%29.svg.png")
        embed.timestamp = datetime.strptime(data["join_date"], "%Y-%m-%d %H:%M:%S")
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)

    
    @commands.command(name="classicube", aliases=["cc"])
    async def classiCubeAPI(self, ctx, *, user=None):
        """Gets information about ClassiCube, or searches players.
        user = ID or name
        Leave as blank for general statistics"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        if user:
            data = self.REST("https://www.classicube.net/api/player/"+self.escape(user))
            if not data or data["error"] != "":
                if user.isdigit():
                    data = self.REST("https://www.classicube.net/api/id/"+self.escape(user))
                if not data or data["error"] != "":
                    await ctx.message.clear_reactions()
                    await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
                    await ctx.send("User not found!")
                    return

            flags = []
            if "b" in data["flags"]:
                flags.append("Banned from forums")
            if "d" in data["flags"]:
                flags.append("Developer")
            if "m" in data["flags"]:
                flags.append("Forum moderator")
            if "a" in data["flags"]:
                flags.append("Forum admin")
            if "e" in data["flags"]:
                flags.append("Blog editor")
            if "p" in data["flags"]:
                flags.append("Patreon")
            if "u" in data["flags"]:
                flags.append("Unverified")
            if "r" in data["flags"]:
                flags.append("Recovering account")
            
            embed = discord.Embed(title="ClassiCube User", colour=0x977dab)
            embed.set_author(name=data["username"],
                icon_url="attachment://head.png")
            embed.add_field(name="ID", value=data["id"])
            ago = self.td_format(datetime.utcnow() - datetime.utcfromtimestamp(data["registered"]))
            if len(ago) == 0:
                ago = "Under a minute"
            embed.add_field(name="Account created", value="On " + datetime.utcfromtimestamp(data["registered"]).strftime("%c") + "\n" + ago + " ago")
            if flags:
                embed.add_field(name="Notes", value=", ".join(flags))
            
            if self.REST("https://static.classicube.net/skins/" + str(data["username"]) + ".png", returns="r.status_code == 200"):
                embed.add_field(name="Skin URL", value="[Click me](https://static.classicube.net/skins/" + str(data["username"]) + ".png)")
                await BotUtils.skinRenderer2D("https://static.classicube.net/skins/" + str(data["username"]) + ".png", str(data["id"]))
                await BotUtils.headRenderer("https://static.classicube.net/skins/" + str(data["username"]) + ".png", str(data["id"]))
                file = discord.File("skins/2d/" + str(data["id"]) + ".png", filename="skin.png")
                file2 = discord.File("skins/head/" + str(data["id"]) + ".png", filename="head.png")
            else:
                file = discord.File("skins/2d/default.png", filename="skin.png")
                file2 = discord.File("skins/head/default.png", filename="head.png")

            embed.set_footer(text="|", icon_url="https://www.classicube.net/static/img/cc-cube-small.png")
            embed.set_image(url="attachment://skin.png")
            embed.timestamp = datetime.utcnow()

            await ctx.message.clear_reactions()
            await ctx.send(files=[file, file2], embed=embed)
        else:
            data = self.REST("https://www.classicube.net/api/players/")
            onlinecount = 0
            playercount = data["playercount"]
            players = ""
            for p in data["lastfive"]:
                players += str(p) + "\n"
            
            data = self.REST("https://www.classicube.net/api/servers/")
            serverlist = []
            servers = ""
            for server in sorted(data["servers"], key=lambda k: k["players"], reverse=True):
                if server["players"] > 0:
                    temp = "[" + str(server["country_abbr"]) + "] [" + str(server["name"]) + "](https://www.classicube.net/server/play/" + str(server["hash"]) + ") | " + str(server["players"]) + "/" + str(server["maxplayers"])
                    onlinecount += server["players"]
                    if len(servers) + len("\n---\n") + len(temp) > 1024:
                        serverlist.append(servers)
                        servers = ""
                    servers += temp+"\n---\n"
            serverlist.append(servers)

            embed = discord.Embed(title="ClassiCube", colour=0x977dab)
            embed.add_field(name="Total Accounts", value=playercount)
            embed.add_field(name="Accounts Online\n(Inaccurate)", value=str(onlinecount))
            embed.add_field(name="Last five accounts", value=players)
            for i in range(len(serverlist)):
                embed.add_field(name="("+str(i+1)+"/"+str(len(serverlist))+") Servers with players\nClick the server names to join!", value=serverlist[i])

            embed.set_footer(text="|", icon_url="https://www.classicube.net/static/img/cc-cube-small.png")
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed)

    
    @commands.command(name="wynncraft", aliases=["wc", "wynn"])
    async def WynncraftAPI(self, ctx, *, user=None):
        """Gets information about Wynncraft, or searches players.
        Leave as blank for general statistics"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        if user:
            data = self.REST("https://api.wynncraft.com/v2/player/"+self.escape(user)+"/stats")
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
            stats.sort(key=lambda x:int(x.split(" ")[-1]))
            stats.reverse()

            classes = []
            for s in data["classes"]:
                classes.append("**" + "".join([i for i in s["name"].title() if not i.isdigit()]) + ":** Level " + str(round(s["level"])))
            classes.sort(key=lambda x:float(x.split(" ")[-1]))
            classes.reverse()

            embed = discord.Embed(title="Wynncraft Player", colour=0x7bbf32)
            embed.set_author(name=data["username"],
                    icon_url="https://crafatar.com/avatars/"+data["uuid"])
            embed.add_field(name="Rank", value=rank)
            embed.add_field(name="Guild", value=str(data["guild"]["name"]))
            embed.add_field(name="Playtime", value=str(round(data["meta"]["playtime"]/12, 2))+"h")
            embed.add_field(name="First joined on", value=data["meta"]["firstJoin"].replace("T", ", ").split(".")[0])
            embed.add_field(name="Last joined on", value=data["meta"]["lastJoin"].replace("T", ", ").split(".")[0])
            if data["meta"]["location"]["online"]:
                embed.add_field(name="Currently in", value=data["meta"]["location"]["server"])
            
            embed.add_field(name="Global stats", value="\n".join(stats))
            embed.add_field(name="Classes", value="\n".join(classes))
            
            embed.set_footer(text="|", icon_url="https://cdn.wynncraft.com/img/ico/android-icon-192x192.png")
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed)
            return
        else:
            data = self.REST("https://api.wynncraft.com/public_api.php?action=onlinePlayersSum")
            embed = discord.Embed(title="Wynncraft", colour=0x7bbf32)
            embed.add_field(name="Players Online", value=data["players_online"])

            embed.set_footer(text="|", icon_url="https://cdn.wynncraft.com/img/ico/android-icon-192x192.png")
            embed.timestamp = datetime.utcnow()
            await ctx.message.clear_reactions()
            await ctx.send(embed=embed)

    # ---
    # WEBSITES
    # ---

    @commands.command(name="mixer")
    async def MixerAPI(self, ctx, *, user):
        """Gets information about mixer users"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        data = self.REST("https://mixer.com/api/v1/channels/" + self.escape(user))
        
        name = data["token"]
        if data["user"]["username"].lower() != data["token"].lower():
            name = data["token"] + " (" + data["user"]["username"] + ")"

        s = ""
        if data["online"]:
            s = " (Currently Streaming)"

        embed = discord.Embed(title="Mixer user - " + name + s, color=0x002050, url="https://mixer.com/" + data["token"])

        if data["user"]["avatarUrl"]:
            embed.set_thumbnail(url=data["user"]["avatarUrl"])
        

        types = []
        groups = []
        if data["user"]["verified"]:
            types.append("Verified")
        if data["suspended"]:
            types.append("Suspended")
        if data["featured"]:
            types.append("Featured")
        if data["partnered"]:
            types.append("Partnered")
        if data["interactive"]:
            types.append("Interactive Stream")
        if data["vodsEnabled"]:
            types.append("VODs")
        
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

        embed.set_footer(icon_url="http://teambeyond.net/wp-content/uploads/2017/05/Mixer-Logo.png", text="LVL " + str(data["user"]["level"]) + " • Account created ")
        embed.timestamp = datetime.strptime(data["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)

    @commands.command(name="twitch")
    async def TwitchAPI(self, ctx, *, user):
        """Gets information about twitch users"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        token = self.REST("https://id.twitch.tv/oauth2/token?client_id="+config.api_keys["twitchID"]+"&client_secret="+config.api_keys["twitchSecret"]+"&grant_type=client_credentials", method=requests.post)["access_token"]
        data = self.REST("https://api.twitch.tv/helix/users?login=" + self.escape(user), headers={"Authorization": "Bearer " + token})["data"][0]

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
        embed.add_field(name="Viewers", value=str(data["view_count"]))

        embed.set_footer(icon_url="https://www.stickpng.com/assets/images/580b57fcd9996e24bc43c540.png", text="User id " + data["id"])
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)


    @commands.command(name="imdb", aliases=["movie", "movies"])
    async def IMDbAPI(self, ctx, *, title):
        """Gets information about movies using the IMDb"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        data = self.REST("http://www.omdbapi.com/?apikey=" + config.api_keys["omdb"] + "&t=" + self.escape(title))
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
        await ctx.send(embed=embed)


    @commands.command(name="urbandictionary", aliases=["urban", "define"])
    async def UrbanDictionaryAPI(self, ctx, *, term):
        """Gets information about the urban dictionary"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        data = self.REST("http://api.urbandictionary.com/v0/define?term=" + self.escape(term))
        data = data["list"][0]
        embed = discord.Embed(title=data["word"], colour=0x1d2439, url=data["permalink"])
        embed.add_field(name="Definition", value="```"+data["definition"].replace("\r","")+"```")
        embed.add_field(name="Example", value="```"+data["example"].replace("\r","")+"```")
        embed.set_footer(text=str(data["thumbs_up"])+"\N{THUMBS UP SIGN}, " + str(data["thumbs_down"]) + "\N{THUMBS DOWN SIGN} | Submitted")
        embed.timestamp = datetime.strptime(data["written_on"].split("T")[0], "%Y-%m-%d")
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)


    @commands.command(name="invite", aliases=["discord"])
    async def DiscordAPI(self, ctx, *, invite):
        """Gets information about discord invites"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        invite = str(invite.split("/")[-1])
        data = self.REST("https://discordapp.com/api/v6/invite/" +  self.escape(invite) + "?with_counts=true")
        
        try:
            data["guild"]
        except:
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
            await ctx.send(data["message"])
            return

        embed = discord.Embed(title="Click here to join the server!", colour=0x7289DA, url="https://discord.gg/" + data["code"])
        embed.add_field(name="Guild Name", value=str(data["guild"]["name"]))
        if data["guild"]["description"]:
            embed.add_field(name="Description", value=str(data["guild"]["description"]))
        embed.add_field(name="Members", value=str(data["approximate_member_count"]))
        embed.add_field(name="Online", value=str(data["approximate_presence_count"]))
        

        flagName = {
            "VERIFIED": "Verified",
            "LURKABLE": "Lurking enabled",
            "INVITE_SPLASH": "Custom invite splash screen",
            "VIP_REGIONS": "VIP Server",
            "FEATURABLE": "Featured server",
            "DISCOVERABLE": "In server discoveries",
            "NEWS": "News channel",
            "BANNER": "Custom banner",
            "VANITY_URL": "Custom vanity url",
            "ANIMATED_ICON": "Animated icon",
            "COMMERCE": "Store",
            "MORE_EMOJI": "More emoji"
        }

        flags = data["guild"]["features"]

        if flags:
            embed.add_field(name="Special features", value="\n".join([flagName[n] for n in flags]))
        
        try:
            embed.add_field(name="Invite created by", value=str(data["inviter"]["username"]) + "#" + str(data["inviter"]["discriminator"]) + " (<@" + str(data["inviter"]["id"]) + ">)")
        except KeyError:
            pass

        if "BANNER" in flags and data["guild"]["banner"]:
            embed.set_image(url="https://cdn.discordapp.com/banners/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["banner"]) + ".webp?size=4096")
       
        if "ANIMATED_ICON" in flags and \
            data["guild"]["icon"] and \
            data["guild"]["icon"].startswith("a_"):
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["icon"] + ".gif?size=4096"))
        elif data["guild"]["icon"]:
            embed.set_thumbnail(url="https://cdn.discordapp.com/icons/" + str(data["guild"]["id"]) + "/" + str(data["guild"]["icon"] + ".webp?size=4096"))
        
        embed.set_footer(text="Server ID " + str(data["guild"]["id"]))
        embed.timestamp = datetime.utcnow()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)


    @commands.command(name="weather", aliases=["sää"])
    async def WeatherAPI(self, ctx, *, city):
        """Gets information about the weather"""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        geocoding = self.REST("https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=en&q=" + self.escape(city))
        data = self.REST("https://api.darksky.net/forecast/" +  config.api_keys["darksky"] + "/" + geocoding[0]["lat"] + "," + geocoding[0]["lon"] + "?exclude=minutely,hourly,daily,flags&units=si")
        
        embed = discord.Embed(title=geocoding[0]["display_name"], colour=0xffb347)
        embed.set_thumbnail(url="https://darksky.net/images/weather-icons/" + data["currently"]["icon"] + ".png")
        suffix = ""
        try:
            data["alerts"]
            hasAlerts = True
        except:
            hasAlerts = False
        if hasAlerts:
            suffix = "\n\n---"
        embed.add_field(name="Weather", value=str(round(data["currently"]["temperature"], 2)) + "°C (" + str(round(data["currently"]["temperature"] * (9/5) + 32, 2)) + "°F)\n" \
            + data["currently"]["summary"] + "\n" \
            + "Feels Like: " + str(round(data["currently"]["apparentTemperature"], 2)) + "°C (" + str(round(data["currently"]["apparentTemperature"] * (9/5) + 32, 2)) + "°F)\n" \
            + "Humidity: " + str(round(data["currently"]["humidity"] * 100, 2)) + "%\n" \
            + "Clouds: " + str(round(data["currently"]["cloudCover"] * 100, 2)) + "%\n" \
            + "Wind: " + str(data["currently"]["windSpeed"]) + " m/s (" + str(round(int(data["currently"]["windSpeed"]) * 2.2369362920544, 2)) + " mph)" + suffix)
        if hasAlerts:
            alerts = []
            for alert in data["alerts"]:
                if len(alerts) > 23:
                    continue
                if alert["title"] not in alerts:
                    embed.add_field(name=alert["title"], value=alert["description"][:1024])
                    alerts.append(alert["title"])
        embed.set_footer(text="Powered by Dark Sky and OpenStreetMap")
        embed.timestamp = datetime.utcfromtimestamp(data["currently"]["time"])
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)

    
    @commands.command(name="twitter")
    async def TwitterAPI(self, ctx, *, user):
        """Gets information about twitter users."""
        auth = OAuth1(config.api_keys["twitterConsKey"], config.api_keys["twitterConsSecret"], config.api_keys["twitterAccToken"], config.api_keys["twitterAccSecret"])
        data = self.REST("https://api.twitter.com/1.1/users/search.json?count=1&q=" + self.escape(user), auth=auth)[0]
        embed = discord.Embed(title=data["name"] + " (@" + data["screen_name"] + ")", url="https://twitter.com/"+data["screen_name"], description=data["description"], color=0x1DA1F2)
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


    @commands.command(name="user", aliases=["käyttäjä"])
    async def discordUser(self, ctx, *, user):
        """Gets information about discord users."""
        await ctx.message.add_reaction("\N{HOURGLASS}")
        user = await commands.UserConverter().convert(ctx, user)
        embed = discord.Embed(title="Discord User " + user.name + "#" + str(user.discriminator), colour=0x7289DA)
        embed.set_thumbnail(url=str(user.avatar_url))
        embed.add_field(name="Account created", value="On " + user.created_at.strftime("%c") + "\n" + self.td_format(datetime.utcnow() - user.created_at) + " ago")
        embed.set_footer(text="User ID" + str(user.id))
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)


    @commands.command(name="status", aliases=["statuspage"])
    async def StatusAPI(self, ctx, *, name="None"):
        """Gets information about status pages."""
        pages = [
            ("discord", "https://status.discordapp.com"),
            ("twitter", "https://api.twitterstat.us"),
            ("reddit", "https://reddit.statuspage.io"),
            ("cloudflare", "https://www.cloudflarestatus.com"),
            ("dropbox", "https://status.dropbox.com"),
            ("github", "https://www.githubstatus.com"),
            ("medium", "https://medium.statuspage.io"),
            ("epicgames", "https://status.epicgames.com")
        ]
        await ctx.message.add_reaction("\N{HOURGLASS}")
        for page in pages:
            if name.lower() == page[0]:
                col = 0x00
                j = self.REST(page[1] + "/index.json")
                if j["status"]["indicator"] == "none":
                    col = 0x00ff00
                elif j["status"]["indicator"] == "minor":
                    col = 0xffa500
                elif j["status"]["indicator"] == "major":
                    col = 0xff0000

                embed = discord.Embed(title="**" + page[0].title() + " Status** - " + j["status"]["description"], colour=col, url=page[1])
                for comp in j["components"]:
                    embed.add_field(name=comp["name"], value=comp["status"].replace("_", " ").title())
                embed.timestamp = datetime.utcnow()
                
                await ctx.message.clear_reactions()
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
                        embed.description = "**" + dateutil.parser.parse(lastUpdate["created_at"]).strftime("%b %d %H:%M:%S %Y UTC%z") \
                                          + "**: " + lastUpdate["body"] + "\n\n\n**" \
                                          + dateutil.parser.parse(firstUpdate["created_at"]).strftime("%b %d %H:%M:%S %Y UTC%z") \
                                          + "**: " + firstUpdate["body"]
                    else:
                        embed.description = firstUpdate["body"]

                    if incident["scheduled_for"]:
                        embed.timestamp = dateutil.parser.parse(incident["scheduled_for"])
                        embed.set_footer(text=incident["impact"].title() + " • Starts")
                    else:
                        embed.timestamp = dateutil.parser.parse(incident["created_at"])
                        embed.set_footer(text=incident["impact"].title() + " • Started")

                    await ctx.send(embed=embed)
                return

        await ctx.message.clear_reactions()
        await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
        await ctx.send("Invalid page! Currently supported pages: ```\n" + "\n".join([n.title() for n, a in pages]) + "```")

def setup(bot):
    bot.add_cog(APIs(bot))
